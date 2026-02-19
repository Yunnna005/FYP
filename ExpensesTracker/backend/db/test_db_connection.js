import pool from './db_connection.js';

async function testConnection() {
  try {
    const result = await pool.query('SELECT NOW()');
    console.log('DB connected successfully!');
    console.log('Server time:', result.rows[0]);
  } catch (error) {
    console.error('DB connection failed:', error);
  } finally {
    await pool.end();
  }
}

testConnection();
