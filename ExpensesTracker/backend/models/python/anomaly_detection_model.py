import json

import pandas as pd
import numpy as np
import pickle
import warnings
import os
warnings.filterwarnings('ignore')

from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from models.db.dbconfig import get_engine,read_data, write_data, DB_AVAILABLE,CSV_DIR, get_user_accounts

VELOCITY_FEATURES = [
    'vel_1d', 'vel_7d', 'vel_30d', 'count_30d', 'accounts.COUNT(transactions)',
]
AMOUNT_FEATURES = [
    'avg_amt_30d',
    'accounts.MEAN(monthly_stats.total_spend)',
    'accounts.MAX(monthly_stats.total_spend)',
    'accounts.SUM(monthly_stats.total_spend)',
    'accounts.balances_current',
]
RECENCY_FEATURES = [
    'days_since_last', 'accounts.TIME_SINCE_LAST(transactions.date)',
]
MERCHANT_FEATURES = ['merchant_diversity', 'new_merchant_count']

ALL_ANOMALY_FEATURES = VELOCITY_FEATURES + AMOUNT_FEATURES + RECENCY_FEATURES + MERCHANT_FEATURES

FEATURE_LABELS = {
    'vel_1d': 'Transactions today',
    'vel_7d': 'Transactions this week',
    'vel_30d': 'Transactions this month',
    'count_30d': 'Transaction count (30d)',
    'accounts.COUNT(transactions)': 'Total transactions ever',
    'avg_amt_30d': 'Avg transaction amount (30d)',
    'accounts.MEAN(transactions.amount)': 'All-time avg transaction amount',
    'accounts.MAX(transactions.amount)': 'Largest transaction ever',
    'accounts.MEAN(monthly_stats.total_spend)': 'Avg monthly spend',
    'accounts.MAX(monthly_stats.total_spend)': 'Highest single-month spend',
    'accounts.SUM(monthly_stats.total_spend)': 'Lifetime total spend',
    'accounts.balances_current': 'Current balance',
    'days_since_last': 'Days since last transaction',
    'accounts.TIME_SINCE_LAST(transactions.date)': 'Seconds since last transaction',
    'merchant_diversity': 'Unique merchants visited',
    'new_merchant_count': 'New merchants explored',
}

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'anomaly_models.pkl')


def get_severity(is_anomaly, score):
    if not is_anomaly: return 'Normal'
    if score >= 80: return 'Critical'
    if score >= 65: return 'High'
    return 'Medium'

def per_account_anomaly_summary(user_id: str, transactions_df: pd.DataFrame, accounts_info: dict) -> list:
    summary = []
    for acc in accounts_info.get("accounts", []):
        acc_id = acc["account_id"]
        acc_trans = transactions_df[transactions_df["account_id"] == acc_id]

        if acc_trans.empty:
            summary.append({
                "account_id": acc_id,
                "account_name": acc.get("name", ""),
                "account_type": acc.get("type", ""),
                "currency_code": acc.get("currency_code", ""),
                "transaction_count": 0,
                "unusually_large_count": 0,
                "unusually_small_count": 0,
                "avg_transaction_amount": 0.0,
                "top_merchant": None,
            })
            continue

        top_merch = (
            acc_trans.groupby("merchant_name")["amount"]
            .sum().abs().idxmax()
            if "merchant_name" in acc_trans.columns else None
        )
        summary.append({
            "account_id": acc_id,
            "account_name": acc.get("name", ""),
            "account_type": acc.get("type", ""),
            "currency_code": acc.get("currency_code", ""),
            "transaction_count": int(len(acc_trans)),
            "unusually_large_count": int((acc_trans["spend_anomaly_type"] == "Unusually Large").sum())
                if "spend_anomaly_type" in acc_trans.columns else 0,
            "unusually_small_count": int((acc_trans["spend_anomaly_type"] == "Unusually Small").sum())
                if "spend_anomaly_type" in acc_trans.columns else 0,
            "avg_transaction_amount": round(float(acc_trans["amount"].abs().mean()), 2),
            "top_merchant": str(top_merch) if top_merch else None,
        })
    return summary

def identify_drivers(user_row, user_segment, segment_medians, overall_medians,available_features, top_n=3):
    if user_segment in segment_medians.index:
        reference = segment_medians.loc[user_segment]
        reference_label = f"{user_segment} segment"
    else:
        reference = overall_medians
        reference_label = "all users"

    deviations = {}
    for col in available_features:
        if col not in reference.index:
            continue
        m = reference[col]
        v = user_row[col]
        deviations[col] = abs(v - m) / (abs(m) + 1e-9)

    top = sorted(deviations.items(), key=lambda x: x[1], reverse=True)[:top_n]
    results = []
    for feat, dev in top:
        uv = round(float(user_row[feat]), 2)
        mv = round(float(reference[feat]), 2)
        direction = 'above' if uv > mv else 'below'
        label = FEATURE_LABELS.get(feat, feat)
        results.append(
            f"{label}: {uv} ({reference_label} median is {mv} — "
            f"you are {direction} average by {round(dev, 1)}x)"
        )
    return results


