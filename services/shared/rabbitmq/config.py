from pydantic_settings import BaseSettings

class RabbitMQConfig(BaseSettings):
    host: str = "localhost"
    port: int = 5672
    username: str = "guest"
    password: str = "guest"
    virtual_host: str = "/"
    
    # Exchange names
    USER_EXCHANGE: str = "user_events"
    NOTIFICATION_EXCHANGE: str = "notifications"
    
    # Queue names
    EMAIL_QUEUE: str = "email_notifications"
    TELEGRAM_QUEUE: str = "telegram_notifications"
    
    class Config:
        env_prefix = "RABBITMQ_"
        env_file = ".env"

rabbit_config = RabbitMQConfig()

def get_rabbit_url():
    return f"amqp://{rabbit_config.username}:{rabbit_config.password}@{rabbit_config.host}:{rabbit_config.port}/{rabbit_config.virtual_host}"