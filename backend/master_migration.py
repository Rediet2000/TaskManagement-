import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    host = "localhost"
    dbname = "taskmanagement"
    user = "postgres"
    password = "postgres"
    port = "5432"

    try:
        conn = psycopg2.connect(
            host=host,
            database=dbname,
            user=user,
            password=password,
            port=port
        )
        cur = conn.cursor()
        
        # Table -> [Columns to check/add]
        # Column format: (name, type, default_value_or_none)
        migrations = {
            "organizations": [
                ("telegram_bot_token", "VARCHAR", None),
                ("telegram_chat_id", "VARCHAR", None),
                ("telegram_enabled", "BOOLEAN", "FALSE"),
                ("email_notifications_enabled", "BOOLEAN", "TRUE"),
                ("emission_email_address", "VARCHAR", None),
                ("bcc_recipients", "BOOLEAN", "FALSE"),
                ("plain_text_mail", "BOOLEAN", "FALSE"),
                ("address_user_in_emails_with", "VARCHAR", "'full_name'"),
                ("emails_header", "TEXT", None),
                ("emails_footer", "TEXT", None),
                ("notification_template", "TEXT", None),
                ("email_delivery_method", "VARCHAR", "'smtp'"),
                ("smtp_helo_domain", "VARCHAR", None),
                ("smtp_authentication", "VARCHAR", "'login'"),
                ("smtp_use_starttls", "BOOLEAN", "TRUE"),
                ("smtp_use_ssl", "BOOLEAN", "FALSE"),
                ("system_page_title", "VARCHAR", "'Task Management System'"),
                ("theme_mode", "VARCHAR", "'system'"),
                ("border_radius", "VARCHAR", "'0.75rem'"),
                ("font_family", "VARCHAR", "'Inter, sans-serif'"),
                ("font_size_base", "VARCHAR", "'16px'"),
                ("industry", "VARCHAR", None),
                ("address", "VARCHAR", None),
                ("timezone", "VARCHAR", "'UTC'"),
                ("default_language", "VARCHAR", "'en'"),
                ("contact_phone", "VARCHAR", None),
                ("contact_email", "VARCHAR", None),
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
                ("reminder_at", "TIMESTAMP WITH TIME ZONE", None),
                ("reminder_sent", "BOOLEAN", "FALSE")
            ],
            "tasks": [
                ("is_archived", "BOOLEAN", "FALSE"),
                ("due_reminder_sent", "BOOLEAN", "FALSE")
            ],
            "users": [
                ("profile_photo_url", "VARCHAR", None),
                ("username", "VARCHAR", None),
                ("job_title", "VARCHAR", None),
                ("bio", "VARCHAR", None),
                ("phone_number", "VARCHAR", None),
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
                ("dnd_schedule", "TEXT", None),
                ("two_factor_enabled", "BOOLEAN", "FALSE"),
                ("two_factor_secret", "VARCHAR", None),
                ("last_login", "TIMESTAMP WITH TIME ZONE", None)
            ],
            "roles": [
                ("permissions_json", "TEXT", None),
                ("is_standard", "BOOLEAN", "FALSE")
            ],
            "invitations": [
                ("branch_ids", "INTEGER[]", None),
                ("dept_ids", "INTEGER[]", None)
            ]
        }

        for table, columns in migrations.items():
            logger.info(f"Checking table: {table}")
            for col_name, col_type, default_val in columns:
                cur.execute(f"""
                    SELECT count(*) 
                    FROM information_schema.columns 
                    WHERE table_name=%s AND column_name=%s;
                """, (table, col_name))
                
                if cur.fetchone()[0] == 0:
                    logger.info(f"  Adding column {table}.{col_name} ({col_type})")
                    alter_query = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"
                    if default_val is not None:
                        alter_query += f" DEFAULT {default_val}"
                    cur.execute(alter_query)
        
        conn.commit()
        logger.info("All migrations completed successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Migration error: {e}")

if __name__ == "__main__":
    migrate()
