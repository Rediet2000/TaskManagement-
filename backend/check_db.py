from sqlalchemy import create_engine, inspect
from app.core.config import settings

def check_schema():
    print(f"Connecting to database at {settings.DATABASE_URL}...")
    try:
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        columns = inspector.get_columns('tasks')
        print("Columns in 'tasks' table:")
        found_rating = False
        for column in columns:
            print(f"- {column['name']} ({column['type']})")
            if column['name'] == 'rating':
                found_rating = True
        
        if found_rating:
            print("\nSUCCESS: 'rating' column found.")
        else:
            print("\nFAILURE: 'rating' column NOT found.")
            
    except Exception as e:
        print(f"Error inspecting database: {e}")

if __name__ == "__main__":
    check_schema()
