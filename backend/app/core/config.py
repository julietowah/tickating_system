"""Settings loaded from environment variables."""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


# Find the nearest .env file and load its values.
load_dotenv()


class Settings(BaseSettings):
    """Values that can change between development and production."""

    database_url: str = "sqlite:///./service_desk.db"
    secret_key: str
    access_token_expire_minutes: int = 60


settings = Settings()
