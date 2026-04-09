import json
import logging
import pandas as pd
import sqlalchemy
from models.db.dbconfig import (
    DB_AVAILABLE,
    CSV_DIR,
    read_data,
    write_data,
    get_engine,
)

log = logging.getLogger(__name__)

ALL_TIME_TABLE = "user_all_time_stats"
MONTHLY_TABLE = "user_monthly_stats"

ALL_TIME_KEYS = ["user_id", "account_id"]
ALL_TIME_VALUES = [
    "total_transactions",
    "avg_transactions_value",
    "largest_transaction",
]

MONTHLY_KEYS = ["user_id", "account_id", "month_start_date"]
MONTHLY_VALUES = [
    "total_amount",
    "total_transactions",
    "total_spent",
    "total_received",
    "avg_transaction",
    "largest",
    "largest_abs",
    "spending_by_category",
]


def run_user_stats(user_id=None):
    transactions = read_data("transactions")
    accounts = read_data("accounts")
    users = read_data("users")

    if transactions.empty or accounts.empty or users.empty:
        log.warning("No transactions, accounts, or users data — skipping user stats")
        return

    accounts = accounts.merge(
        users[["user_id", "account_id"]],
        on="account_id",
        how="inner",
    )

    if user_id is not None:
        accounts = accounts[accounts['user_id'].astype(str) == str(user_id)]
        if accounts.empty:
            log.warning(f"No accounts found for user {user_id}")
            return

    transactions['date'] = pd.to_datetime(transactions['date'])
    transactions['month'] = transactions['date'].dt.strftime('%Y-%m')

    all_time_rows = []
    monthly_rows = []

    for _, account in accounts.iterrows():
        uid = str(account['user_id'])
        account_id = str(account['account_id'])
        account_transactions = transactions[
            transactions['account_id'].astype(str) == account_id
        ]
        if account_transactions.empty:
            continue

        all_amounts = account_transactions['amount']
        all_time_rows.append({
            "user_id": uid,
            "account_id": account_id,
            "total_transactions": int(len(all_amounts)),
            "avg_transactions_value": round(float(all_amounts.mean()), 2),
            "largest_transaction": round(float(all_amounts.max()), 2),
        })

        for month, group in account_transactions.groupby('month'):
            amounts = group['amount']
            total = round(float(amounts.sum()), 2)
            count = int(len(amounts))
            monthly_rows.append({
                "user_id": uid,
                "account_id": account_id,
                "month_start_date": f"{month}-01",
                "total_amount": total,
                "total_transactions": count,
                "total_spent": round(float(amounts[amounts < 0].sum()), 2),
                "total_received": round(float(amounts[amounts > 0].sum()), 2),
                "avg_transaction": round(total / count, 2),
                "largest": round(float(amounts.max()), 2),
                "largest_abs": round(
                    float(amounts.loc[amounts.abs().idxmax()]), 2
                ),
                "spending_by_category": json.dumps(
                    group['category_id'].value_counts().to_dict()
                ),
            })

    new_all_time = pd.DataFrame(all_time_rows)
    new_monthly = pd.DataFrame(monthly_rows)

    if new_all_time.empty and new_monthly.empty:
        log.warning("No stats generated")
        return

    all_time_result = _sync_table(
        new_df=new_all_time,
        table=ALL_TIME_TABLE,
        key_cols=ALL_TIME_KEYS,
        value_cols=ALL_TIME_VALUES,
    )
    monthly_result = _sync_table(
        new_df=new_monthly,
        table=MONTHLY_TABLE,
        key_cols=MONTHLY_KEYS,
        value_cols=MONTHLY_VALUES,
    )

    log.info(
        f"All-time stats — inserted: {all_time_result['inserted']}, "
        f"updated: {all_time_result['updated']}, "
        f"unchanged: {all_time_result['unchanged']}"
    )
    log.info(
        f"Monthly stats — inserted: {monthly_result['inserted']}, "
        f"updated: {monthly_result['updated']}, "
        f"unchanged: {monthly_result['unchanged']}"
    )


