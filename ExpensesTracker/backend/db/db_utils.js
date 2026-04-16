import pool from "./db_connection.js";

export async function getTransactionsByOwner(email, phone) {
  try {
    const query = `
      SELECT t.category_id, t.date, t.description, t.amount, t.merchant_name, t.pending, t.currency_code
      FROM users u
      JOIN transactions t ON u.account_id = t.account_id
      WHERE u.email = $1
      AND u.phone_number = $2
      ORDER BY t.date DESC;`;

    const { rows } = await pool.query(query, [email, phone]);
    return rows;
  } catch (error) {
    console.error("Database query error:", error.message);
    throw new Error("Failed to fetch transactions");
  }
}

export async function getTransactionsByAccountId(account_id) {
  try {
    const query = `
      SELECT category_id, date, description, amount, merchant_name, pending, currency_code
      FROM transactions
      WHERE account_id = $1
      ORDER BY date DESC;`;

    const { rows } = await pool.query(query, [account_id]);
    return rows;
  } catch (error) {
    console.error("Database query error:", error.message);
    throw new Error("Failed to fetch transactions");
  }
}

export async function getUserByEmailAndPhone(email, phone) {
  try {
    const query = `
      SELECT user_id
      FROM users
      WHERE email = $1
      AND phone_number = $2`;

    const { rows } = await pool.query(query, [email, phone]);
    return rows[0] || null;
  } catch (error) {
    console.error("Database query error:", error.message);
    throw new Error("Failed to fetch userID");
  }
}

export async function getMonthlyStatsByUserId(user_id, account_id) {
  try {
    const query = `
      SELECT * 
      FROM user_monthly_stats 
      WHERE user_id = $1 AND account_id = $2
      ORDER BY month_start_date DESC;`;

    const { rows } = await pool.query(query, [user_id, account_id]);
    return rows;
  } catch (error) {
    console.error("Database query error:", error.message);
    throw new Error("Failed to fetch monthly stats");
  }
}

export async function getUserById(user_id) {
  try {
    const query = `
      SELECT u.user_id, u.email, u.phone_number, u.full_name, u.account_id,
             a.name AS account_name, a.balances_current, a.currency_code
      FROM users u
      LEFT JOIN accounts a ON a.account_id = u.account_id
      WHERE u.user_id = $1`;
    const { rows } = await pool.query(query, [user_id]);
    return rows[0] || null;
  } catch (error) {
    console.error("Database query error:", error.message);
    throw new Error("Failed to fetch user");
  }
}

export async function deleteUserData(user_id) {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");

    const userRes = await client.query(
      "SELECT account_id FROM users WHERE user_id = $1",
      [user_id]
    );
    if (userRes.rows.length === 0) {
      await client.query("ROLLBACK");
      return false;
    }
    const accountId = userRes.rows[0].account_id;

    await client.query("DELETE FROM transactions WHERE account_id = $1", [accountId]);
    await client.query("DELETE FROM transactions_enriched WHERE user_id = $1", [user_id]);
    await client.query("DELETE FROM fm_encoded WHERE user_id = $1", [user_id]);
    await client.query("DELETE FROM anomaly_scores WHERE user_id = $1", [user_id]);
    await client.query("DELETE FROM recommendations WHERE user_id = $1", [user_id]);
    await client.query("DELETE FROM user_monthly_stats WHERE user_id = $1", [user_id]);
    await client.query("DELETE FROM user_all_time_stats WHERE user_id = $1", [user_id]);
    await client.query("DELETE FROM users WHERE user_id = $1", [user_id]);
    await client.query("DELETE FROM accounts WHERE account_id = $1", [accountId]);

    await client.query("COMMIT");
    return true;
  } catch (err) {
    await client.query("ROLLBACK");
    console.error("Delete user data error:", err.message);
    throw new Error("Failed to delete user data");
  } finally {
    client.release();
  }
}