def run_anomaly_detection(user_id=None):
    engine = get_engine() if DB_AVAILABLE else None

    fm_encoded = read_data('fm_encoded').set_index('user_id')
    transactions_df = read_data('transactions_enriched')
    transactions_df['date'] = pd.to_datetime(transactions_df['date'])

    available_features = [f for f in ALL_ANOMALY_FEATURES if f in fm_encoded.columns]
    X = fm_encoded[available_features].fillna(0).copy()
    X.index = fm_encoded.index

    if user_id is not None:
        try:
            with open(MODEL_PATH, 'rb') as f:
                bundle = pickle.load(f)
            iso_forest = bundle['iso_forest']
            scaler = bundle['scaler']
            saved_feat = bundle['feature_cols']
            segment_medians = bundle.get('segment_medians', pd.DataFrame())
            overall_medians = bundle.get('overall_medians', pd.Series(dtype=float))

            X_user = X.loc[[user_id], saved_feat].fillna(0)
            X_scaled = scaler.transform(X_user)

            iso_label = iso_forest.predict(X_scaled)[0]
            iso_score = iso_forest.score_samples(X_scaled)[0]

            iso_norm = float(
                1 - (iso_score - bundle['iso_score_min']) /
                (bundle['iso_score_max'] - bundle['iso_score_min'])
            )
            anomaly_score = round(iso_norm * 100, 2)
            is_anomaly = iso_label == -1

            user_segment = fm_encoded.loc[user_id].get('task_segment', None)
            drivers = identify_drivers(
                X.loc[user_id, saved_feat],
                user_segment,
                segment_medians,
                overall_medians,
                saved_feat,
            )

            row = fm_encoded.loc[user_id]
            result = pd.DataFrame([{
                'user_id': user_id,
                'iso_score': round(iso_norm * 100, 2),
                'lof_score': round(iso_norm * 100, 2),  
                'anomaly_score': anomaly_score,
                'iso_flag': is_anomaly,
                'lof_flag': is_anomaly,
                'is_anomaly': is_anomaly,
                'severity': get_severity(is_anomaly, anomaly_score),
                **{f: row.get(f, 0) for f in saved_feat},
                'task_segment': row.get('task_segment', ''),
                'top_category': row.get('top_category', ''),
                'top_merchant': row.get('top_merchant', ''),
                'primary_spending_trend': row.get('primary_spending_trend', ''),
            }]).set_index('user_id')

            result.to_sql('anomaly_scores', engine, if_exists='append',index=True, method='multi')
            return result

        except FileNotFoundError:
            print("No saved model found — running full retrain...")
            user_id = None

    # train on all users
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    iso_forest = IsolationForest(n_estimators=200, contamination=0.05, max_features=1.0, random_state=42, n_jobs=-1)
    iso_labels = iso_forest.fit_predict(X_scaled)
    iso_scores = iso_forest.score_samples(X_scaled)

    lof = LocalOutlierFactor(n_neighbors=min(20, len(X)-1), contamination=0.05, metric='euclidean', n_jobs=-1)
    lof_labels = lof.fit_predict(X_scaled)
    lof_scores = lof.negative_outlier_factor_

    # Normalize 0–100
    iso_norm = 1 - (iso_scores - iso_scores.min()) / (iso_scores.max() - iso_scores.min())
    lof_norm = 1 - (lof_scores - lof_scores.min()) / (lof_scores.max() - lof_scores.min())

    anomaly_df = pd.DataFrame(index=fm_encoded.index)
    anomaly_df['iso_flag'] = iso_labels == -1
    anomaly_df['lof_flag'] = lof_labels == -1
    anomaly_df['is_anomaly'] = anomaly_df['iso_flag'] & anomaly_df['lof_flag']
    anomaly_df['iso_score'] = (iso_norm * 100).round(2)
    anomaly_df['lof_score'] = (lof_norm * 100).round(2)
    anomaly_df['anomaly_score'] = ((iso_norm + lof_norm) / 2 * 100).round(2)
    anomaly_df['severity'] = [ get_severity(a, s) for a, s in zip(anomaly_df['is_anomaly'], anomaly_df['anomaly_score'])]

    for col in available_features:
        anomaly_df[col] = fm_encoded[col]
    for col in ['task_segment','top_category','top_merchant','primary_spending_trend']:
        if col in fm_encoded.columns:
            anomaly_df[col] = fm_encoded[col]

    if 'task_segment' in fm_encoded.columns:
        segments = fm_encoded.loc[X.index, 'task_segment']
        segment_medians = X.groupby(segments).median()
    else:
        segment_medians = pd.DataFrame()

    overall_medians = X.median()

    def _drivers_for(uid):
        user_segment = (
            fm_encoded.loc[uid].get('task_segment', None)
            if 'task_segment' in fm_encoded.columns
            else None
        )
        return identify_drivers(
            X.loc[uid],
            user_segment,
            segment_medians,
            overall_medians,
            available_features,
        )

    anomaly_df['anomaly_drivers'] = anomaly_df.index.to_series().apply(_drivers_for)

    if DB_AVAILABLE:
        users_accounts = pd.read_sql(
            "SELECT u.user_id, a.account_id, a.name, a.type, a.currency_code "
            "FROM accounts a JOIN users u ON u.account_id = a.account_id",
            engine
        )
    else:
        users_csv = pd.read_csv(CSV_DIR / "users.csv")
        accounts_csv = pd.read_csv(CSV_DIR / "accounts.csv")
        users_accounts = users_csv[['user_id', 'account_id']].merge(
            accounts_csv[['account_id', 'name', 'type', 'currency_code']],
            on='account_id', how='left'
        )
    acc_grouped = users_accounts.groupby("user_id")

    def account_ids_for(uid):
        if uid in acc_grouped.groups:
            return acc_grouped.get_group(uid)["account_id"].tolist()
        return []

    anomaly_df["account_ids"] = anomaly_df.index.to_series().apply(lambda uid: json.dumps(account_ids_for(uid)))
    anomaly_df["primary_account_id"] = anomaly_df.index.to_series().apply(lambda uid: (account_ids_for(uid) or [None])[0])
    anomaly_df["account_count"] = anomaly_df.index.to_series().apply(lambda uid: len(account_ids_for(uid)))
    
    # Save model bundle
    bundle = {
        'iso_forest': iso_forest,
        'scaler': scaler,
        'feature_cols': available_features,
        'iso_score_min': float(iso_scores.min()),
        'iso_score_max': float(iso_scores.max()),
        'segment_medians': segment_medians,
        'overall_medians': overall_medians,
    }
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(bundle, f)
    print(f"[anomaly] Model saved: {MODEL_PATH}")

    # Write to DB
    anomaly_df['anomaly_drivers_json'] = anomaly_df['anomaly_drivers'].apply(lambda drivers: json.dumps(drivers) if drivers else '[]')
    write_data(anomaly_df.drop(columns=['anomaly_drivers']),'anomaly_scores',if_exists='replace',)

    flagged = anomaly_df['is_anomaly'].sum()
    print(f"[anomaly] Done — {flagged}/{len(anomaly_df)} users flagged")
    return anomaly_df


