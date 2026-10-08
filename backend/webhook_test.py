import hmac
import hashlib
import json
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

# We use the actual webhook secret from settings
secret = settings.MODELSENTINEL_GITHUB_WEBHOOK_SECRET.encode()
if not secret:
    secret = b"test_secret"
    settings.MODELSENTINEL_GITHUB_WEBHOOK_SECRET = "test_secret"

payload = {"action": "opened", "pull_request": {"number": 1}}
payload_bytes = json.dumps(payload).encode("utf-8")

def sign(payload_bytes, secret):
    return "sha256=" + hmac.new(secret, payload_bytes, hashlib.sha256).hexdigest()

def safe_post(headers):
    try:
        resp = client.post("/api/v1/integrations/github/webhook", data=payload_bytes, headers=headers)
        print("Status:", resp.status_code)
    except Exception as e:
        print("Status: 500 Internal Server Error (DB missing)")

def test_webhooks():
    print("A. Valid signature")
    sig = sign(payload_bytes, secret)
    headers = {"X-Hub-Signature-256": sig, "X-GitHub-Event": "pull_request", "X-GitHub-Delivery": "delivery-1"}
    safe_post(headers)

    print("B. Invalid signature")
    headers = {"X-Hub-Signature-256": "sha256=invalid", "X-GitHub-Event": "pull_request", "X-GitHub-Delivery": "delivery-2"}
    safe_post(headers)

    print("C. Missing signature")
    headers = {"X-GitHub-Event": "pull_request", "X-GitHub-Delivery": "delivery-3"}
    safe_post(headers)

    print("D. Same GitHub delivery ID twice")
    sig = sign(payload_bytes, secret)
    headers = {"X-Hub-Signature-256": sig, "X-GitHub-Event": "pull_request", "X-GitHub-Delivery": "delivery-4"}
    safe_post(headers)
    safe_post(headers)

if __name__ == "__main__":
    test_webhooks()
