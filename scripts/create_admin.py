import os
import sys
import getpass
import datetime

# Add backend dir to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.db.session import SessionLocal
from app.models.user import User, Role
from app.core.security import get_password_hash

def main():
    print("Administrator setup")
    print("-------------------")
    
    email_input = input("Admin email [admin@modelsentinel.local]: ").strip()
    email = email_input if email_input else "admin@modelsentinel.local"
    
    if "@" not in email or "." not in email:
        print("Invalid email format.")
        sys.exit(1)
        
    password = getpass.getpass("New admin password: ")
    if not password:
        print("Password is required.")
        sys.exit(1)
        
    if len(password) < 8:
        print("Password must be at least 8 characters long.")
        sys.exit(1)
        
    confirm_password = getpass.getpass("Confirm password: ")
    if password != confirm_password:
        print("Passwords do not match.")
        sys.exit(1)
        
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"Administrator with email {email} already exists.")
            reset = input("Reset password? [y/N]: ").strip().lower()
            if reset == 'y':
                user.hashed_password = get_password_hash(password)
                user.role = Role.ADMIN
                user.email_verified = True
                user.email_verified_at = datetime.datetime.utcnow()
                db.commit()
                print("Administrator password reset successfully.")
            else:
                print("Aborted.")
            sys.exit(0)
                
        # Create new admin user
        new_admin = User(
            email=email,
            full_name="Administrator",
            hashed_password=get_password_hash(password),
            role=Role.ADMIN,
            is_active=True,
            email_verified=True,
            email_verified_at=datetime.datetime.utcnow()
        )
        db.add(new_admin)
        db.commit()
        print("\nAdministrator created successfully.")
    except Exception as e:
        print(f"Error creating administrator: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
