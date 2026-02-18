import time
from sqlalchemy.exc import OperationalError
from app.db.base import Base, engine
from app.models.task_tracking import GitCommit # Ensure it's imported for metadata
from app.models.core import User # Ensure core models are also in metadata
from app.models.notes import Note # Ensure notes models are in metadata
from app.models.integrations import GitHubIntegration # Ensure integration models are in metadata

def migrate_columns():
    print("Checking for missing columns...")
    from app.db.base import SessionLocal
    import sqlalchemy
    from sqlalchemy import text
    
    db = SessionLocal()
    try:
        # Table -> [Columns to check/add]
        # Column format: (name, type, default_val)
        migrations = {
            "organizations": [
                ("telegram_bot_token", "VARCHAR", "NULL"),
                ("telegram_chat_id", "VARCHAR", "NULL"),
                ("telegram_enabled", "BOOLEAN", "FALSE"),
                ("email_notifications_enabled", "BOOLEAN", "TRUE"),
                ("emission_email_address", "VARCHAR", "NULL"),
                ("bcc_recipients", "BOOLEAN", "FALSE"),
                ("plain_text_mail", "BOOLEAN", "FALSE"),
                ("address_user_in_emails_with", "VARCHAR", "'full_name'"),
                ("emails_header", "TEXT", "NULL"),
                ("emails_footer", "TEXT", "NULL"),
                ("notification_template", "TEXT", "NULL"),
                ("email_delivery_method", "VARCHAR", "'smtp'"),
                ("smtp_helo_domain", "VARCHAR", "NULL"),
                ("smtp_authentication", "VARCHAR", "'login'"),
                ("smtp_use_starttls", "BOOLEAN", "TRUE"),
                ("smtp_use_ssl", "BOOLEAN", "FALSE"),
                ("system_page_title", "VARCHAR", "'Task Management System'"),
                ("theme_mode", "VARCHAR", "'system'"),
                ("border_radius", "VARCHAR", "'0.75rem'"),
                ("font_family", "VARCHAR", "'Inter, sans-serif'"),
                ("font_size_base", "VARCHAR", "'16px'"),
                ("industry", "VARCHAR", "NULL"),
                ("address", "VARCHAR", "NULL"),
                ("timezone", "VARCHAR", "'UTC'"),
                ("default_language", "VARCHAR", "'en'"),
                ("contact_phone", "VARCHAR", "NULL"),
                ("contact_email", "VARCHAR", "NULL"),
                ("show_dashboard_clock", "BOOLEAN", "TRUE"),
                ("show_dashboard_map", "BOOLEAN", "FALSE"),
                ("show_dashboard_stats", "BOOLEAN", "TRUE"),
                ("show_dashboard_tasks", "BOOLEAN", "TRUE"),
                ("dashboard_layout", "VARCHAR", "'clock,stats,tasks,map'"),
                ("dashboard_refresh_rate", "INTEGER", "30"),
                ("dashboard_clock_type", "VARCHAR", "'analog'"),
                ("dashboard_metrics_config", "VARCHAR", "'tasks,active,overdue,problems'"),
                ("dashboard_compact_mode", "BOOLEAN", "FALSE")
            ],
            "notes": [
                ("reminder_at", "TIMESTAMP WITH TIME ZONE", "NULL"),
                ("reminder_sent", "BOOLEAN", "FALSE")
            ],
            "tasks": [
                ("is_archived", "BOOLEAN", "FALSE"),
                ("due_reminder_sent", "BOOLEAN", "FALSE")
            ],
            "users": [
                ("profile_photo_url", "VARCHAR", "NULL"),
                ("username", "VARCHAR", "NULL"),
                ("job_title", "VARCHAR", "NULL"),
                ("bio", "VARCHAR", "NULL"),
                ("phone_number", "VARCHAR", "NULL"),
                ("timezone", "VARCHAR", "'UTC'"),
                ("language", "VARCHAR", "'en'"),
                ("auth_method", "VARCHAR", "'email_password'"),
                ("task_view_preference", "VARCHAR", "'board'"),
                ("default_task_sort", "VARCHAR", "'due_date'"),
                ("start_of_week", "VARCHAR", "'monday'"),
                ("date_format", "VARCHAR", "'YYYY-MM-DD'"),
                ("time_format", "VARCHAR", "'24h'"),
                ("email_notifications", "TEXT", "'{\"task_assigned\":true,\"status_changes\":true,\"mentions\":true,\"daily_summary\":false,\"weekly_summary\":false}'"),
                ("in_app_notifications", "TEXT", "'{\"task_assigned\":true,\"status_changes\":true,\"mentions\":true}'"),
                ("dnd_schedule", "TEXT", "NULL"),
                ("two_factor_enabled", "BOOLEAN", "FALSE"),
                ("two_factor_secret", "VARCHAR", "NULL"),
                ("last_login", "TIMESTAMP WITH TIME ZONE", "NULL")
            ],
            "roles": [
                ("permissions_json", "TEXT", "NULL"),
                ("is_standard", "BOOLEAN", "FALSE")
            ],
            "invitations": [
                ("branch_ids", "INTEGER[]", "NULL"),
                ("dept_ids", "INTEGER[]", "NULL")
            ]
        }

        for table, columns in migrations.items():
            for col_name, col_type, default_val in columns:
                # Use introspection to check if column exists
                check_sql = text(f"SELECT count(*) FROM information_schema.columns WHERE table_name='{table}' AND column_name='{col_name}'")
                res = db.execute(check_sql).fetchone()
                
                if res[0] == 0:
                    print(f"  Adding column {table}.{col_name}...")
                    alter_sql = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"
                    if default_val != "NULL":
                        alter_sql += f" DEFAULT {default_val}"
                    db.execute(text(alter_sql))
        
        db.commit()
        print("Migration check complete.")
    except Exception as e:
        print(f"Migration error: {e}")
        db.rollback()
    finally:
        db.close()

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
    
    # Run manual column migrations
    migrate_columns()
    
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
