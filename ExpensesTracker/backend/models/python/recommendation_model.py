import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler

from models.db.dbconfig import get_engine, write_data, get_user_accounts, DB_AVAILABLE, CSV_DIR, read_data

PEER_BENCHMARK_COLS = [
    'vel_7d','vel_30d','avg_amt_30d','count_30d',
    'accounts.MEAN(monthly_stats.total_spend)',
    'accounts.MAX(monthly_stats.total_spend)',
    'accounts.SUM(monthly_stats.total_spend)',
    'merchant_diversity','new_merchant_count','days_since_last',
]
PRIORITY_ORDER = {'high': 0, 'medium': 1, 'low': 2}


def safe_get(row, col, default=0):
    val = row.get(col, default) if hasattr(row, 'get') else getattr(row, col, default)
    return default if pd.isna(val) else val

def check_spending_warnings(user_row, peer_row, user_id, transactions_df):
    warnings_out = []
    avg_30d = safe_get(user_row, 'avg_amt_30d')
    all_time_avg = safe_get(user_row, 'accounts.MEAN(monthly_stats.total_spend)')
    peer_avg = safe_get(peer_row, 'accounts.MEAN(monthly_stats.total_spend)') if peer_row is not None else None

    MIN_MEANINGFUL_AVG = 50

    if (all_time_avg >= MIN_MEANINGFUL_AVG and avg_30d >= MIN_MEANINGFUL_AVG and avg_30d > all_time_avg * 1.4):
        pct = round((avg_30d / all_time_avg - 1) * 100)
        warnings_out.append({
            'type': 'spending_warning',
            'comparison': 'personal',
            'priority': 'high',
            'message': f'Your avg transaction amount this month (${avg_30d:.0f}) is {pct}% above your usual average (${all_time_avg:.0f}).',
            'action': 'Review your recent transactions to identify what changed.',
            'metric': {'avg_amt_30d': avg_30d, 'all_time_avg': all_time_avg, 'pct_above': pct},
    })
        
    if (peer_avg and peer_avg >= MIN_MEANINGFUL_AVG and avg_30d >= MIN_MEANINGFUL_AVG and avg_30d > peer_avg * 1.5):
        pct = round((avg_30d / peer_avg - 1) * 100)
        warnings_out.append({
            'type': 'spending_warning',
            'comparison': 'peer',
            'priority': 'medium',
            'message': f'Your recent avg spend (${avg_30d:.0f}/txn) is {pct}% higher than similar users (${peer_avg:.0f}/txn).',
            'action': 'Consider whether your spending aligns with your financial goals.',
            'metric': {'avg_amt_30d': avg_30d, 'peer_avg': peer_avg, 'pct_above': pct},
    })

    user_trans = transactions_df[transactions_df['user_id'] == user_id]
    if not user_trans.empty:
        large_count = (user_trans['spend_anomaly_type'] == 'Unusually Large').sum()
        if large_count >= 3:
            warnings_out.append({'type':'spending_warning','comparison':'personal','priority':'high',
                'message': f'You have {large_count} unusually large transactions vs your own average.',
                'action': 'Check these transactions — they are significantly larger than your typical spend.',
                'metric': {'large_transactions': int(large_count)}})
    return warnings_out


def check_savings_suggestions(user_row, peer_row):
    suggestions = []
    monthly_spend = safe_get(user_row, 'accounts.MEAN(monthly_stats.total_spend)')
    peer_monthly_spend = safe_get(peer_row, 'accounts.MEAN(monthly_stats.total_spend)') if peer_row is not None else None
    balance = safe_get(user_row, 'accounts.balances_current')

    if peer_monthly_spend and peer_monthly_spend > 0 and monthly_spend > peer_monthly_spend * 1.2:
        saving = round(monthly_spend - peer_monthly_spend, 2)
        suggestions.append({'type':'savings_suggestion','comparison':'peer','priority':'medium',
            'message': f'You spend ${monthly_spend:.0f}/month. Similar users spend ${peer_monthly_spend:.0f}/month.',
            'action': f'Reducing to peer-level spending could save you ~${saving:.0f}/month.',
            'metric': {'monthly_spend': monthly_spend, 'peer_monthly_spend': peer_monthly_spend, 'potential_saving': saving}})

    if 0 < balance < 200:
        suggestions.append({'type':'savings_suggestion','comparison':'personal','priority':'high',
            'message': f'Your current balance is low (${balance:.2f}).',
            'action': 'Consider reducing discretionary spending this month to build a buffer.',
            'metric': {'current_balance': balance}})

    if balance > 1000 and monthly_spend > 0:
        save_rate = round(balance / (monthly_spend + 1) * 100, 1)
        if save_rate < 50:
            suggestions.append({'type':'savings_suggestion','comparison':'personal','priority':'low',
                'message': f'Your balance-to-spend ratio is {save_rate}% — you have room to save more.',
                'action': 'Setting a monthly savings target could help you grow your balance faster.',
                'metric': {'balance': balance, 'monthly_spend': monthly_spend, 'save_rate_pct': save_rate}})
    return suggestions


