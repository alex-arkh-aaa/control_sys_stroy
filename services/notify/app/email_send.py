import asyncio
from smtplib import SMTP
from email.mime.text import MIMEText
from config import settings

async def send_email(mail: str, message: str, full_name: str, subject: str) -> bool:
    
    def sync_send_email():

        
        message_text = f'Добрый день, {full_name}!\n{message}'
        msg = MIMEText(message_text, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_login
        msg["To"] = mail
        
        with SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_login, settings.smtp_password)
            server.send_message(msg)
            print('Email отправлен синхронно')
        return True

    try:
        # Запускаем синхронный код в отдельном потоке
        await asyncio.to_thread(sync_send_email)
        print(f"✓ Email успешно отправлен на {mail}")
        return True
        
    except Exception as e:
        print(f"✗ Email error: {e}")
        return False