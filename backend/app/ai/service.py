from app.core.config import settings
from app.ai.providers.base import LLMProvider

def get_llm_provider() -> LLMProvider:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "groq":
        from app.ai.providers.groq_provider import GroqProvider
        return GroqProvider()
    raise ValueError(f"Unsupported LLM provider: {provider}")
