import json
from typing import Optional
from models.db.dbconfig import read_query

def get_latest_month(user_id: str) -> Optional[str]:
    """Return the most recent month (YYYY-MM) the user has stats for."""
    df = read_query(
        """SELECT MAX(month_start_date) AS latest
           FROM user_monthly_stats
           WHERE user_id = :uid""",
        params={"uid": user_id},
    )
    if df.empty or df.iloc[0]["latest"] is None:
        return None
    latest = df.iloc[0]["latest"]
    return latest.strftime("%Y-%m")

def get_stats(user_id: str, month: Optional[str] = None) -> dict:
    all_time_df = read_query(
        "SELECT * FROM user_all_time_stats WHERE user_id = :uid",
        params={"uid": user_id},
    )

    if month:
        monthly_df = read_query(
            """SELECT * FROM user_monthly_stats
               WHERE user_id = :uid AND month_start_date = :month""",
            params={"uid": user_id, "month": f"{month}-01"},
        )
    else:
        monthly_df = read_query(
            """SELECT * FROM user_monthly_stats
               WHERE user_id = :uid
               ORDER BY month_start_date DESC LIMIT 3""",
            params={"uid": user_id},
        )

    return {
        "all_time": all_time_df.to_dict("records"),
        "monthly": monthly_df.to_dict("records"),
    }

def get_recommendations(user_id: str) -> dict:
    df = read_query(
        """SELECT user_id, segment, total_recommendations, high_priority_count,
                  top_rec_type, top_rec_priority, top_rec_message, top_rec_action,
                  all_recommendations, is_anomaly, anomaly_score
           FROM recommendations
           WHERE user_id = :uid""",
        params={"uid": user_id},
    )

    if df.empty:
        return {}

    row = df.iloc[0].to_dict()

    raw = row.get("all_recommendations")
    if isinstance(raw, str):
        try:
            row["all_recommendations"] = json.loads(raw)
        except json.JSONDecodeError:
            row["all_recommendations"] = []

    return row

def get_forecast(user_id: str) -> dict:
    df = read_query(
        """SELECT user_id, forecast_month, segment,
                  spend_forecast, spend_lower, spend_upper, spend_method,
                  count_forecast, avg_amount_forecast,
                  hist_avg_spend, last_month_spend,
                  spend_pct_change_vs_hist, spend_direction, spend_vs_last_month_pct,
                  confidence, confidence_note, trend_summary,
                  top_category_forecasts
           FROM forecasts
           WHERE user_id = :uid
           ORDER BY forecast_month DESC
           LIMIT 1""",
        params={"uid": user_id},
    )

    if df.empty:
        return {}

    row = df.iloc[0].to_dict()

    raw = row.get("top_category_forecasts")
    if isinstance(raw, str):
        try:
            row["top_category_forecasts"] = json.loads(raw)
        except json.JSONDecodeError:
            row["top_category_forecasts"] = {}

    return row

def get_anomalies(user_id: str) -> dict:
    df = read_query(
        """SELECT user_id, is_anomaly, severity, anomaly_score,
                  iso_score, lof_score,
                  vel_1d, vel_7d, vel_30d, count_30d, avg_amt_30d,
                  days_since_last, merchant_diversity, new_merchant_count,
                  task_segment, top_category, top_merchant,
                  primary_spending_trend
           FROM anomaly_scores
           WHERE user_id = :uid""",
        params={"uid": user_id},
    )

    if df.empty:
        return {}

    return df.iloc[0].to_dict()

def get_flagged_transactions(user_id: str, limit: int = 5) -> list[dict]:
    df = read_query(
        """SELECT date, merchant_name, category_id, amount, currency_code,
                  is_new_merchant, user_avg_amount, deviation_ratio,
                  spend_anomaly_type
           FROM transactions_enriched
           WHERE user_id = :uid
             AND spend_anomaly_type IS NOT NULL
             AND spend_anomaly_type != 'Normal'
           ORDER BY date DESC
           LIMIT :limit""",
        params={"uid": user_id, "limit": limit},
    )

    if df.empty:
        return []

    return df.to_dict("records")