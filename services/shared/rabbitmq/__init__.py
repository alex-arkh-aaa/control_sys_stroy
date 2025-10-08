from faststream.rabbit import RabbitBroker
from .config import get_rabbit_url
import asyncio

class RabbitMQManager:
    def __init__(self):
        self.broker = RabbitBroker(get_rabbit_url())
        self._is_connected = False
    
    async def connect(self):
        if not self._is_connected:
            await self.broker.start()
            self._is_connected = True
        print("✅ RabbitMQ connected")

# Глобальный инстанс
rabbit_manager = RabbitMQManager()