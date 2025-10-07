from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    smtp_server: str
    smtp_port: int
    smtp_login: str
    smtp_password: str

    class Config:
        env_file = Path(__file__).parent / ".env"

settings = Settings()