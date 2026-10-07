import os

class Config:
    API_URL = os.environ.get("MODELSENTINEL_API_URL", "http://localhost:8000/api/v1")
    TIMEOUT = int(os.environ.get("MODELSENTINEL_TIMEOUT", "30"))
    DEBUG = os.environ.get("MODELSENTINEL_DEBUG", "0").lower() in ("1", "true", "yes")

config = Config()
