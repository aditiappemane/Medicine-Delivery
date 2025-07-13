from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import json
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserLogin, UserUpdate, UserResponse, 
    PhoneVerification, Token
)
from app.utils.auth import get_password_hash, verify_password, create_access_token
from app.utils.sms import (
    generate_verification_code, send_verification_sms, 
    store_verification_code, verify_phone_code
)
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with medical profile."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.phone == user_data.phone)
    ).first()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    db_user = User(
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role,
        device_token=user_data.device_token
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User registration failed"
        )

@router.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """User login with email and password."""
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile."""
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile and delivery address."""
    update_data = user_update.dict(exclude_unset=True)
    
    # Handle JSON fields
    if "allergies" in update_data and update_data["allergies"] is not None:
        update_data["allergies"] = json.dumps(update_data["allergies"])
    
    if "medical_conditions" in update_data and update_data["medical_conditions"] is not None:
        update_data["medical_conditions"] = json.dumps(update_data["medical_conditions"])
    
    # Update user fields
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    try:
        db.commit()
        db.refresh(current_user)
        return current_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile update failed"
        )

@router.post("/verify-phone")
def verify_phone_number(
    phone_verification: PhoneVerification,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify phone number with SMS code."""
    if current_user.phone != phone_verification.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number does not match user's phone"
        )
    
    if verify_phone_code(phone_verification.phone, phone_verification.verification_code):
        current_user.is_phone_verified = True
        db.commit()
        return {"message": "Phone number verified successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )

@router.post("/send-verification-code")
def send_phone_verification_code(
    phone: str,
    current_user: User = Depends(get_current_active_user)
):
    """Send verification code to user's phone number."""
    if current_user.phone != phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number does not match user's phone"
        )
    
    if current_user.is_phone_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is already verified"
        )
    
    # Generate and send verification code
    verification_code = generate_verification_code()
    store_verification_code(phone, verification_code)
    
    if send_verification_sms(phone, verification_code):
        return {"message": "Verification code sent successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification code"
        ) 