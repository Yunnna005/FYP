import pool from "../backend/db_connection.js";

export async function getTransactionsByOwner(email, phone) {
  try {
    const query = `
      SELECT t.*
      FROM users u
      JOIN accounts a ON u.user_id = a.user_id
      JOIN transactions t ON a.account_id = t.account_id
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