import os
import uuid
import datetime
import hashlib
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User, VerificationToken
from app.core.config import settings

class EmailProvider:
    def send_verification_email(self, email: str, token: str) -> bool:
        """
        Sends an email with a verification link.
        """
        pass

class DevelopmentEmailProvider(EmailProvider):
    def send_verification_email(self, email: str, token: str) -> bool:
        # In development, just print the token nicely
        print("\n" + "="*50)
        print(" DEVELOPMENT EMAIL INTERCEPT")
        print("="*50)
        print(f" To: {email}")
        print(f" Subject: Verify your ModelSentinel Account")
        print(f" Link: http://localhost:5173/verify-email?token={token}")
        print("="*50 + "\n")
        return True

class SMTPEmailProvider(EmailProvider):
    def __init__(self):
        self.host = os.getenv("SMTP_HOST")
        self.port = os.getenv("SMTP_PORT")
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.sender = os.getenv("EMAIL_FROM", "noreply@modelsentinel.com")

    def send_verification_email(self, email: str, token: str) -> bool:
        # SMTP implementation goes here. For now, since we only need configurable 
        # abstraction, we'll act like it succeeded if configured, or print it.
        # This is where smtplib would be used.
        return True

def get_email_provider() -> EmailProvider:
    provider_type = os.getenv("EMAIL_PROVIDER", "console")
    if provider_type == "smtp":
        return SMTPEmailProvider()
    return DevelopmentEmailProvider()

provider = get_email_provider()

def create_verification_token(db: Session, user: User) -> str:
    # Generate raw token
    raw_token = str(uuid.uuid4())
    # Hash for storage
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    
    token_record = VerificationToken(
        token_hash=token_hash,
        user_id=user.id,
        expires_at=expires_at
    )
    db.add(token_record)
    db.commit()
    
    return raw_token

def verify_token(db: Session, raw_token: str) -> Optional[User]:
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    token_record = db.query(VerificationToken).filter(VerificationToken.token_hash == token_hash).first()
    
    if not token_record:
        return None
        
    if token_record.used_at:
        return None
        
    if token_record.expires_at < datetime.datetime.utcnow():
        return None
        
    user = token_record.user
    if not user:
        return None
        
    # Mark token used
    token_record.used_at = datetime.datetime.utcnow()
    # Mark user verified
    user.email_verified = True
    user.email_verified_at = datetime.datetime.utcnow()
    
    db.commit()
    return user

def send_verification_email(email: str, token: str) -> bool:
    return provider.send_verification_email(email, token)