def _sync_table(new_df, table, key_cols, value_cols):
    """
    Compare new_df against what's already in the table.
    Insert rows that don't exist, update rows whose values changed,
    skip rows that match exactly.
    """
    result = {"inserted": 0, "updated": 0, "unchanged": 0}

    if new_df.empty:
        return result

    existing_df = _load_existing(table)

    if existing_df.empty:
        _insert_rows(new_df, table)
        result["inserted"] = len(new_df)
        return result

    for col in key_cols:
        new_df[col] = new_df[col].astype(str)
        existing_df[col] = existing_df[col].astype(str)

    existing_indexed = existing_df.set_index(key_cols)

    to_insert = []
    to_update = []

    for _, new_row in new_df.iterrows():
        key = tuple(new_row[col] for col in key_cols)

        if key not in existing_indexed.index:
            to_insert.append(new_row)
            continue

        existing_row = existing_indexed.loc[key]
        if isinstance(existing_row, pd.DataFrame):
            existing_row = existing_row.iloc[0]

        if _rows_match(new_row, existing_row, value_cols):
            result["unchanged"] += 1
        else:
            to_update.append(new_row)

    if to_insert:
        _insert_rows(pd.DataFrame(to_insert), table)
        result["inserted"] = len(to_insert)

    if to_update:
        _update_rows(pd.DataFrame(to_update), table, key_cols, value_cols)
        result["updated"] = len(to_update)

    return result


def _load_existing(table):
    """Load current contents of a stats table. Returns empty DF if missing."""
    try:
        df = read_data(table)
        return df if not df.empty else pd.DataFrame()
    except Exception as e:
        log.info(f"No existing {table} ({e})")
        return pd.DataFrame()


def _rows_match(row_a, row_b, value_cols):
    """Return True if two rows have identical values across value_cols."""
    for col in value_cols:
        a, b = row_a[col], row_b[col]

        if col == "spending_by_category":
            if _normalize_json(a) != _normalize_json(b):
                return False
            continue

        try:
            if round(float(a), 2) != round(float(b), 2):
                return False
        except (TypeError, ValueError):
            if str(a) != str(b):
                return False

    return True


def _normalize_json(value):
    """Parse a JSON string/dict into a stable canonical form for comparison."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    try:
        return json.dumps(json.loads(value), sort_keys=True)
    except (TypeError, ValueError):
        return str(value)


def _insert_rows(df, table):
    """Insert new rows via the existing write_data helper."""
    write_data(df, table, if_exists="append", index=False)


def _update_rows(df, table, key_cols, value_cols):
    """Update rows in place, matching on key_cols."""
    if DB_AVAILABLE:
        _update_rows_db(df, table, key_cols, value_cols)
    else:
        _update_rows_csv(df, table, key_cols, value_cols)


def _update_rows_db(df, table, key_cols, value_cols):
    engine = get_engine()
    set_clause = ", ".join(f"{c} = :{c}" for c in value_cols)
    where_clause = " AND ".join(f"{c} = :{c}" for c in key_cols)
    sql = sqlalchemy.text(
        f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    )
    with engine.begin() as conn:
        for _, row in df.iterrows():
            params = {c: row[c] for c in set(value_cols) | set(key_cols)}
            conn.execute(sql, params)


def _update_rows_csv(df, table, key_cols, value_cols):
    path = CSV_DIR / f"{table}.csv"
    if not path.exists():
        write_data(df, table, if_exists="append", index=False)
        return

    existing = pd.read_csv(path)
    for col in key_cols:
        existing[col] = existing[col].astype(str)
        df[col] = df[col].astype(str)

    existing_indexed = existing.set_index(key_cols)
    df_indexed = df.set_index(key_cols)[value_cols]
    existing_indexed.update(df_indexed)
    merged = existing_indexed.reset_index()
    merged.to_csv(path, index=False)