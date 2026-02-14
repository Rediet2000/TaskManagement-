import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models.notes import Note
from app.models.task_tracking import Notification
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_reminders():
    """
    Periodically check for notes with upcoming reminders and create notifications.
    """
    logger.info("--- Reminder Service Started ---")
    while True:
        try:
            db = SessionLocal()
            now = datetime.now()
            # Find notes with reminders in the next minute that haven't been 'notified' yet
            # For simplicity, we'll mark them as notified in a metadata field or similar
            # In a real system, you'd have a 'reminder_sent' flag.
            
            # Since we don't have a 'reminder_sent' flag yet, let's just 
            # find notes where reminder_at is past-due (but recent).
            # To avoid duplicate notifications, this is a bit tricky without a flag.
            
            # For MVP, let's just log and create one notification.
            # I'll add a 'notified' check later? 
            # Actually, let's check notes where reminder_at is within [now-5min, now]
            
            notes = db.query(Note).filter(
                Note.reminder_at != None,
                Note.reminder_at <= now,
                Note.reminder_at >= now - timedelta(minutes=5)
            ).all()
            
            for note in notes:
                # Check if notification already exists for this note/reminder
                existing = db.query(Notification).filter(
                    Notification.message.like(f"%Reminder for note: {note.title}%"),
                    Notification.created_at >= note.reminder_at
                ).first()
                
                if not existing:
                    logger.info(f"Triggering reminder for note: {note.title}")
                    notif = Notification(
                        user_id=note.user_id,
                        channel="web",
                        message=f"Transmission Reminder for note: {note.title}",
                        status="Pending",
                        trigger_event="note_reminder"
                    )
                    db.add(notif)
            
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Error in reminder task: {e}")
        
        await asyncio.sleep(60) # Check every minute

def start_background_tasks():
    loop = asyncio.get_event_loop()
    loop.create_task(check_reminders())
