from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type, Optional

from pydantic import BaseModel

class LLMProvider(ABC):
    @abstractmethod
    def health_check(self) -> bool:
        """Check if the provider is configured and available."""
        pass

    @abstractmethod
    def generate_structured(self, prompt: str, system_prompt: str, response_model: Type[BaseModel], **kwargs) -> BaseModel:
        """Generate structured output adhering to a Pydantic model."""
        pass

    @abstractmethod
    def request_tool_calls(self, prompt: str, system_prompt: str, tools: List[Dict[str, Any]], **kwargs) -> Any:
        """Ask the model to select tools to execute."""
        pass
