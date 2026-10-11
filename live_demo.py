import requests
import uuid
from datetime import datetime, timedelta
import io
import time
import os

API_BASE = "http://localhost:8000/api/v1"

def print_step(title):
    print(f"\n{'-'*50}")
    print(f"> {title}")
    print(f"{'-'*50}")

def simulate():
    print("""
=====================================================
      ModelSentinel Live Demo Simulator              
=====================================================
This script will demonstrate the full ML-reliability 
workflow dynamically, bypassing all dummy data!

It will:
1. Create a brand new Model & Version
2. Generate a baseline distribution for it
3. Stream anomalous live telemetry (Data Drift!)
4. Trigger an Incident in the ModelSentinel backend
=====================================================
""")
    
    import sys
    model_name = sys.argv[1] if len(sys.argv) > 1 else "Live Demo Predictor"
    email = sys.argv[2] if len(sys.argv) > 2 else "admin@modelsentinel.local"
    password = sys.argv[3] if len(sys.argv) > 3 else "admin"
    print(f"Using model name: {model_name}")

    print_step("Authenticating with Backend...")
    auth_res = requests.post(f"{API_BASE}/auth/login", data={
        "username": email,
        "password": password
    })
    if auth_res.status_code != 200:
        print("❌ Error authenticating:", auth_res.text)
        print("\nMake sure to provide your email and password as arguments!")
        print("Usage: python live_demo.py \"Model Name\" your_email your_password")
        return
    token = auth_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[*] Successfully authenticated!")
        
    slug = model_name.lower().replace(" ", "-") + "-" + str(uuid.uuid4())[:4]
    
    # 1. Create Model
    print_step(f"Creating model '{model_name}'...")
    res = requests.post(f"{API_BASE}/models", headers=headers, json={
        "name": model_name,
        "slug": slug,
        "framework": "xgboost",
        "task_type": "classification",
        "primary_metric": "f1_score",
        "environment": "production",
        "status": "active"
    })
    if res.status_code != 201:
        print("❌ Error creating model:", res.text)
        return
    model = res.json()
    model_id = model["id"]
    print(f"[*] Model created! ID: {model_id}")
    
    # 1b. Create Baseline File directly in backend so telemetry works
    baseline_path = os.path.join("data", f"{slug}_baseline.csv")
    os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
    with open(baseline_path, "w") as f:
        f.write("timestamp,feature_1,feature_2,feature_3,prediction,actual\n")
        for _ in range(100):
            # Normal values
            f.write("2024-01-01T00:00:00,1.0,2.0,3.0,1,1\n")
    print(f"[*] Generated baseline distribution at '{baseline_path}'")
    
    # 2. Create Model Version
    print_step(f"Creating model version v1.0.0...")
    res = requests.post(f"{API_BASE}/models/{model_id}/versions", headers=headers, json={
        "version": "v1.0.0",
        "description": "Initial production version",
        "is_active": True
    })
    if res.status_code != 201:
        print("❌ Error creating model version:", res.text)
        return
    version = res.json()
    version_id = version["id"]
    print(f"[*] Version created and activated! ID: {version_id}")

    time.sleep(1)

    # 3. Generate Anomalous Telemetry
    print_step(f"Simulating Anomalous Live Telemetry...")
    print("Generating 500 rows of predictions with extreme data drift...")
    csv_content = "timestamp,feature_1,feature_2,feature_3,prediction,actual\n"
    now = datetime.utcnow()
    for i in range(500):
        # Crazy values to trigger severe drift alerts
        ts = (now - timedelta(minutes=500-i)).isoformat()
        f1 = 999.9  # extreme drift from baseline 1.0
        f2 = -500.0 # extreme drift from baseline 2.0
        f3 = 0.0
        pred = 1
        actual = 0  # wrong prediction
        csv_content += f"{ts},{f1},{f2},{f3},{pred},{actual}\n"
        
    print("✅ Telemetry payload ready.")
    
    time.sleep(1)

    # 4. Upload Telemetry
    print_step(f"Sending Telemetry to ModelSentinel Engine...")
    print(f"POST {API_BASE}/telemetry/")
    files = {
        'file': ('telemetry.csv', io.StringIO(csv_content), 'text/csv')
    }
    data = {
        'model_id': model_id,
        'model_version_id': version_id,
        'source': 'live_production_stream',
        'window_start': (now - timedelta(minutes=500)).isoformat(),
        'window_end': now.isoformat()
    }
    
    res = requests.post(f"{API_BASE}/telemetry/", headers=headers, data=data, files=files)
    if res.status_code != 201:
        print("❌ Error uploading telemetry:", res.text)
        return
        
    result = res.json()
    print("✅ Telemetry processed by backend engine successfully!")
    print(f"  Rows processed: {result.get('sample_count')}")
    
    incident_id = result.get('incident_id')
    if incident_id:
        print(f"  🚨 ML INCIDENT TRIGGERED BY ENGINE: {incident_id}")
    else:
        print("  ✅ Engine found no anomalies (Wait, we intended to trigger one!)")
        
    print_step("🎉 DEMO WORKFLOW COMPLETE!")
    print("Your backend has dynamically processed everything.")
    print("Go back to the ModelSentinel UI in your browser:")
    print(" 1. Check the 'Models' page to see your new model.")
    print(" 2. Check the 'Incidents' page to see the newly detected anomaly!")
    if incident_id:
        print(f" 3. Click 'Investigate' on the incident to have the LLM analyze it.")

if __name__ == "__main__":
    try:
        simulate()
    except Exception as e:
        print(f"Error: {e}")
