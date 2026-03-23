import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

from prophet import Prophet
from dbconfig import get_engine, write_table


def forecast_with_prophet(series_df, target_col, periods=1):
    df = series_df[['month', target_col]].copy()
    df.columns = ['ds', 'y']
    df = df.dropna().sort_values('ds')
    m = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False, changepoint_prior_scale=0.1, interval_width=0.80)
    m.fit(df)
    future = m.make_future_dataframe(periods=periods, freq='MS')
    forecast = m.predict(future)
    last = forecast.iloc[-1]
    return (max(0, round(float(last['yhat']), 2)),
            max(0, round(float(last['yhat_lower']), 2)),
            max(0, round(float(last['yhat_upper']), 2)),
            last['ds'])


def forecast_with_wma(series, n_weights=3):
    values = series.dropna().values[-n_weights:]
    if len(values) == 0:
        return None, None, None
    weights = np.arange(1, len(values) + 1, dtype=float)
    forecast = float(np.average(values, weights=weights))
    return round(forecast, 2), max(0, round(forecast * 0.80, 2)), round(forecast * 1.20, 2)


def forecast_categories(user_id, monthly_category, top_n=3):
    user_cat = monthly_category[monthly_category['user_id'] == user_id].copy()
    if user_cat.empty: return {}
    cat_totals = user_cat.groupby('category_id')['category_spend'].sum()
    top_cats = cat_totals.nlargest(top_n).index.tolist()
    cat_forecasts = {}
    for cat in top_cats:
        series = user_cat[user_cat['category_id'] == cat].sort_values('month')['category_spend']
        pt, lo, hi = forecast_with_wma(series)
        if pt is not None:
            cat_forecasts[str(cat)] = {
                'forecast': pt, 'lower': lo, 'upper': hi,
                'hist_avg': round(float(series.mean()), 2),
                'data_points': len(series)
            }
    return cat_forecasts


def build_forecast_record(user_id, user_monthly, segment, monthly_category, segment_medians, global_medians):
    n_months = len(user_monthly)
    next_month = user_monthly['month'].max() + pd.DateOffset(months=1)
    rec = {'user_id': user_id, 'forecast_month': next_month,
           'n_months_history': n_months, 'segment': segment}

    # Total spend
    if n_months >= 4:
        try:
            pt, lo, hi, _ = forecast_with_prophet(user_monthly, 'total_spend')
            rec.update({'spend_forecast': pt, 'spend_lower': lo, 'spend_upper': hi, 'spend_method': 'prophet'})
        except Exception:
            pt, lo, hi = forecast_with_wma(user_monthly['total_spend'])
            rec.update({'spend_forecast': pt or 0, 'spend_lower': lo or 0, 'spend_upper': hi or 0, 'spend_method': 'wma_fallback'})
    elif n_months >= 2:
        pt, lo, hi = forecast_with_wma(user_monthly['total_spend'])
        rec.update({'spend_forecast': pt or 0, 'spend_lower': lo or 0, 'spend_upper': hi or 0, 'spend_method': 'wma'})
    else:
        med = float(segment_medians.loc[segment, 'total_spend']) \
              if segment in segment_medians.index else float(global_medians['total_spend'])
        rec.update({'spend_forecast': round(med,2), 'spend_lower': round(med*0.8,2),
                    'spend_upper': round(med*1.2,2), 'spend_method': 'segment_median'})

    # Transaction count
    if n_months >= 4:
        try:
            pt, lo, hi, _ = forecast_with_prophet(user_monthly, 'transaction_count')
            rec.update({'count_forecast': int(round(pt)), 'count_lower': int(round(lo)),
                        'count_upper': int(round(hi)), 'count_method': 'prophet'})
        except Exception:
            pt, lo, hi = forecast_with_wma(user_monthly['transaction_count'])
            rec.update({'count_forecast': int(round(pt or 0)), 'count_lower': int(round(lo or 0)),
                        'count_upper': int(round(hi or 0)), 'count_method': 'wma_fallback'})
    else:
        pt, lo, hi = forecast_with_wma(user_monthly['transaction_count'])
        if pt is None:
            med = float(segment_medians.loc[segment,'transaction_count']) \
                  if segment in segment_medians.index else float(global_medians['transaction_count'])
            pt, lo, hi = med, med*0.8, med*1.2
        rec.update({'count_forecast': int(round(pt)), 'count_lower': int(round(lo)),
                    'count_upper': int(round(hi)), 'count_method': 'wma'})

    # Derived avg amount
    rec['avg_amount_forecast'] = round(rec['spend_forecast'] / max(rec['count_forecast'], 1), 2)

    # History context
    rec['hist_avg_spend'] = round(float(user_monthly['total_spend'].mean()), 2)
    rec['hist_avg_count'] = round(float(user_monthly['transaction_count'].mean()), 1)
    rec['last_month_spend'] = round(float(user_monthly['total_spend'].iloc[-1]), 2)
    rec['last_month_count'] = int(user_monthly['transaction_count'].iloc[-1])

    # Direction + confidence
    hist_avg = rec['hist_avg_spend']
    forecast = rec['spend_forecast']
    pct_change = (forecast - hist_avg) / hist_avg * 100 if hist_avg > 0 else 0
    rec['spend_pct_change_vs_hist'] = round(pct_change, 1)
    rec['spend_direction'] = 'increasing' if pct_change > 10 else ('decreasing' if pct_change < -10 else 'stable')

    last = rec['last_month_spend']
    rec['spend_vs_last_month_pct'] = round((forecast - last) / last * 100, 1) if last > 0 else 0

    method = rec['spend_method']
    n = rec['n_months_history']
    rec['confidence'] = 'high' if (method == 'prophet' and n >= 6) \
                        else ('medium' if (method in ('prophet','wma') and n >= 3) \
                        else 'low')
    return rec