def check_budget_advice(user_row, peer_row, category_cols):
    advice = []
    if not category_cols: return advice

    user_cat_spend = {}
    for col in category_cols:
        cat_name = col.split('monthly_stats.')[1].rstrip(')')
        val = safe_get(user_row, col)
        if val > 0:
            user_cat_spend[cat_name] = val

    if not user_cat_spend: return advice

    top_cat = max(user_cat_spend, key=user_cat_spend.get)
    top_cat_val = user_cat_spend[top_cat]
    top_cat_col = f'accounts.MEAN(monthly_stats.{top_cat})'

    if peer_row is not None and top_cat_col in peer_row.index:
        peer_cat_val = safe_get(peer_row, top_cat_col)
        if peer_cat_val > 0 and top_cat_val > peer_cat_val * 1.3:
            pct = round((top_cat_val / peer_cat_val - 1) * 100)
            advice.append({'type':'budget_advice','comparison':'peer','priority':'medium',
                'message': f'You spend {pct}% more than similar users on {top_cat} (${top_cat_val:.0f} vs ${peer_cat_val:.0f}/month).',
                'action': f'Setting a monthly budget for {top_cat} could bring your spend in line with peers.',
                'metric': {'category': top_cat, 'user_spend': top_cat_val, 'peer_spend': peer_cat_val, 'pct_above': pct}})

    spikes = {}
    for col in category_cols:
        cat_name = col.split('monthly_stats.')[1].rstrip(')')
        mean_val = safe_get(user_row, col)
        max_col = col.replace('MEAN','MAX')
        max_val = safe_get(user_row, max_col)
        if mean_val > 0 and max_val > mean_val * 2:
            spikes[cat_name] = round(max_val / mean_val, 1)

    if spikes:
        spike_cat = max(spikes, key=spikes.get)
        spike_ratio = spikes[spike_cat]
        advice.append({'type':'budget_advice','comparison':'personal','priority':'medium',
            'message': f'Your {spike_cat} spending spiked to {spike_ratio}x your usual amount in your highest month.',
            'action': f'Consider a monthly cap on {spike_cat} to avoid these irregular spikes.',
            'metric': {'category': spike_cat, 'spike_ratio': spike_ratio}})
    return advice


def check_behavioral_nudges(user_row, peer_row, user_id, transactions_df):
    nudges = []
    vel_1d = safe_get(user_row, 'vel_1d')
    vel_30d = safe_get(user_row, 'vel_30d')
    diversity = safe_get(user_row, 'merchant_diversity')
    days_since = safe_get(user_row, 'days_since_last')
    peer_div = safe_get(peer_row, 'merchant_diversity') if peer_row is not None else None

    if vel_1d >= 4 and vel_30d > 0:
        daily_avg = vel_30d / 30
        if vel_1d > daily_avg * 5:
            nudges.append({'type':'behavioral_nudge','comparison':'personal','priority':'medium',
                'message': f'You made {int(vel_1d)} transactions today — your daily average is {daily_avg:.1f}.',
                'action': "Unusually high transaction days can indicate impulse spending.",
                'metric': {'vel_1d': int(vel_1d), 'daily_avg': round(daily_avg,1)}})

    if peer_div and peer_div > 0 and diversity < peer_div * 0.5:
        nudges.append({'type':'behavioral_nudge','comparison':'peer','priority':'low',
            'message': f'You shop at {int(diversity)} unique merchants — similar users visit {int(peer_div)} on average.',
            'action': 'Exploring alternatives could save money.',
            'metric': {'user_diversity': int(diversity), 'peer_diversity': int(peer_div)}})

    user_trans = transactions_df[transactions_df['user_id'] == user_id].copy()
    if not user_trans.empty:
        user_trans['is_weekend'] = user_trans['date'].dt.weekday >= 5
        wk_spend = user_trans[user_trans['is_weekend']]['amount'].abs().sum()
        wd_spend = user_trans[~user_trans['is_weekend']]['amount'].abs().sum()
        total = wk_spend + wd_spend
        wk_pct = round(wk_spend / total * 100) if total > 0 else 0
        if wk_pct > 55:
            nudges.append({'type':'behavioral_nudge','comparison':'personal','priority':'low',
                'message': f'{wk_pct}% of your total spend happens on weekends.',
                'action': 'Weekend spending often includes more impulse purchases.',
                'metric': {'weekend_spend_pct': wk_pct}})

    if days_since > 14 and vel_30d <= 2:
        nudges.append({'type':'behavioral_nudge','comparison':'personal','priority':'low',
            'message': f'You have been mostly inactive — only {int(vel_30d)} transactions in the last 30 days.',
            'action': 'Check if any scheduled payments may have gone unnoticed.',
            'metric': {'days_since_last': int(days_since), 'vel_30d': int(vel_30d)}})
    return nudges


