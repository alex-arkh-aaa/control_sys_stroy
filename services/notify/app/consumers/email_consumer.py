import sys
import os
from pathlib import Path

# Добавляем корень проекта в Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from faststream import FastStream
from shared.rabbitmq import rabbit_manager
from shared.rabbitmq.schemas import UserRegisteredEvent, UserDeletedEvent
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from email_send import send_email
broker = rabbit_manager.broker
app = FastStream(broker)

@broker.subscriber("user_events")
async def handle_user_events(event: UserRegisteredEvent | UserDeletedEvent):
    try:
        if isinstance(event, UserRegisteredEvent):
            await _send_welcome_email(event)
        elif isinstance(event, UserDeletedEvent):
            await _send_deletion_email(event)
            
        print(f"✅ Processed {event.event_type} for {event.email}")
        
    except Exception as e:
        print(f"❌ Failed to process {event.event_type}: {e}")
        raise e

async def _send_welcome_email(event: UserRegisteredEvent):
    subject = "Добро пожаловать в Control System!"
    message = f"""Уважаемый(ая) {event.name}!

Вы успешно зарегистрировались в системе управления строительными дефектами.

Ваш ID: {event.user_id}

С уважением,
Команда Control System"""
    
    await send_email(event.email, message, event.name, subject)

async def _send_deletion_email(event: UserDeletedEvent):
    subject = "Аккаунт удален"
    message = f"""Уважаемый(ая) {event.name}!

Ваш аккаунт был успешно удален из системы управления строительными дефектами.

С уважением,
Команда Control System"""
    
    await send_email(event.email, message, event.name, subject)