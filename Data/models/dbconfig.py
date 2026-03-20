import os
import pandas as pd
from sqlalchemy import create_engine, text
import psycopg2

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "finance_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "admin"),
}

DATABASE_URL = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)


def get_engine():
    return create_engine(DATABASE_URL)


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def read_table(table: str, engine=None) -> pd.DataFrame:
    eng = engine or get_engine()
    return pd.read_sql(f"SELECT * FROM {table}", eng)


def read_query(query: str, engine=None, params=None) -> pd.DataFrame:
    eng = engine or get_engine()
    return pd.read_sql(query, eng, params=params)


def write_table(df: pd.DataFrame, table: str, if_exists="replace", engine=None):
    eng = engine or get_engine()
    df.to_sql(table, eng, if_exists=if_exists, index=True, method="multi", chunksize=500)
