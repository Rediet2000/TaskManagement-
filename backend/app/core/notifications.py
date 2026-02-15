from typing import Any, Optional
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

notification_service = NotificationService()
