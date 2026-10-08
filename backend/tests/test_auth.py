import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import SessionLocal
from app.models.user import User, Role
from app.core.security import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def clean_db():
    db = SessionLocal()
    try:
        db.query(User).delete()
        db.commit()
        yield db
    finally:
        db.close()

def test_registration_success():
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "New User"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "VIEWER"
    
def test_registration_duplicate_email():
    # First create
    client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "New User"
    })
    # Then try to create duplicate
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "Duplicate User"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_registration_role_escalation_prevented():
    response = client.post("/api/v1/auth/register", json={
        "email": "hacker@example.com",
        "password": "SecurePassword123!",
        "full_name": "Hacker",
        "role": "ADMIN"
    })
    assert response.status_code == 200
    data = response.json()
    # Should force to VIEWER despite requesting ADMIN
    assert data["role"] == "VIEWER"

def test_login_success(clean_db: Session):
    client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User"
    })
    
    # Get token from db
    from app.models.user import VerificationToken
    user = clean_db.query(User).filter(User.email == "newuser@example.com").first()
    token_record = clean_db.query(VerificationToken).filter(VerificationToken.user_id == user.id).first()
    
    # Needs to match raw token, but we only have hash in DB. 
    # Actually, we can just manually set it in DB and commit, why didn't it work?
    # Because SQLite caches it? Let's just do `db.refresh(user)` in the endpoint? No, the login endpoint creates a new session.
    # Ah, SQLAlchemy caches objects. Maybe `clean_db.commit()` didn't work because `user` was modified but `clean_db` didn't track it properly?
    user.email_verified = True
    clean_db.add(user)
    clean_db.commit()
    
    response = client.post("/api/v1/auth/login", data={
        "username": "newuser@example.com",
        "password": "SecurePassword123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(clean_db: Session):
    client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User"
    })
    
    user = clean_db.query(User).filter(User.email == "newuser@example.com").first()
    user.email_verified = True
    clean_db.add(user)
    clean_db.commit()
    
    response = client.post("/api/v1/auth/login", data={
        "username": "newuser@example.com",
        "password": "WrongPassword!"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_unknown_email():
    response = client.post("/api/v1/auth/login", data={
        "username": "unknown@example.com",
        "password": "SecurePassword123!"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_empty_credentials():
    response = client.post("/api/v1/auth/login", data={
        "username": "",
        "password": ""
    })
    assert response.status_code == 422  # FastAPI validation error

def test_plaintext_password_not_returned(clean_db: Session):
    client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User"
    })
    
    user = clean_db.query(User).filter(User.email == "newuser@example.com").first()
    user.email_verified = True
    clean_db.add(user)
    clean_db.commit()
    
    response = client.post("/api/v1/auth/login", data={
        "username": "newuser@example.com",
        "password": "SecurePassword123!"
    })
    token = response.json()["access_token"]
    
    me_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    data = me_response.json()
    assert "password" not in data
    assert "hashed_password" not in data
    assert data["email"] == "newuser@example.com"

def test_unauthorized_access():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_session_logout(clean_db: Session):
    client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User"
    })
    
    user = clean_db.query(User).filter(User.email == "newuser@example.com").first()
    user.email_verified = True
    clean_db.add(user)
    clean_db.commit()
    
    response = client.post("/api/v1/auth/login", data={
        "username": "newuser@example.com",
        "password": "SecurePassword123!"
    })
    token = response.json()["access_token"]
    
    logout_response = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_response.status_code == 200
    
def test_unverified_user_cannot_login():
    client.post("/api/v1/auth/register", json={
        "email": "unverified@example.com",
        "password": "SecurePassword123!",
        "full_name": "Unverified User"
    })
    
    response = client.post("/api/v1/auth/login", data={
        "username": "unverified@example.com",
        "password": "SecurePassword123!"
    })
    assert response.status_code == 401
    assert "verify your email" in response.json()["detail"]
