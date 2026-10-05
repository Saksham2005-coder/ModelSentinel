from typing import Any, Callable, Dict, List
import inspect

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: List[Dict[str, Any]] = []

    def register(self, name: str, description: str, parameters_schema: Dict[str, Any]):
        def decorator(func: Callable):
            self._tools[name] = func
            self._schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters_schema
                }
            })
            return func
        return decorator

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return self._schemas

    def execute(self, name: str, kwargs: Dict[str, Any], context: Dict[str, Any]) -> Any:
        if name not in self._tools:
            raise ValueError(f"Tool {name} not found")
        # Inject context (like db session) if requested by the tool
        func = self._tools[name]
        sig = inspect.signature(func)
        call_kwargs = {}
        for param_name in sig.parameters:
            if param_name in kwargs:
                call_kwargs[param_name] = kwargs[param_name]
            elif param_name in context:
                call_kwargs[param_name] = context[param_name]
        return func(**call_kwargs)

registry = ToolRegistry()

# Import tools so they get registered
import app.investigation.tools.monitoring_tool
import app.investigation.tools.incident_tool
