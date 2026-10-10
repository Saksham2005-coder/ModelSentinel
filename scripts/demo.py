import sys
import os
import subprocess
import time
import argparse

def run_command(cmd, cwd=None, wait=True):
    print(f"Running: {cmd}")
    process = subprocess.Popen(cmd, shell=True, cwd=cwd)
    if wait:
        process.wait()
        if process.returncode != 0:
            print(f"Command failed with exit code {process.returncode}")
            sys.exit(process.returncode)
    return process

def check_backend_ready():
    import urllib.request
    print("Waiting for backend readiness (this may take a few seconds)...")
    for _ in range(30):
        try:
            resp = urllib.request.urlopen("http://localhost:8000/health")
            if resp.getcode() == 200:
                print("Backend is ready!")
                return True
        except:
            pass
        time.sleep(0.5)
    return False

def check_frontend_ready():
    import urllib.request
    print("Waiting for frontend readiness...")
    for _ in range(30):
        try:
            resp = urllib.request.urlopen("http://localhost:5173/")
            if resp.getcode() == 200:
                print("Frontend is ready!")
                return True
        except:
            pass
        time.sleep(0.5)
    return False

def seed_demo(reset=False):
    print("Preparing demo environment...")
    
    # We execute seed script inside the backend container
    # so we don't have to worry about python environment / dependencies locally.
    # Ensure admin user exists before seeding
    admin_cmd = "docker compose -f docker-compose.demo.yml exec backend python scripts/create_admin.py --demo"
    print("Bootstrapping demo admin account...")
    subprocess.Popen(admin_cmd, shell=True).wait()

    cmd = "docker compose -f docker-compose.demo.yml exec backend python scripts/seed_demo_environment.py"
    if reset:
        cmd += " --reset"
        print("Executing reset command...")
    else:
        print("Executing seed command...")
        
    process = subprocess.Popen(cmd, shell=True)
    process.wait()
    if process.returncode == 0:
        print("Success!")
    else:
        print(f"Failed with exit code {process.returncode}")

def start_demo():
    print("Starting ModelSentinel Demo Environment...")
    run_command("docker compose -f docker-compose.demo.yml up -d")
    
    if check_backend_ready() and check_frontend_ready():
        print("\n========================================================")
        print("ModelSentinel Hackathon Demo Environment Started Successfully!")
        print("Frontend: http://localhost:5173")
        print("Backend API: http://localhost:8000")
        print("========================================================\n")
    else:
        print("Services failed to become ready in time. Check docker logs.")
        sys.exit(1)

def stop_demo():
    print("Stopping ModelSentinel...")
    run_command("docker compose -f docker-compose.demo.yml down")

def status_demo():
    run_command("docker compose -f docker-compose.demo.yml ps")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ModelSentinel Demo Workflow Script")
    parser.add_argument("action", choices=["start", "stop", "reset", "seed", "status"], help="Action to perform")
    args = parser.parse_args()

    if args.action == "start":
        start_demo()
    elif args.action == "stop":
        stop_demo()
    elif args.action == "status":
        status_demo()
    elif args.action == "reset":
        seed_demo(reset=True)
    elif args.action == "seed":
        seed_demo(reset=False)