def run_sequential_forecasting(user_id=None):
    engine = get_engine()

    transactions_df = pd.read_sql("SELECT * FROM transactions_enriched", engine)
    fm_encoded = pd.read_sql("SELECT * FROM fm_encoded", engine).set_index('user_id')
    transactions_df['date'] = pd.to_datetime(transactions_df['date'])

    transactions_df['month'] = transactions_df['date'].dt.to_period('M').dt.to_timestamp()
    transactions_df['amount_abs'] = transactions_df['amount'].abs()

    monthly_user = (
        transactions_df.groupby(['user_id','month'])
        .agg(total_spend=('amount_abs','sum'), transaction_count=('amount_abs','count'),
             avg_amount=('amount_abs','mean'))
        .reset_index()
    )
    monthly_category = (
        transactions_df.groupby(['user_id','month','category_id'])['amount_abs']
        .sum().reset_index().rename(columns={'amount_abs':'category_spend'})
    )

    segment_map = fm_encoded['task_segment'].to_dict()
    monthly_user['segment'] = monthly_user['user_id'].map(segment_map)

    segment_medians = monthly_user.groupby('segment')[['total_spend','transaction_count','avg_amount']].median()
    global_medians = monthly_user[['total_spend','transaction_count','avg_amount']].median()

    target_users = [user_id] if user_id else monthly_user['user_id'].unique().tolist()
    all_records = []

    for uid in enumerate(target_users):
        user_monthly = monthly_user[monthly_user['user_id'] == uid].sort_values('month')
        if user_monthly.empty: continue
        segment = segment_map.get(uid, None)

        try:
            rec = build_forecast_record(uid, user_monthly, segment, monthly_category, segment_medians, global_medians)
            rec['top_category_forecasts'] = json.dumps(
                forecast_categories(uid, monthly_category))

            pct = abs(rec['spend_pct_change_vs_hist'])
            direct = rec['spend_direction']
            hist = rec['hist_avg_spend']
            rec['trend_summary'] = (
                f"Your spending is forecast to {direct} by {pct:.0f}% vs your historical average."
                if direct != 'stable'
                else f"Your spending is forecast to remain stable near your historical average of ${hist:.0f}."
            )
            rec['confidence_note'] = (
                f"Based on {rec['n_months_history']} months of data using {rec['spend_method']}."
                + (" Treat as indicative only." if rec['confidence'] == 'low' else "")
            )
            rec['forecast_month'] = rec['forecast_month'].strftime('%Y-%m')
            all_records.append(rec)
        except Exception as e:
            print(f"  [forecast] Error for user {uid}: {e}")

    if not all_records:
        print("  [forecast] No records to write.")
        return pd.DataFrame()

    result_df = pd.DataFrame(all_records).set_index('user_id')
    write_table(result_df, 'forecasts', if_exists='replace' if not user_id else 'append', engine=engine)
    return result_df


def run_forecast(user_id):
    engine = get_engine()
    row_df = pd.read_sql(f"SELECT * FROM forecasts WHERE user_id = {user_id}", engine)
    if row_df.empty:
        return {'error': f'User {user_id} not found', 'spend_forecast': None}

    row = row_df.iloc[0]
    cat_forecasts = json.loads(row['top_category_forecasts']) \
                    if row.get('top_category_forecasts') else {}

    cat_summary = [
        {'category': cat, 'forecast': v['forecast'], 'hist_avg': v['hist_avg'],
         'trend': 'up' if v['forecast'] > v['hist_avg'] * 1.1
                  else ('down' if v['forecast'] < v['hist_avg'] * 0.9 else 'stable')}
        for cat, v in cat_forecasts.items()
    ]

    return {
        'user_id': str(row['user_id']),
        'forecast_month': str(row['forecast_month']),
        'spend_forecast': float(row['spend_forecast']),
        'spend_lower': float(row['spend_lower']),
        'spend_upper': float(row['spend_upper']),
        'spend_method': str(row['spend_method']),
        'spend_direction': str(row['spend_direction']),
        'spend_pct_change_vs_hist': float(row['spend_pct_change_vs_hist']),
        'spend_vs_last_month_pct': float(row['spend_vs_last_month_pct']),
        'count_forecast': int(row['count_forecast']),
        'count_lower': int(row['count_lower']),
        'count_upper': int(row['count_upper']),
        'avg_amount_forecast': float(row['avg_amount_forecast']),
        'hist_avg_spend': float(row['hist_avg_spend']),
        'last_month_spend': float(row['last_month_spend']),
        'n_months_history': int(row['n_months_history']),
        'top_category_forecasts': cat_summary,
        'trend_summary': str(row['trend_summary']),
        'confidence': str(row['confidence']),
        'confidence_note': str(row['confidence_note']),
    }
