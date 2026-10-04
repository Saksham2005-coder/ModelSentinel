import os
from pydantic_settings import BaseSettings

from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "ModelSentinel API")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "modelsentinel")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "modelsentinel_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "modelsentinel")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    TESTING: bool = os.getenv("TESTING", "0") == "1"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.TESTING:
            return "sqlite:///./test.db"
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