def run_anomaly_check(user_id):
    engine = get_engine() if DB_AVAILABLE else None
    row_df = read_data(
        'anomaly_scores',
        query=f"SELECT * FROM anomaly_scores WHERE user_id = {user_id}" if DB_AVAILABLE else None,
        engine=engine
    )
    if DB_AVAILABLE:
        pass  
    else:
        row_df = row_df[row_df['user_id'] == user_id]

    if row_df.empty:
        return {'error': f'User {user_id} not found', 'is_anomaly': False, 'anomaly_score': 0}

    row = row_df.iloc[0]
    trans_df = read_data(
        'transactions_enriched',
        query=f"SELECT * FROM transactions_enriched WHERE user_id = {user_id}" if DB_AVAILABLE else None,
        engine=engine
    )
    if not DB_AVAILABLE:
        trans_df = trans_df[trans_df['user_id'] == user_id]
    trans_df['date'] = pd.to_datetime(trans_df['date'])

    accounts_info = get_user_accounts(user_id, engine)

    # Suspicious transactions
    if not trans_df.empty:
        pmap = {'Unusually Large': 0, 'Unusually Small': 1, 'Normal': 2}
        trans_df['_p'] = trans_df['spend_anomaly_type'].map(pmap).fillna(2)
        suspicious = (
            trans_df.sort_values(['_p','deviation_ratio'], ascending=[True, False])
            .head(5)[['date','amount','merchant_name','category_id',
                       'account_id','deviation_ratio','spend_anomaly_type']]
            .to_dict('records')
        )
        anomaly_summary = trans_df['spend_anomaly_type'].value_counts().to_dict()
    else:
        suspicious    = []
        anomaly_summary = {}

    # Per-account breakdown
    per_account = per_account_anomaly_summary(user_id, trans_df, accounts_info)

    return {
        'user_id': str(user_id),
        'is_anomaly': bool(row['is_anomaly']),
        'anomaly_score': float(row['anomaly_score']),
        'severity': str(row['severity']),
        'iso_flagged': bool(row['iso_flag']),
        'lof_flagged': bool(row['lof_flag']),
        'transactions_today': int(row.get('vel_1d', 0)),
        'transactions_this_week': int(row.get('vel_7d', 0)),
        'transactions_this_month': int(row.get('vel_30d', 0)),
        'avg_transaction_amt_30d': round(float(row.get('avg_amt_30d', 0)), 2),
        'days_since_last_transaction': round(float(row.get('days_since_last', 0)), 1),
        'unique_merchants_visited': int(row.get('merchant_diversity', 0)),
        'spending_segment': str(row.get('task_segment', '')),
        'top_category': str(row.get('top_category', '')),
        'spending_trend': str(row.get('primary_spending_trend', '')),
        'suspicious_transactions': suspicious,
        'transaction_anomaly_summary': anomaly_summary,
        'primary_account_id': accounts_info['primary_account_id'],
        'account_ids': accounts_info['account_ids'],
        'account_count': accounts_info['account_count'],
        'per_account': per_account,
    }