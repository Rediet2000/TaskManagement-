import time
from sqlalchemy.exc import OperationalError
from app.db.base import Base, engine
from app.models.task_tracking import GitCommit # Ensure it's imported for metadata
from app.models.core import User # Ensure core models are also in metadata
from app.models.notes import Note # Ensure notes models are in metadata

def ensure_schema():
    print("Waiting for database to be ready...")
    retries = 10
    while retries > 0:
        try:
            # Try to connect
            with engine.connect() as conn:
                pass
            print("Database is ready.")
            break
        except OperationalError:
            retries -= 1
            print(f"Database not ready. Retrying in 2 seconds... ({retries} retries left)")
            time.sleep(2)
    
    if retries == 0:
        print("Could not connect to database. Exiting.")
        return

    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    print("Schema sync complete.")
    
    # Auto-seed permissions if running on fresh DB
    try:
        from scripts.init_permissions import init_permissions
        print("Seeding permissions...")
        init_permissions()
    except Exception as e:
        print(f"Warning: Could not seed permissions: {e}")

if __name__ == "__main__":
    ensure_schema()
