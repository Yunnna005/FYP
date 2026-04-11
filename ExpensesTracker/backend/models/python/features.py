import pandas as pd
import numpy as np
import json
import featuretools as ft
from sqlalchemy import text
from featuretools.primitives import Day, Weekday, IsWeekend, Mean, Sum, Count, Max, Std, TimeSincePrevious, TimeSinceLast
import warnings
warnings.filterwarnings('ignore')

from models.db.dbconfig import get_engine, read_query, write_data, DB_AVAILABLE, CSV_DIR

def load_raw_data(engine, user_id=None):
    if DB_AVAILABLE:
        if user_id:
            acc_row = read_query(
                "SELECT account_id FROM users WHERE user_id = :uid",
                engine,
                params={"uid": user_id},
            )
            if acc_row.empty:
                raise ValueError(f"User {user_id} not found in database")
            acc_ids = acc_row['account_id'].tolist()

            users_df = read_query(
                "SELECT * FROM users WHERE user_id = :uid",
                engine,
                params={"uid": user_id},
            )
            accounts_df = read_query(
                "SELECT * FROM accounts WHERE account_id = ANY(:acc_ids)",
                engine,
                params={"acc_ids": acc_ids},
            )
            transactions_df = read_query(
                "SELECT * FROM transactions WHERE account_id = ANY(:acc_ids)",
                engine,
                params={"acc_ids": acc_ids},
            )
        else:
            users_df = read_query("SELECT * FROM users", engine)
            accounts_df = read_query(
                "SELECT a.* FROM accounts a JOIN users u ON u.account_id = a.account_id",
                engine,
            )
            transactions_df = read_query(
                "SELECT t.* FROM transactions t JOIN users u ON u.account_id = t.account_id",
                engine,
            )
    else:
        users_df = pd.read_csv(CSV_DIR / "users.csv")
        accounts_df = pd.read_csv(CSV_DIR / "accounts.csv")
        transactions_df = pd.read_csv(CSV_DIR / "transactions.csv")
        if user_id:
            users_df = users_df[users_df["user_id"] == user_id]
            acc_ids = users_df["account_id"].tolist()
            accounts_df = accounts_df[accounts_df["account_id"].isin(acc_ids)]
            transactions_df = transactions_df[transactions_df["account_id"].isin(acc_ids)]
    return users_df, accounts_df, transactions_df

