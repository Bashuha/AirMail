import os
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from pydantic_settings import BaseSettings, SettingsConfigDict
import pika


BASEDIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    # RabbitMQ
    RMQ_HOST: str = "localhost"
    RMQ_PORT: int = 5672
    RMQ_USER: str
    RMQ_PASSWORD: str
    RMQ_QUEUE: str = "notifications.service"
    RMQ_EXCHANGE: str = "notify"
    RMQ_ROUTING_KEY: str = "send.messages"

    # Database
    DATABASE_URL: str = "sqlite:///./notifications.db"
    
    # SMTP (Email)
    SMTP_HOST: str = "smtp.yandex.ru"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM: str

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
connection_params = pika.ConnectionParameters(
    host=settings.RMQ_HOST,
    port=settings.RMQ_PORT,
    credentials=pika.PlainCredentials(settings.RMQ_USER, settings.RMQ_PASSWORD),
)


def configure_logging(level = logging.INFO):
    logs_dir = BASEDIR / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    log_format = "[%(asctime)s.%(msecs)03d] - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(
        level=level,
        datefmt=date_format,
        format=log_format,
    )
    
    log_file = logs_dir / "unexpected_errors.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=2 * 1024 * 1024,  # 2 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    
    logging.getLogger().addHandler(file_handler)
    
    os.chmod(log_file, 0o666)