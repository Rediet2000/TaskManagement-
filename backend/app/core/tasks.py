import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models.notes import Note
from app.models.task_tracking import Notification, Task
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
            now = datetime.now(timezone.utc)
            # Find notes with reminders in the next minute that haven't been 'notified' yet
            notes = db.query(Note).filter(
                Note.reminder_at != None,
                Note.reminder_at <= now,
                Note.reminder_sent == False
            ).all()
            
            for note in notes:
                logger.info(f"Triggering reminder for note: {note.title}")
                from app.core.notifications import notification_service
                
                context = {
                    "task_title": note.title,
                    "content": note.content[:100] + "..." if note.content and len(note.content) > 100 else (note.content or ""),
                    "folder_name": note.folder.name if note.folder else "General",
                    "sender_name": note.creator.full_name if note.creator else "System"
                }
                
                message = notification_service.format_message(db, note.org_id, "en", "NOTE_REMINDER", context)
                notif = Notification(
                    user_id=note.created_by,
                    channel="web",
                    message=message,
                    status="Pending",
                    trigger_event="note_reminder"
                )
                db.add(notif)
                if note.creator and note.creator.email:
                    notification_service.send_email_notification(db, note.org_id, note.creator.email, f"Reminder: {note.title}", message)

                note.reminder_sent = True
            
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Error in reminder task: {e}")
        
        await asyncio.sleep(60)

async def check_task_reminders():
    """
    Periodically check for tasks that are due soon.
    """
    logger.info("--- Task Reminder Service Started ---")
    while True:
        try:
            db = SessionLocal()
            now = datetime.now(timezone.utc)
            # Find tasks due in the next 24 hours that haven't been notified
            soon = now + timedelta(hours=24)
            
            tasks = db.query(Task).filter(
                Task.due_date != None,
                Task.due_date <= soon,
                Task.due_date >= now,
                Task.due_reminder_sent == False,
                Task.status != "Completed"
            ).all()
            
            from app.core.notifications import notification_service

            for task in tasks:
                logger.info(f"Triggering due reminder for task: {task.title}")
                assignee = task.assignee
                if assignee:
                    context = {
                        "task_title": task.title,
                        "status": task.status,
                        "priority": task.priority,
                        "sender_name": "System",
                        "date": task.due_date.strftime("%Y-%m-%d"),
                        "time": task.due_date.strftime("%H:%M")
                    }
                    message = notification_service.format_message(db, task.org_id, assignee.language or "en", "TASK_DUE_SOON", context)
                    if "TASK_DUE_SOON" in message:
                        message = f"🔔 Task Due Soon: {task.title}\nDue at: {task.due_date.strftime('%Y-%m-%d %H:%M')}"

                    notif = Notification(
                        user_id=assignee.id,
                        channel="web",
                        message=message,
                        status="Pending",
                        trigger_event="task_due_reminder"
                    )
                    db.add(notif)
                    if assignee.email:
                        notification_service.send_email_notification(db, task.org_id, assignee.email, f"Due Soon: {task.title}", message)

                task.due_reminder_sent = True
            
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Error in task reminder loop: {e}")
        
        await asyncio.sleep(300)

def start_background_tasks():
    loop = asyncio.get_event_loop()
    loop.create_task(check_reminders())
    loop.create_task(check_task_reminders())
