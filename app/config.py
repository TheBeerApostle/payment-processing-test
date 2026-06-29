import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Загружаем .env файл


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/payments")

    # API
    API_KEY: str = os.getenv("API_KEY", "test-api-key-12345")

    # Outbox
    OUTBOX_POLL_INTERVAL: int = int(os.getenv("OUTBOX_POLL_INTERVAL", "5"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    WEBHOOK_TIMEOUT: int = int(os.getenv("WEBHOOK_TIMEOUT", "10"))

    # RabbitMQ
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()