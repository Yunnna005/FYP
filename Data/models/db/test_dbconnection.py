import os
from pathlib import Path
from dotenv import load_dotenv
import sqlalchemy

load_dotenv(Path(__file__).parent / ".env")

DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

def test_db_connection():
    engine = sqlalchemy.create_engine(DB_URL)
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT 1"))
        assert result.scalar() == 1
    print(f"[OK] Connected to {os.getenv('DB_NAME')} on {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")

if __name__ == "__main__":
    test_db_connection()