def generate_user_recommendations(user_id, fm_row, peer_row, transactions_df, category_cols, anomaly_row):
    all_recs = []
    user_trans = transactions_df[transactions_df['user_id'] == user_id].copy()
    if 'date' in user_trans.columns:
        user_trans['date'] = pd.to_datetime(user_trans['date'])

    all_recs += check_spending_warnings(fm_row,  peer_row, user_id, user_trans)
    all_recs += check_savings_suggestions(fm_row, peer_row)
    all_recs += check_budget_advice(fm_row, peer_row, category_cols)
    all_recs += check_behavioral_nudges(fm_row, peer_row, user_id, user_trans)

    if anomaly_row is not None and bool(anomaly_row.get('is_anomaly', False)):
        score = anomaly_row.get('anomaly_score', 0)
        all_recs.append({'type':'spending_warning','comparison':'model','priority':'high',
            'message': f'Our anomaly detection model flagged your account (score: {float(score):.0f}/100).',
            'action': 'Review your recent transactions for any unusual activity.',
            'metric': {'anomaly_score': float(score)}})

    all_recs.sort(key=lambda r: PRIORITY_ORDER.get(r['priority'], 3))
    return all_recs


def run_recommendation_engine(user_id=None):
    engine = get_engine() if DB_AVAILABLE else None
    print(f"[recommendation] Loading data...")

    fm_encoded = read_data('fm_encoded', engine=engine).set_index('user_id')
    transactions_df = read_data('transactions_enriched', engine=engine)
    anomaly_df = read_data('anomaly_scores', engine=engine).set_index('user_id')
    transactions_df['date'] = pd.to_datetime(transactions_df['date'])

    available_benchmark = [c for c in PEER_BENCHMARK_COLS if c in fm_encoded.columns]
    category_cols = [c for c in fm_encoded.columns
                     if 'monthly_stats' in c and 'MEAN' in c
                     and 'total' not in c and 'avg_transaction' not in c]

    peer_benchmarks = fm_encoded.groupby('task_segment')[available_benchmark + category_cols].median()

    # XGBoost feature importance
    print("[recommendation] Training XGBoost for feature importance...")
    health_df = fm_encoded[available_benchmark].fillna(0).copy()
    health_df['anomaly_score'] = anomaly_df['anomaly_score'].reindex(health_df.index).fillna(50)

    score = pd.Series(0, index=health_df.index)
    if 'vel_30d' in health_df.columns:
        score += ((health_df['vel_30d'] >= 3) & (health_df['vel_30d'] <= 25)).astype(int)
    if 'avg_amt_30d' in health_df.columns:
        med = health_df['avg_amt_30d'].median()
        score += ((health_df['avg_amt_30d'] > 0) & (health_df['avg_amt_30d'] <= med * 2.5)).astype(int)
    if 'accounts.balances_current' in fm_encoded.columns:
        score += (fm_encoded['accounts.balances_current'].reindex(health_df.index).fillna(0) > 0).astype(int)
    if 'merchant_diversity' in health_df.columns:
        score += (health_df['merchant_diversity'] >= health_df['merchant_diversity'].median()).astype(int)
    score += (health_df['anomaly_score'] < 50).astype(int)
    health_label = (score >= 3).astype(int)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(health_df)
    xgb = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1,
                         subsample=0.8, colsample_bytree=0.8, random_state=42,
                         eval_metric='logloss', verbosity=0)
    xgb.fit(X_scaled, health_label)

    target_users = [user_id] if user_id else fm_encoded.index.tolist()

    if DB_AVAILABLE:
        all_accounts = pd.read_sql(
            "SELECT u.user_id, a.account_id, a.name, a.type, a.currency_code "
            "FROM accounts a JOIN users u ON u.account_id = a.account_id",
            engine
        )
    else:
        users_csv = pd.read_csv(CSV_DIR / "users.csv")
        accounts_csv = pd.read_csv(CSV_DIR / "accounts.csv")
        all_accounts = users_csv[['user_id', 'account_id']].merge(
            accounts_csv[['account_id', 'name', 'type', 'currency_code']],
            on='account_id', how='left'
        )
    acc_grouped = all_accounts.groupby("user_id")

    def acc_ids(uid):
        if uid in acc_grouped.groups:
            return acc_grouped.get_group(uid)["account_id"].tolist()
        return []

    summary_rows = []
    for uid in target_users:
        if uid not in fm_encoded.index:
            continue
        fm_row = fm_encoded.loc[uid]
        segment = fm_row.get('task_segment', None)
        peer_row = peer_benchmarks.loc[segment] if segment in peer_benchmarks.index else None
        anomaly_row = anomaly_df.loc[uid].to_dict() if uid in anomaly_df.index else None

        recs = generate_user_recommendations(uid, fm_row, peer_row, transactions_df, category_cols, anomaly_row)
        top_rec = recs[0] if recs else None
        user_acc_ids = acc_ids(uid)

        summary_rows.append({
            'user_id': uid,
            'primary_account_id': (user_acc_ids or [None])[0],
            'account_ids': json.dumps(user_acc_ids),
            'account_count': len(user_acc_ids),
            'segment': str(fm_row.get('task_segment', 'Unknown')),
            'total_recommendations': len(recs),
            'high_priority_count': sum(1 for r in recs if r['priority'] == 'high'),
            'top_rec_type': top_rec['type'] if top_rec else None,
            'top_rec_priority': top_rec['priority'] if top_rec else None,
            'top_rec_message': top_rec['message']  if top_rec else None,
            'top_rec_action': top_rec['action']   if top_rec else None,
            'all_recommendations': json.dumps(recs),
            'is_anomaly': bool(anomaly_row.get('is_anomaly', False)) if anomaly_row else False,
            'anomaly_score': float(anomaly_row.get('anomaly_score', 0)) if anomaly_row else 0,
        })

    result_df = pd.DataFrame(summary_rows).set_index('user_id')
    write_data(result_df, 'recommendations',
               if_exists='replace' if not user_id else 'append')

    print(f"[recommendation] Done — {len(result_df)} users processed")
    return result_df