def run_feature_engineering(user_id=None):
    engine = get_engine()
    print(f"[features] Loading data {'for user ' + str(user_id) if user_id else 'for all users'}...")

    users_df, accounts_df, transactions_df = load_raw_data(engine, user_id)

    transactions_df['date'] = pd.to_datetime(transactions_df['date'])

    account_to_user = users_df.set_index('account_id')['user_id'].to_dict()
    transactions_df['user_id'] = transactions_df['account_id'].map(account_to_user)
    accounts_df['user_id'] = accounts_df['account_id'].map(account_to_user)

    print("[features] Building EntitySet...")
    es = ft.EntitySet(id="financial_system")
    es.add_dataframe(dataframe_name="users", dataframe=users_df, index="user_id")
    es.add_dataframe(dataframe_name="accounts", dataframe=accounts_df, index="account_id")
    es.add_dataframe(dataframe_name="transactions", dataframe=transactions_df, index="transaction_id", time_index="date")
    es.add_relationship("accounts", "account_id", "users", "account_id")
    es.add_relationship("accounts", "account_id", "transactions", "account_id")

    #DFS
    print("[features] Running DFS...")
    last_date   = transactions_df['date'].max()
    cutoff_times = pd.DataFrame({'user_id': users_df['user_id'], 'time': last_date})

    feature_matrix, feature_defs = ft.dfs(
        entityset=es,
        target_dataframe_name="users",
        cutoff_time=cutoff_times,
        trans_primitives=[Day, Weekday, IsWeekend, TimeSincePrevious],
        agg_primitives=[Mean, Sum, Count, Max, Std, TimeSinceLast],
        max_depth=2,
        verbose=False
    )

    numeric_cols = feature_matrix.select_dtypes(include=[np.number]).columns
    feature_matrix[numeric_cols] = feature_matrix[numeric_cols].fillna(0)

    # Correlation filter
    corr_matrix = feature_matrix.corr(numeric_only=True).abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    protected = ['TIME_SINCE', 'COUNT(transactions)']
    to_drop = [c for c in upper.columns if any(upper[c] > 0.95) and not any(k in c for k in protected)]
    feature_matrix = feature_matrix.drop(columns=to_drop)

    #Encode
    remaining = [f for f in feature_defs if any(n in feature_matrix.columns for n in f.get_feature_names())]
    feature_matrix.ww.init()
    fm_encoded, _ = ft.encode_features(feature_matrix, remaining, top_n=10)

    #Custom metrics
    print("[features] Computing custom metrics...")
    recency_col = [c for c in fm_encoded.columns if 'TIME_SINCE_LAST' in c][0]
    fm_encoded['days_since_last'] = fm_encoded[recency_col] / 86400

    # Velocity metrics
    def calc_velocity(uid, trans_df):
        ut = trans_df[trans_df['user_id'] == uid].sort_values('date')
        if ut.empty:
            return pd.Series([0, 0, 0, 0], index=['days_since_last', 'vel_1d', 'vel_7d', 'vel_30d'])
        last = ut['date'].max()
        return pd.Series([
            0,
            len(ut[ut['date'] >= last - pd.Timedelta(days=1)]),
            len(ut[ut['date'] >= last - pd.Timedelta(days=7)]),
            len(ut[ut['date'] >= last - pd.Timedelta(days=30)]),
        ], index=['days_since_last', 'vel_1d', 'vel_7d', 'vel_30d'])

    velocity = fm_encoded.index.to_series().apply(lambda x: calc_velocity(x, transactions_df))
    fm_encoded[['days_since_last', 'vel_1d', 'vel_7d', 'vel_30d']] = velocity

    # Behaviour segment
    def classify_behaviour(row):
        v7, v30, v1 = row['vel_7d'], row['vel_30d'], row['vel_1d']
        if v1 >= 5 or v7 >= 20: return 'High-Intensity User'
        if 3 <= v7 <= 10: return 'Healthy Active User'
        if v7 == 2: return 'Consistent Weekly'
        if v7 == 1: return 'Single-Tasker'
        if v7 == 0 and v30 >= 1:   return 'Monthly/Occasional'
        return 'Low Activity/Trial'

    fm_encoded['task_segment'] = fm_encoded.apply(classify_behaviour, axis=1)

    # Top category and merchant
    transactions_df = transactions_df.sort_values(['user_id', 'date'])
    transactions_df['is_new_merchant'] = ~transactions_df.duplicated(subset=['user_id', 'merchant_name'], keep='first')

    cat_spend = transactions_df.groupby(['user_id','category_id'])['amount'].sum().abs().reset_index()
    top_cat = cat_spend.sort_values(['user_id','amount'],ascending=[True,False]).groupby('user_id').head(1)
    merch_spend= transactions_df.groupby(['user_id','merchant_name'])['amount'].sum().abs().reset_index()
    top_merch = merch_spend.sort_values(['user_id','amount'],ascending=[True,False]).groupby('user_id').head(1)

    fm_encoded['top_category'] = top_cat.set_index('user_id')['category_id']
    fm_encoded['top_merchant'] = top_merch.set_index('user_id')['merchant_name']

    # Spending trend
    def category_trend(uid, trans_df):
        ut = trans_df[trans_df['user_id'] == uid]
        if ut.empty: return "No Data"
        cutoff = ut['date'].max() - pd.Timedelta(days=30)
        recent = ut[ut['date'] > cutoff].groupby('category_id')['amount'].sum().abs()
        history = ut[ut['date'] <= cutoff].groupby('category_id')['amount'].sum().abs()
        trends = recent / (history + 1)
        return f"Surging in {trends.idxmax()}" if not trends.empty else "Stable"

    fm_encoded['primary_spending_trend'] = fm_encoded.index.to_series().apply(lambda x: category_trend(x, transactions_df))

    # Merchant diversity
    merch_stats = transactions_df.groupby('user_id').agg(
        merchant_name  = ('merchant_name',  'nunique'),
        transaction_id = ('transaction_id', 'count'),
        is_new_merchant= ('is_new_merchant','sum'),
    )
    merch_stats['merchant_diversity'] = (merch_stats['merchant_name'] / merch_stats['transaction_id']).round(2)
    fm_encoded['merchant_diversity'] = merch_stats['merchant_diversity']
    fm_encoded['new_merchant_count'] = merch_stats['is_new_merchant']
    fm_encoded[['merchant_diversity','new_merchant_count']] = fm_encoded[['merchant_diversity','new_merchant_count']].fillna(0)

    # Deviation ratio on transactions
    spending_only = transactions_df[transactions_df['amount'] < 0].copy()
    user_spending_baselines = (
        spending_only.groupby('user_id')['amount']
        .apply(lambda s: s.abs().mean())
        .to_dict()
    )
    transactions_df['user_avg_amount'] = transactions_df['user_id'].map(user_spending_baselines)


    def classify_deviation(row):
        baseline = row['user_avg_amount']
        if pd.isna(baseline) or baseline <= 0:
            return 'Normal'
        if row['amount'] >= 0:
            return 'Normal'  # income is never classified as unusual spending
        magnitude = abs(row['amount'])
        ratio = magnitude / baseline
        if ratio > 3.0:
            return 'Unusually Large'
        if ratio < 0.3:
            return 'Unusually Small'
        return 'Normal'


    transactions_df['spend_anomaly_type'] = transactions_df.apply(classify_deviation, axis=1)

    transactions_df['deviation_ratio'] = transactions_df.apply(
        lambda r: (abs(r['amount']) / r['user_avg_amount'])
        if (r['amount'] < 0 and pd.notna(r['user_avg_amount']) and r['user_avg_amount'] > 0)
        else 0.0,
        axis=1,
    )

    # 30d behaviour
    def behavior_30d(uid, trans_df):
        ut = trans_df[trans_df['user_id'] == uid]
        if ut.empty:
            return pd.Series([0, 0], index=['avg_amt_30d', 'count_30d'])
        last30 = ut[ut['date'] >= ut['date'].max() - pd.Timedelta(days=30)]

        spending_only = last30[last30['amount'] < 0]
        if spending_only.empty:
            return pd.Series([0, len(last30)], index=['avg_amt_30d', 'count_30d'])

        return pd.Series(
            [spending_only['amount'].abs().mean(), len(last30)],
            index=['avg_amt_30d', 'count_30d'],
        )

    b30 = fm_encoded.index.to_series().apply(lambda x: behavior_30d(x, transactions_df))
    fm_encoded[['avg_amt_30d','count_30d']] = b30

    acc_grouped = accounts_df.groupby('user_id')

    def _acc_ids(uid):
            if uid in acc_grouped.groups:
                return acc_grouped.get_group(uid)['account_id'].tolist()
            return []

    fm_encoded['account_ids'] = fm_encoded.index.to_series().apply(lambda uid: json.dumps(_acc_ids(uid)))
    fm_encoded['primary_account_id'] = fm_encoded.index.to_series().apply(lambda uid: (_acc_ids(uid) or [None])[0])
    fm_encoded['account_count'] = fm_encoded.index.to_series().apply(lambda uid: len(_acc_ids(uid)))

    #PostgreSQL
    print("[features] Writing to database...")

    if user_id:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM fm_encoded WHERE user_id = :uid"), {"uid": user_id})
            conn.execute(text("DELETE FROM transactions_enriched WHERE user_id = :uid"), {"uid": user_id})
        write_data(fm_encoded, 'fm_encoded', if_exists='append')
        write_data(transactions_df, 'transactions_enriched', if_exists='append', index=False)
    else:
        write_data(fm_encoded, 'fm_encoded', if_exists='replace')
        write_data(transactions_df, 'transactions_enriched', if_exists='replace', index=False)

    print(f"[features] Done — {len(fm_encoded)} users in fm_encoded")
    return fm_encoded, transactions_df