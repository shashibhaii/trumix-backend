from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import random
import string
from .. import models, schemas, database

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

# Security Config
SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token", auto_error=False)

# Utils
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme_optional), db: Session = Depends(database.get_db)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        token_data = schemas.TokenData(email=email)
    except JWTError:
        return None
    
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    return user

# Endpoints

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Check if user exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        phone=user.phone,
        role=models.UserRole.user
    )
        
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send welcome email
    try:
        from ..services.email_service import send_welcome_email
        email_data = {
            'email': new_user.email,
            'name': new_user.name
        }
        send_welcome_email(email_data)
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send welcome email: {str(e)}")
        # Don't fail registration if email fails
    
    return new_user

@router.post("/send-otp")
def send_otp(request: schemas.OTPRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.phone == request.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this phone number not found")
        
    # Generate OTP
    otp = str(random.randint(100000, 999999))
    
    # Save OTP to DB
    user.otp = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    
    # Send OTP (Mock)
    print(f"--- OTP for {request.phone}: {otp} ---")
    
    return {"message": "OTP sent successfully"}

@router.post("/login-otp", response_model=schemas.Token)
def login_otp(request: schemas.OTPLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.phone == request.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not user.otp or user.otp != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    if user.otp_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")
        
    # Clear OTP
    user.otp = None
    user.otp_expiry = None
    db.commit()
    
    # Generate Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role.value,
        "user": user
    }

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid credentials")
    
    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=403, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role.value,
        "user": user
    }

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid credentials")
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=403, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role.value,
        "user": user
    }
