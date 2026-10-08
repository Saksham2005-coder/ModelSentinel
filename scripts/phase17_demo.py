import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def create_model():
    print("Creating Test Model...")
    res = requests.post(f"{BASE_URL}/models/", json={
        "name": "Phase 17 Demo Model",
        "slug": "phase17-demo-model",
        "framework": "xgboost",
        "task_type": "classification",
        "primary_metric": "accuracy"
    })
    model = res.json()
    print(f"Model created: {model['id']}")
    return model

def create_historical_incident(model_id):
    print("Creating Historical Incident...")
    res = requests.post(f"{BASE_URL}/incidents/", json={
        "model_id": model_id,
        "title": "Historical Data Drift (Resolved)",
        "summary": "Data drift detected in feature 'age'",
        "severity": "high",
        "category": "data_drift"
    })
    inc = res.json()
    print(f"Incident created: {inc['id']}")
    
    print("Resolving incident to create memory...")
    # Add memory directly or via resolution
    mem_res = requests.post(f"{BASE_URL}/incidents/{inc['id']}/memory", json={
        "title": "Historical Drift Resolution",
        "resolution_summary": "Retrained model with updated feature weights"
    })
    mem = mem_res.json()
    print(f"Memory created: {mem['id']}")
    
    # We will simulate resolution memory directly via DB script if API doesn't support manual creation easily
    # But let's check if the API has a way to update it.
    
    return inc, mem

def main():
    model = create_model()
    model_id = model["id"]
    
    # Needs to run within app context for DB access since we don't have API for full ResolutionMemory population yet.
    pass

if __name__ == "__main__":
    main()
