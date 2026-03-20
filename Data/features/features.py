import pandas as pd
import numpy as np
import json
import featuretools as ft
from featuretools.primitives import Day, Weekday, IsWeekend, Mean, Sum, Count, Max, Std, TimeSincePrevious, TimeSinceLast
import warnings
warnings.filterwarnings('ignore')

from db.config import get_engine, read_query, write_table


def expand_json_categories(df, column_name):
    json_as_df = (
        df[column_name]
        .apply(lambda x: json.loads(x.replace("'", '"')) if isinstance(x, str) else x)
        .apply(pd.Series)
        .fillna(0)
    )
    return pd.concat([df.drop(columns=[column_name]), json_as_df], axis=1)


def load_raw_data(engine, user_id=None):
    uid_filter = f"WHERE user_id = {user_id}" if user_id else ""
    acc_filter = ""

    if user_id:
        acc_df = read_query(
            f"SELECT account_id FROM users WHERE user_id = {user_id}", engine
        )
        if acc_df.empty:
            raise ValueError(f"User {user_id} not found in database")
        acc_ids = tuple(acc_df['account_id'].tolist())
        acc_filter = f"WHERE account_id IN {acc_ids}" if len(acc_ids) > 1 \
                     else f"WHERE account_id = {acc_ids[0]}"

    users_df = read_query(f"SELECT * FROM users {uid_filter}", engine)
    accounts_df = read_query(f"SELECT * FROM accounts {acc_filter}", engine)
    transactions_df = read_query(f"SELECT * FROM transactions {acc_filter}", engine)
    monthly_stats_df = read_query(f"SELECT * FROM user_monthly_stats {acc_filter}", engine)
    all_time_stats_df = read_query(f"SELECT * FROM user_all_time_stats {acc_filter}", engine)

    return users_df, accounts_df, transactions_df, monthly_stats_df, all_time_stats_df


def run_feature_engineering(user_id=None):
    engine = get_engine()
    print(f"[features] Loading data {'for user ' + str(user_id) if user_id else 'for all users'}...")

    users_df, accounts_df, transactions_df, monthly_stats_df, all_time_stats_df = \
        load_raw_data(engine, user_id)

    # Parse dates
    transactions_df['date'] = pd.to_datetime(transactions_df['date'])
    monthly_stats_df['month_start_date'] = pd.to_datetime(monthly_stats_df['month_start_date'])

    if 'spending_by_category' in monthly_stats_df.columns:
        monthly_stats_df = expand_json_categories(monthly_stats_df, 'spending_by_category')

    #Featuretools setup
    print("[features] Building Setup...")
    es = ft.EntitySet(id="financial_system")
    es.add_dataframe(dataframe_name="users", dataframe=users_df, index="user_id")
    es.add_dataframe(dataframe_name="accounts", dataframe=accounts_df, index="account_id")
    es.add_dataframe(dataframe_name="transactions", dataframe=transactions_df, index="transaction_id", time_index="date")
    es.add_dataframe(dataframe_name="monthly_stats", dataframe=monthly_stats_df, index="stats_id", time_index="month_start_date")
    es.add_dataframe(dataframe_name="all_time_stats", dataframe=all_time_stats_df, index="stats_id")

    es.add_relationship("accounts", "account_id", "users", "account_id")
    es.add_relationship("accounts", "account_id", "transactions", "account_id")
    es.add_relationship("accounts", "account_id", "monthly_stats","account_id")
    es.add_relationship("accounts", "account_id", "all_time_stats","account_id")

    # DFS
    print("[features] Running DFS...")
    last_date = transactions_df['date'].max()
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

    #Correlation filter
    corr_matrix = feature_matrix.corr(numeric_only=True).abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    protected = ['TIME_SINCE', 'COUNT(transactions)']
    to_drop = [c for c in upper.columns
            if any(upper[c] > 0.95) and not any(k in c for k in protected)]
    feature_matrix = feature_matrix.drop(columns=to_drop)

    # Encode 
    remaining = [f for f in feature_defs
                 if any(n in feature_matrix.columns for n in f.get_feature_names())]
    feature_matrix.ww.init()
    fm_encoded, _ = ft.encode_features(feature_matrix, remaining, top_n=10)

    #Custom metrics
    print("[features] Computing custom metrics...")
    recency_col = [c for c in fm_encoded.columns if 'TIME_SINCE_LAST' in c][0]
    fm_encoded['days_since_last'] = fm_encoded[recency_col] / 86400

    account_to_user = users_df.set_index('account_id')['user_id'].to_dict()
    transactions_df['user_id'] = transactions_df['account_id'].map(account_to_user)

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
    fm_encoded[['merchant_diversity','new_merchant_count']] = \
        fm_encoded[['merchant_diversity','new_merchant_count']].fillna(0)

    # Deviation ratio on transactions
    user_baselines = transactions_df.groupby('user_id')['amount'].mean().to_dict()
    transactions_df['user_avg_amount'] = transactions_df['user_id'].map(user_baselines)
    transactions_df['deviation_ratio'] = transactions_df['amount'] / transactions_df['user_avg_amount']

    def classify_deviation(d):
        if d > 3.0: return 'Unusually Large'
        if d < 0.5: return 'Unusually Small'
        return 'Normal'

    transactions_df['spend_anomaly_type'] = transactions_df['deviation_ratio'].apply(classify_deviation)

    # 30d behaviour
    def behavior_30d(uid, trans_df):
        ut = trans_df[trans_df['user_id'] == uid]
        if ut.empty: return pd.Series([0, 0], index=['avg_amt_30d','count_30d'])
        last30 = ut[ut['date'] >= ut['date'].max() - pd.Timedelta(days=30)]
        return pd.Series([last30['amount'].mean(), len(last30)], index=['avg_amt_30d','count_30d'])

    b30 = fm_encoded.index.to_series().apply(lambda x: behavior_30d(x, transactions_df))
    fm_encoded[['avg_amt_30d','count_30d']] = b30

    # PostgreSQL
    print("[features] Writing to database...")

    if user_id:
        upsert_fm_encoded(fm_encoded, engine)
        upsert_transactions(transactions_df, engine)
    else:
        write_table(fm_encoded, 'fm_encoded', if_exists='replace', engine=engine)
        write_table(transactions_df, 'transactions_enriched', if_exists='replace', engine=engine)

    print(f"[features] Done — {len(fm_encoded)} users in fm_encoded")
    return fm_encoded, transactions_df


def upsert_fm_encoded(fm_encoded, engine):
    from sqlalchemy.dialects.postgresql import insert
    fm_encoded.reset_index().to_sql(
        'fm_encoded', engine, if_exists='append', index=False,
        method='multi', chunksize=100
    )


def upsert_transactions(transactions_df, engine):
    transactions_df.to_sql(
        'transactions_enriched', engine, if_exists='append',
        index=False, method='multi', chunksize=500
    )
