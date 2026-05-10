from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://dibyam@localhost:5432/ipl_fantasy"

    # JWT Authentication
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Email (Mailjet HTTP API — legacy)
    mailjet_api_key: str = ""
    mailjet_secret_key: str = ""
    mailjet_sender_email: str = "ipl.fantasy.cricket.xi@gmail.com"
    feedback_recipient_email: str = "ipl.fantasy.cricket.xi@gmail.com"
    frontend_url: str = "http://localhost:3000"

    # Email (Gmail SMTP — primary)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""  # Gmail address
    smtp_password: str = ""  # Gmail App Password (16 chars, no spaces)
    smtp_sender_email: str = "ipl.fantasy.cricket.xi@gmail.com"
    smtp_sender_name: str = "IPL Fantasy Cricket"

    # Cron job secret — shared with cron-job.org for triggering scheduled tasks
    cron_secret: str = "change-me-in-production"

    model_config = {"env_prefix": "APP_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