def run_recommendation(user_id):
    engine = get_engine() if DB_AVAILABLE else None
    row_df = read_data(
        'recommendations',
        query=f"SELECT * FROM recommendations WHERE user_id = {user_id}" if DB_AVAILABLE else None,
        engine=engine
    )
    if not DB_AVAILABLE:
        row_df = row_df[row_df['user_id'] == user_id]

    if row_df.empty:
        return {'error': f'User {user_id} not found', 'recommendations': []}

    row  = row_df.iloc[0]
    recs = json.loads(row['all_recommendations']) if row['all_recommendations'] else []

    grouped = {'spending_warning':[], 'savings_suggestion':[], 'budget_advice':[], 'behavioral_nudge':[]}
    for r in recs:
        grouped[r['type']].append(r)

    top_rec = recs[0] if recs else {}
    accounts_info = get_user_accounts(user_id, engine)

    trans_df = read_data(
        'transactions_enriched',
        query=f"SELECT account_id, amount, category_id, merchant_name "
              f"FROM transactions_enriched WHERE user_id = {user_id}" if DB_AVAILABLE else None,
        engine=engine
    )
    if not DB_AVAILABLE:
        trans_df = trans_df[trans_df['user_id'] == user_id][['account_id', 'amount', 'category_id', 'merchant_name']]
    per_account_spend = []
    for acc in accounts_info.get("accounts", []):
        acc_id = acc["account_id"]
        acc_trans = trans_df[trans_df["account_id"] == acc_id]
        per_account_spend.append({
            "account_id": acc_id,
            "account_name": acc.get("name", ""),
            "account_type": acc.get("type", ""),
            "currency_code": acc.get("currency_code", ""),
            "total_spend": round(float(acc_trans["amount"].abs().sum()), 2) if not acc_trans.empty else 0.0,
            "transaction_count": int(len(acc_trans)),
            "avg_amount": round(float(acc_trans["amount"].abs().mean()), 2) if not acc_trans.empty else 0.0,
            "top_category":  (
                acc_trans.groupby("category_id")["amount"].sum().abs().idxmax()
                if not acc_trans.empty and "category_id" in acc_trans.columns else None
            ),
        })

    return {
        'user_id': str(row['user_id']),
        'segment': str(row['segment']),
        'total_recommendations': int(row['total_recommendations']),
        'high_priority_count': int(row['high_priority_count']),
        'top_recommendation': {
            'type': top_rec.get('type'),
            'priority': top_rec.get('priority'),
            'message': top_rec.get('message', 'No issues found — your finances look healthy!'),
            'action': top_rec.get('action', 'Keep up the good work.'),
        },
        'spending_warnings': grouped['spending_warning'],
        'savings_suggestions': grouped['savings_suggestion'],
        'budget_advice': grouped['budget_advice'],
        'behavioral_nudges': grouped['behavioral_nudge'],
        'is_anomaly': bool(row['is_anomaly']),
        'anomaly_score': float(row['anomaly_score']),
        'primary_account_id': accounts_info['primary_account_id'],
        'account_ids': accounts_info['account_ids'],
        'account_count': accounts_info['account_count'],
        'per_account': per_account_spend,
    }
