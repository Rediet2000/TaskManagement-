from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base

# Import all models to ensure they are registered in Base.metadata
from app.models import core, task_tracking, notes, integrations, agile

def migrate():
    print(f"Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)
    
    print("Ensuring all tables exist...")
    Base.metadata.create_all(bind=engine)
    
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

        # --- Organizations Table ---
        add_column_if_missing("organizations", "telegram_bot_token", "VARCHAR NULL")
        add_column_if_missing("organizations", "telegram_chat_id", "VARCHAR NULL")
        add_column_if_missing("organizations", "telegram_enabled", "BOOLEAN DEFAULT FALSE")
        add_column_if_missing("organizations", "email_notifications_enabled", "BOOLEAN DEFAULT TRUE")
        add_column_if_missing("organizations", "system_page_title", "VARCHAR DEFAULT 'Task Management System'")
        add_column_if_missing("organizations", "theme_mode", "VARCHAR DEFAULT 'system'")
        add_column_if_missing("organizations", "industry", "VARCHAR NULL")
        add_column_if_missing("organizations", "address", "VARCHAR NULL")
        add_column_if_missing("organizations", "timezone", "VARCHAR DEFAULT 'UTC'")
        add_column_if_missing("organizations", "default_language", "VARCHAR DEFAULT 'en'")
        add_column_if_missing("organizations", "contact_phone", "VARCHAR NULL")
        add_column_if_missing("organizations", "contact_email", "VARCHAR NULL")
        add_column_if_missing("organizations", "show_dashboard_clock", "BOOLEAN DEFAULT TRUE")
        add_column_if_missing("organizations", "show_dashboard_map", "BOOLEAN DEFAULT FALSE")
        add_column_if_missing("organizations", "show_dashboard_stats", "BOOLEAN DEFAULT TRUE")
        add_column_if_missing("organizations", "show_dashboard_tasks", "BOOLEAN DEFAULT TRUE")
        add_column_if_missing("organizations", "dashboard_layout", "VARCHAR DEFAULT 'clock,stats,tasks,map'")
        add_column_if_missing("organizations", "dashboard_refresh_rate", "INTEGER DEFAULT 30")
        add_column_if_missing("organizations", "dashboard_clock_type", "VARCHAR DEFAULT 'analog'")
        add_column_if_missing("organizations", "dashboard_metrics_config", "VARCHAR DEFAULT 'tasks,active,overdue,problems'")
        add_column_if_missing("organizations", "dashboard_compact_mode", "BOOLEAN DEFAULT FALSE")

        # --- Users Table ---
        add_column_if_missing("users", "profile_photo_url", "VARCHAR NULL")
        add_column_if_missing("users", "username", "VARCHAR UNIQUE NULL")
        add_column_if_missing("users", "job_title", "VARCHAR NULL")
        add_column_if_missing("users", "bio", "VARCHAR NULL")
        add_column_if_missing("users", "phone_number", "VARCHAR NULL")
        add_column_if_missing("users", "timezone", "VARCHAR DEFAULT 'UTC'")
        add_column_if_missing("users", "language", "VARCHAR DEFAULT 'en'")
        add_column_if_missing("users", "auth_method", "VARCHAR DEFAULT 'email_password'")
        add_column_if_missing("users", "task_view_preference", "VARCHAR DEFAULT 'board'")
        add_column_if_missing("users", "default_task_sort", "VARCHAR DEFAULT 'due_date'")
        add_column_if_missing("users", "start_of_week", "VARCHAR DEFAULT 'monday'")
        add_column_if_missing("users", "date_format", "VARCHAR DEFAULT 'YYYY-MM-DD'")
        add_column_if_missing("users", "time_format", "VARCHAR DEFAULT '24h'")
        add_column_if_missing("users", "email_notifications", "VARCHAR DEFAULT '{\"task_assigned\":true,\"status_changes\":true,\"mentions\":true,\"daily_summary\":false,\"weekly_summary\":false}'")
        add_column_if_missing("users", "in_app_notifications", "VARCHAR DEFAULT '{\"task_assigned\":true,\"status_changes\":true,\"mentions\":true}'")
        add_column_if_missing("users", "dnd_schedule", "VARCHAR NULL")
        add_column_if_missing("users", "two_factor_enabled", "BOOLEAN DEFAULT FALSE")
        add_column_if_missing("users", "two_factor_secret", "VARCHAR NULL")
        add_column_if_missing("users", "last_login", "TIMESTAMP WITH TIME ZONE NULL")

        # --- Tasks Table ---
        add_column_if_missing("tasks", "rating", "INTEGER NULL")
        add_column_if_missing("tasks", "rating_comment", "TEXT NULL")
        add_column_if_missing("tasks", "completed_at", "TIMESTAMP WITH TIME ZONE NULL")
        add_column_if_missing("tasks", "assigner_id", "INTEGER NULL REFERENCES users(id)")
        add_column_if_missing("tasks", "accountable_id", "INTEGER NULL REFERENCES users(id)")
        add_column_if_missing("tasks", "board_id", "INTEGER NULL REFERENCES boards(id)")
        add_column_if_missing("tasks", "board_column_id", "INTEGER NULL REFERENCES board_columns(id)")
        add_column_if_missing("tasks", "checklist", "JSONB NOT NULL DEFAULT '[]'::jsonb")
        add_column_if_missing("tasks", "is_archived", "BOOLEAN DEFAULT FALSE")

        # --- Sprints Table ---
        add_column_if_missing("sprints", "board_id", "INTEGER NULL REFERENCES boards(id)")

        # --- Notes Table ---
        add_column_if_missing("notes", "reminder_at", "TIMESTAMP WITH TIME ZONE NULL")

        # --- Audit Logs Table ---
        add_column_if_missing("audit_logs", "org_id", "INTEGER NULL REFERENCES organizations(id)")
        
        print("Migration process finished.")

if __name__ == "__main__":
    migrate()
