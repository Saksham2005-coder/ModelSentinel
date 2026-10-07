from typing import List, Dict, Any

ML_COMPONENT_CATEGORIES = [
    "data_ingestion",
    "preprocessing",
    "feature_engineering",
    "model_definition",
    "inference",
    "evaluation",
    "monitoring",
    "configuration",
    "api_service",
    "tests",
    "unknown"
]

def classify_ml_component(file_path: str, symbols: List[str], imports: List[str]) -> Dict[str, Any]:
    """Deterministically classifies a file or symbol into an ML component category."""
    path_lower = file_path.lower()
    
    # 1. Tests
    if "test" in path_lower or any("test" in s.lower() for s in symbols):
        if "pytest" in imports or "unittest" in imports:
            return {"category": "tests", "confidence": "HIGH", "reason": "Test file path or testing imports detected"}
        return {"category": "tests", "confidence": "MEDIUM", "reason": "Test keywords in path or symbols"}

    # 2. Configuration
    if path_lower.endswith(('.yaml', '.yml', '.json')) or "config" in path_lower or "settings" in path_lower:
        return {"category": "configuration", "confidence": "HIGH", "reason": "Configuration file extension or path keyword"}

    # 3. API / Service
    if "api" in path_lower or "routes" in path_lower or "endpoints" in path_lower:
        if "fastapi" in imports or "flask" in imports or "django" in imports:
            return {"category": "api_service", "confidence": "HIGH", "reason": "API routing path with web framework imports"}
        return {"category": "api_service", "confidence": "MEDIUM", "reason": "API keywords in path"}

    # 4. Monitoring / Evaluation
    if "monitor" in path_lower or "metrics" in path_lower or "eval" in path_lower:
        return {"category": "monitoring", "confidence": "MEDIUM", "reason": "Monitoring or evaluation keywords in path"}

    # 5. Inference / Prediction
    if "predict" in path_lower or "inference" in path_lower or "serve" in path_lower:
        return {"category": "inference", "confidence": "HIGH", "reason": "Inference keywords in path"}
    if any("predict" in s.lower() or "infer" in s.lower() for s in symbols):
        return {"category": "inference", "confidence": "MEDIUM", "reason": "Inference keywords in symbols"}

    # 6. Model Definition
    if "model" in path_lower or "architecture" in path_lower or "net" in path_lower:
        if "torch" in imports or "tensorflow" in imports or "keras" in imports or "sklearn" in imports:
            return {"category": "model_definition", "confidence": "HIGH", "reason": "Model path with ML framework imports"}
        return {"category": "model_definition", "confidence": "MEDIUM", "reason": "Model keywords in path"}

    # 7. Preprocessing / Feature Engineering
    if "preprocess" in path_lower or "feature" in path_lower or "transform" in path_lower:
        return {"category": "feature_engineering", "confidence": "HIGH", "reason": "Feature engineering keywords in path"}
    if any("preprocess" in s.lower() or "transform" in s.lower() for s in symbols):
        return {"category": "feature_engineering", "confidence": "MEDIUM", "reason": "Transformation keywords in symbols"}

    # 8. Data Ingestion
    if "data" in path_lower or "ingest" in path_lower or "dataset" in path_lower or "loader" in path_lower:
        if "pandas" in imports or "numpy" in imports:
            return {"category": "data_ingestion", "confidence": "HIGH", "reason": "Data path with data manipulation imports"}
        return {"category": "data_ingestion", "confidence": "MEDIUM", "reason": "Data ingestion keywords in path"}

    # Fallback
    return {"category": "unknown", "confidence": "LOW", "reason": "No deterministic match found"}
