from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate():
    # Force use of internal docker service name if running inside container, but we are running from host
    # So we need to use localhost and port 5432 which is mapped in docker-compose
    # The config has: postgresql://postgres:postgres@localhost/taskmanagement
    
    print(f"Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("Checking for missing columns...")
        
        def add_column_if_missing(table, column, type_def):
            try:
                # SQLAlchemy text() for raw SQL
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}"))
                conn.commit()
                print(f"Added '{column}' column to '{table}'.")
            except Exception as e:
                conn.rollback()
                print(f"Skipping '{column}' in '{table}' (might exist or error): {e}")

        add_column_if_missing("tasks", "rating", "INTEGER NULL")
        add_column_if_missing("tasks", "rating_comment", "TEXT NULL")
        add_column_if_missing("tasks", "completed_at", "TIMESTAMP WITH TIME ZONE NULL")
        add_column_if_missing("notes", "reminder_at", "TIMESTAMP WITH TIME ZONE NULL")
        
        print("Migration process finished.")

if __name__ == "__main__":
    migrate()
