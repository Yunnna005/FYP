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
      WHERE u.email = $1
      AND u.phone_number = $2`;

    const { rows } = await pool.query(query, [email, phone]);
    return rows;
  } catch (error) {
    console.error("Database query error:", error.message);
    throw new Error("Failed to fetch userID");
  }
}