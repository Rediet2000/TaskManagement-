"""
Add profile columns to users table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_profile_columns():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        logger.info("Adding profile columns to users table...")
        
        # Profile Information
        columns_to_add = [
            ("profile_photo_url", "VARCHAR", "NULL"),
            ("phone_number", "VARCHAR", "NULL"),
            ("timezone", "VARCHAR", "DEFAULT 'UTC'"),
            ("language", "VARCHAR", "DEFAULT 'en'"),
            
            # Work Preferences
            ("task_view_preference", "VARCHAR", "DEFAULT 'board'"),
            ("default_task_sort", "VARCHAR", "DEFAULT 'due_date'"),
            ("start_of_week", "VARCHAR", "DEFAULT 'monday'"),
            ("date_format", "VARCHAR", "DEFAULT 'YYYY-MM-DD'"),
            ("time_format", "VARCHAR", "DEFAULT '24h'"),
            
            # Notification Settings - NULL for now, will set defaults via application
            ("email_notifications", "TEXT", "NULL"),
            ("in_app_notifications", "TEXT", "NULL"),
            ("dnd_schedule", "TEXT", "NULL"),
            
            # Security
            ("two_factor_enabled", "BOOLEAN", "DEFAULT FALSE"),
            ("two_factor_secret", "VARCHAR", "NULL"),
            ("last_login", "TIMESTAMP WITH TIME ZONE", "NULL"),
        ]
        
        for column_name, column_type, constraint in columns_to_add:
            try:
                # Check if column exists
                check_query = text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='{column_name}'
                """)
                result = conn.execute(check_query)
                
                if result.fetchone() is None:
                    # Column doesn't exist, add it
                    alter_query = text(f"""
                        ALTER TABLE users 
                        ADD COLUMN {column_name} {column_type} {constraint}
                    """)
                    conn.execute(alter_query)
                    conn.commit()
                    logger.info(f"✓ Added column: {column_name}")
                else:
                    logger.info(f"○ Column already exists: {column_name}")
                    
            except Exception as e:
                logger.error(f"✗ Error adding column {column_name}: {e}")
                conn.rollback()
        
        logger.info("Profile columns migration completed!")

if __name__ == "__main__":
    add_profile_columns()
