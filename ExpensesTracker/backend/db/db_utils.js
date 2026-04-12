import pool from "./db_connection.js";

export async function getTransactionsByOwner(email, phone) {
  try {
    const query = `
      SELECT t.*
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