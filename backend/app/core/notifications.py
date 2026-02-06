from typing import Any
from telegram import Bot
from app.core.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NotificationService:
    def __init__(self):
        self.tg_bot = None
        if settings.TELEGRAM_BOT_TOKEN:
            self.tg_bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    async def send_telegram_notification(self, chat_id: str, message: str):
        if self.tg_bot:
            await self.tg_bot.send_message(chat_id=chat_id, text=message)

    def send_email_notification(self, email_to: str, subject: str, body: str):
        if not settings.SMTP_HOST:
            return
            
        message = MIMEMultipart()
        message["From"] = settings.EMAILS_FROM_NAME
        message["To"] = email_to
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_EMAIL, email_to, message.as_string())

notification_service = NotificationService()
