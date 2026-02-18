from typing import Any, Optional, Dict
import json
from datetime import datetime
from telegram import Bot
from app.core.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models.core import Organization
from sqlalchemy.orm import Session

class NotificationService:
    def __init__(self):
        self.bot_pool = {} # Cache bots by token if needed

    def _get_bot(self, token: str) -> Optional[Bot]:
        if not token:
            return None
        if token not in self.bot_pool:
            try:
                self.bot_pool[token] = Bot(token=token)
            except Exception as e:
                print(f"Error creating Telegram bot: {e}")
                return None
        return self.bot_pool[token]

    async def send_telegram_notification(self, db: Session, org_id: int, message: str, chat_id: Optional[str] = None):
        """
        Sends a telegram notification using organization-specific settings.
        If chat_id is not provided, uses the default one from org settings.
        """
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org or not org.telegram_enabled or not org.telegram_bot_token:
            return

        token = org.telegram_bot_token
        target_chat = chat_id or org.telegram_chat_id
        
        if not target_chat:
            return

        bot = self._get_bot(token)
        if bot:
            try:
                await bot.send_message(chat_id=target_chat, text=message)
            except Exception as e:
                print(f"Error sending Telegram message: {e}")

    def send_telegram_background(self, org_id: int, message: str, chat_id: Optional[str] = None):
        """
        Background version of send_telegram_notification that handles its own DB session.
        Suitable for use with FastAPI BackgroundTasks in sync endpoints.
        """
        from app.db.base import SessionLocal
        import asyncio
        
        db = SessionLocal()
        try:
            # We need to run the async send_telegram_notification in the current thread's loop or create one
            # FastAPI's background tasks for sync def functions run in a threadpool.
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            loop.run_until_complete(self.send_telegram_notification(db, org_id, message, chat_id))
        finally:
            db.close()

    def send_email_notification(self, db: Session, org_id: int, email_to: str, subject: str, body: str):
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org or not org.email_notifications_enabled or not org.smtp_host:
            return

        # Use Org specific SMTP or system default
        smtp_host = org.smtp_host
        smtp_port = org.smtp_port or 587
        smtp_user = org.smtp_user
        smtp_password = org.smtp_password
        from_email = org.smtp_from_email or settings.EMAILS_FROM_EMAIL
            
        message = MIMEMultipart()
        message["From"] = f"{org.name} <{from_email}>"
        message["To"] = email_to
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                if org.smtp_port != 465:
                    server.starttls()
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.sendmail(from_email, email_to, message.as_string())
        except Exception as e:
            print(f"Error sending email: {e}")

    def format_message(self, db: Session, org_id: int, lang: str, event_type: str, context: Dict[str, Any]) -> str:
        """
        Formats a notification message using placeholders.
        """
        org = db.query(Organization).filter(Organization.id == org_id).first()
        template = None
        
        if org and org.notification_template:
            try:
                templates = json.loads(org.notification_template)
                template = templates.get(lang) or templates.get('en')
            except:
                template = None

        if not template:
            # Standard default notifications
            defaults = {
                "NEW_TASK": "🚀 New Task Assigned: {task_title}\nPriority: {priority}\nBy: {sender_name}\nDate: {date} at {time}",
                "TASK_UPDATE": "📝 Task Updated: {task_title}\nStatus: {status}\nBy: {sender_name}",
                "PROBLEM_ASSIGNED": "⚠️ Problem Assigned: {task_title}\nSeverity: {priority}\nDate: {date} {time}",
                "NOTE_REMINDER": "🕒 REMINDER: {task_title}\nFolder: {folder_name}\nContent: {content}\nSet for: {date} {time}"
            }
            template = defaults.get(event_type, "Notification: {task_title} ({date} {time})")

        # Prepare global context
        now = datetime.now()
        global_ctx = {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M"),
            "hour": now.strftime("%H"),
            "minute": now.strftime("%M"),
            "day": now.strftime("%A"),
            "org_name": org.name if org else "Task System"
        }
        
        # Merge contexts
        full_ctx = {**global_ctx, **context}
        
        # Perform replacement
        message = template
        for key, value in full_ctx.items():
            placeholder = "{" + key + "}"
            message = message.replace(placeholder, str(value if value is not None else ""))
            
        return message

notification_service = NotificationService()
