import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "ModelSentinel API")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "modelsentinel")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "modelsentinel_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "modelsentinel")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    TESTING: bool = os.getenv("TESTING", "0") == "1"

    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.TESTING:
            return "sqlite:///./test.db"
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
