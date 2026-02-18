import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

# Database connection parameters from environment variables
DB_NAME = os.getenv("POSTGRES_DB", "taskmanagement")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_SERVER", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

def migrate():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        print("Adding branch_ids and dept_ids to invitations table...")
        
        # Add columns to invitations table
        cursor.execute("ALTER TABLE invitations ADD COLUMN IF NOT EXISTS branch_ids INTEGER[] DEFAULT '{}';")
        cursor.execute("ALTER TABLE invitations ADD COLUMN IF NOT EXISTS dept_ids INTEGER[] DEFAULT '{}';")

        print("Migration completed successfully!")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
