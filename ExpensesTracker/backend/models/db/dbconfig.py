import os
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
import sqlalchemy
import psycopg2

load_dotenv(Path(__file__).parent / ".env")
ROOT_DIR = Path(__file__).parent

CSV_DIR = Path(__file__).parents[2] / "Final"
CSV_DIR.mkdir(parents=True, exist_ok=True)


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "none"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "admin"),
}

DATABASE_URL = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

def check_db():
    try:
        engine = sqlalchemy.create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        print("[db] PostgreSQL connected")
        return True
    except Exception as e:
        print(f"[db] PostgreSQL unavailable ({e})")
        return False

DB_AVAILABLE = check_db()


def get_engine():
    return sqlalchemy.create_engine(DATABASE_URL)


def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def read_query(query: str, engine=None, params=None) -> pd.DataFrame:
    eng = engine or get_engine()
    sql = sqlalchemy.text(query) if params else query
    return pd.read_sql(sql, eng, params=params)

def read_data(table: str, query: str = None, engine=None) -> pd.DataFrame:
    if DB_AVAILABLE:
        eng = engine or get_engine()
        sql = query or f"SELECT * FROM {table}"
        return pd.read_sql(sql, eng)
    else:
        path = CSV_DIR / f"{table}.csv"
        if not path.exists():
            print(f"[db] CSV not found: {path} — returning empty DataFrame")
            return pd.DataFrame()
        df = pd.read_csv(path)
        return df

def write_data(df: pd.DataFrame, table: str, if_exists: str = "replace", index: bool = True, engine=None):
    if DB_AVAILABLE:
        eng = engine or get_engine()
        df.to_sql(table, eng, if_exists=if_exists, index=index, method="multi", chunksize=500)
    else:
        path = CSV_DIR / f"{table}.csv"
        if if_exists == 'append' and path.exists():
            existing = pd.read_csv(path)
            df_reset = df.reset_index() if index else df
            combined = pd.concat([existing, df_reset], ignore_index=True)
            combined.to_csv(path, index=False)
        else:
            df.to_csv(CSV_DIR / f"{table}.csv", index=index)
        print(f"[db] Saved → {CSV_DIR / f'{table}.csv'}")

def write_table(df: pd.DataFrame, table: str, if_exists: str = "replace", engine=None):
    write_data(df, table, if_exists=if_exists, index=True, engine=engine)


def get_user_accounts(user_id: str, engine=None) -> dict:
    empty = {
        "user_id": user_id,
        "account_ids": [],
        "primary_account_id": None,
        "account_count": 0,
        "accounts": [],
    }

    if DB_AVAILABLE:
        eng = engine or get_engine()
        df  = read_query(
            "SELECT a.account_id, a.name, a.type, a.mask, "
            "a.balances_current, a.balances_available, a.currency_code "
            "FROM accounts a "
            "JOIN users u ON u.account_id = a.account_id "
            f"WHERE u.user_id = {user_id} "
            "ORDER BY a.account_id",
            eng
        )
    else:
        users_path = CSV_DIR / "users.csv"
        accounts_path = CSV_DIR / "accounts.csv"

        if not users_path.exists() or not accounts_path.exists():
            return empty

        users_df = pd.read_csv(users_path)
        accounts_df = pd.read_csv(accounts_path)

        user_row = users_df[users_df["user_id"] == user_id]
        if user_row.empty:
            return empty

        acc_ids = user_row["account_id"].tolist()
        df = accounts_df[accounts_df["account_id"].isin(acc_ids)]

    if df.empty:
        return empty

    return {
        "user_id": user_id,
        "account_ids": df["account_id"].tolist(),
        "primary_account_id": int(df["account_id"].iloc[0]),
        "account_count": len(df),
        "accounts": df.to_dict("records"),
    }