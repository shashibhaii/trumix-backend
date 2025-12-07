from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from passlib.context import CryptContext
import getpass

# Password hashing config (same as auth.py)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_admin_user():
    db = SessionLocal()
    try:
        print("--- Create Admin User ---")
        name = input("Enter Name: ")
        email = input("Enter Email: ")
        password = getpass.getpass("Enter Password: ")
        confirm_password = getpass.getpass("Confirm Password: ")

        if password != confirm_password:
            print("Error: Passwords do not match.")
            return

        # Check if user exists
        existing_user = db.query(models.User).filter(models.User.email == email).first()
        if existing_user:
            print(f"Error: User with email {email} already exists.")
            return

        # Create new admin user
        hashed_password = get_password_hash(password)
        new_user = models.User(
            name=name,
            email=email,
            hashed_password=hashed_password,
            role=models.UserRole.admin
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"Success! Admin user '{name}' ({email}) created.")

    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
