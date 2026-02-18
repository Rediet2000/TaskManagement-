from sqlalchemy import text
from app.db.base import engine

def migrate():
    with engine.connect() as conn:
        print("Migrating database for advanced features (Fixed)...")
        
        # Organizations theme columns
        try:
            conn.execute(text("ALTER TABLE organizations ADD COLUMN border_radius VARCHAR DEFAULT '0.75rem'"))
            conn.commit()
            print("Added border_radius to organizations.")
        except Exception as e:
            conn.rollback()
            print(f"border_radius error: {e}")

        try:
            # Fixing font_family escaping
            conn.execute(text("ALTER TABLE organizations ADD COLUMN font_family VARCHAR DEFAULT '''Inter'', sans-serif'"))
            conn.commit()
            print("Added font_family to organizations.")
        except Exception as e:
            conn.rollback()
            print(f"font_family error: {e}")

        try:
            conn.execute(text("ALTER TABLE organizations ADD COLUMN font_size_base VARCHAR DEFAULT '16px'"))
            conn.commit()
            print("Added font_size_base to organizations.")
        except Exception as e:
            conn.rollback()
            print(f"font_size_base error: {e}")

        # Roles columns
        try:
            conn.execute(text("ALTER TABLE roles ADD COLUMN permissions_json TEXT"))
            conn.execute(text("ALTER TABLE roles ADD COLUMN is_standard BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("Added permissions_json and is_standard to roles.")
        except Exception as e:
            conn.rollback()
            print(f"Roles columns error: {e}")

        # User Branches table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_branches (
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    branch_id INTEGER REFERENCES branches(id) ON DELETE CASCADE,
                    PRIMARY KEY (user_id, branch_id)
                )
            """))
            conn.commit()
            print("Created user_branches table.")
        except Exception as e:
            conn.rollback()
            print(f"user_branches table error: {e}")

        # User Departments table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_departments (
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    dept_id INTEGER REFERENCES departments(id) ON DELETE CASCADE,
                    PRIMARY KEY (user_id, dept_id)
                )
            """))
            conn.commit()
            print("Created user_departments table.")
        except Exception as e:
            conn.rollback()
            print(f"user_departments table error: {e}")

        print("Migration process finished.")

if __name__ == "__main__":
    migrate()
