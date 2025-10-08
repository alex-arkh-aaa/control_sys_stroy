from shared.rabbitmq import rabbit_manager
from shared.rabbitmq.schemas import UserRegisteredEvent, UserDeletedEvent

class UserEventPublisher:
    def __init__(self):
        self.broker = rabbit_manager.broker
    
    async def publish_user_registered(self, user_id: int, email: str, name: str):
        event = UserRegisteredEvent(user_id=user_id, email=email, name=name)
        
        # Публикуем напрямую в очередь
        await self.broker.publish(event, queue="user_events")
        print(f"📨 Published user.registered event for {email}")
    
    async def publish_user_deleted(self, user_id: int, email: str, name: str):
        event = UserDeletedEvent(user_id=user_id, email=email, name=name)
        
        await self.broker.publish(event, queue="user_events")
        print(f"📨 Published user.deleted event for {email}")

# Глобальный инстанс
user_publisher = UserEventPublisher()