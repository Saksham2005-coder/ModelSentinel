import json
from typing import Any, Dict, List, Type
from pydantic import BaseModel
from groq import Groq

from app.core.config import settings
from app.ai.providers.base import LLMProvider

class GroqProvider(LLMProvider):
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.client = None
        if self.api_key:
            self.client = Groq(api_key=self.api_key)

    def health_check(self) -> bool:
        if not self.client:
            return False
        try:
            # simple cheap call
            self.client.models.retrieve(self.model)
            return True
        except Exception:
            return False

    def generate_structured(self, prompt: str, system_prompt: str, response_model: Type[BaseModel], **kwargs) -> BaseModel:
        if not self.client:
            raise ValueError("Groq provider not configured")

        schema = response_model.model_json_schema()
        
        # Groq doesn't natively support strictly enforcing an arbitrary pydantic model 
        # in standard chat completions without tool calling or JSON mode.
        # We will use JSON mode and instruct the model to follow the schema.
        
        system_msg = f"{system_prompt}\n\nYou MUST respond with valid JSON that matches the following schema:\n{json.dumps(schema)}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            **kwargs
        )
        
        content = response.choices[0].message.content
        return response_model.model_validate_json(content)

    def request_tool_calls(self, prompt: str, system_prompt: str, tools: List[Dict[str, Any]], **kwargs) -> Any:
        if not self.client:
            raise ValueError("Groq provider not configured")
            
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            tools=tools,
            tool_choice="auto",
            temperature=0.0,
            **kwargs
        )
        
        return response.choices[0].message
