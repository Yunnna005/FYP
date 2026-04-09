import sys
import time
import logging
import argparse
import traceback

from models.db.dbconfig import DB_AVAILABLE, CSV_DIR
from models.python.features  import run_feature_engineering
from models.python.anomaly_detection_model import run_anomaly_detection
from models.python.recommendation_model import run_recommendation_engine
from models.python.forecasting_model import run_sequential_forecasting
from analytics.user_stats import run_user_stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

STEPS = [
    ("User Stats", run_user_stats),
    ("Feature Engineering", run_feature_engineering),
    ("Anomaly Detection", run_anomaly_detection),
    ("Recommendation Engine", run_recommendation_engine),
    ("Sequential Forecasting", run_sequential_forecasting),
]

REQUIRED_CSVS = ["users.csv", "accounts.csv", "transactions.csv"]

def check_data_sources():
    if DB_AVAILABLE:
        return
    missing = [f for f in REQUIRED_CSVS if not (CSV_DIR / f).exists()]
    if missing:
        log.error(f"DB unavailable and missing CSV files in {CSV_DIR}: {missing}")
        sys.exit(1)


def run_pipeline(user_id=None):
    check_data_sources()
    label = f"user {user_id}" if user_id else "ALL users"
    start = time.time()
    log.info(f"Pipeline starting — {label}")

    results = {}
    for name, fn in STEPS:
        t = time.time()
        try:
            fn(user_id=user_id)
            results[name] = f"OK  {round(time.time()-t, 1)}s"
        except Exception as e:
            results[name] = f"FAIL  {e}"
            log.error(f"{name} failed:\n{traceback.format_exc()}")

    log.info(f"Pipeline done in {round(time.time()-start, 1)}s total")
    for name, status in results.items():
        log.info(f"  [{status}]  {name}")
    return results

def add_new_user(user_id: int):
    log.info(f"New user {user_id} — starting pipeline...")
    return run_pipeline(user_id=user_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Finance AI Pipeline")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--full", action="store_true", help="Process all users")
    group.add_argument("--user", type=int, help="Process one user by ID")
    args = parser.parse_args()

    if args.user:
        run_pipeline(user_id=args.user)
    else:
        run_pipeline(user_id=None)
