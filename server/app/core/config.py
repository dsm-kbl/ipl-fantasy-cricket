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

    # Email (Mailjet HTTP API)
    mailjet_api_key: str = ""
    mailjet_secret_key: str = ""
    mailjet_sender_email: str = "dibsarthak@gmail.com"
    frontend_url: str = "http://localhost:3000"

    model_config = {"env_prefix": "APP_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
