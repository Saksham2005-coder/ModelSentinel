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

    MODELSENTINEL_GITHUB_TOKEN: str = os.getenv("MODELSENTINEL_GITHUB_TOKEN", os.getenv("GITHUB_TOKEN", ""))
    MODELSENTINEL_GITHUB_API_URL: str = os.getenv("MODELSENTINEL_GITHUB_API_URL", os.getenv("GITHUB_API_URL", "https://api.github.com"))
    MODELSENTINEL_GITHUB_WEBHOOK_SECRET: str = os.getenv("MODELSENTINEL_GITHUB_WEBHOOK_SECRET", "")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.TESTING:
            # Deterministic relative path for testing
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
            return f"sqlite:///{os.path.join(project_root, 'test.db')}"
        if self.DATABASE_URL:
            # If DATABASE_URL is a relative sqlite URL like sqlite:///./file.db, make it deterministic
            if self.DATABASE_URL.startswith("sqlite:///./"):
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
                db_name = self.DATABASE_URL.replace("sqlite:///./", "")
                return f"sqlite:///{os.path.join(project_root, db_name)}"
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
