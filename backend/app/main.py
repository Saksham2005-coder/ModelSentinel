from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import json

app = FastAPI(
    title="ModelSentinel API",
    version="0.1.0",
)

# CORS setup
origins = os.getenv("BACKEND_CORS_ORIGINS", '["http://localhost:5173"]')
if isinstance(origins, str):
    try:
        origins = json.loads(origins)
    except Exception:
        origins = [origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "modelsentinel-api",
        "version": "0.1.0"
    }
