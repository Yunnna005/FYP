import logging
from analytics.user_stats import run_user_stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)

if __name__ == "__main__":
    print("=== First run (should INSERT everything) ===")
    run_user_stats()

    print("\n=== Second run (should show all UNCHANGED) ===")
    run_user_stats()