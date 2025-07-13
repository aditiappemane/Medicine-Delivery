from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    phone: str
    first_name: str
    last_name: str
    role: str = "user"
    device_token: str = None
    
    @validator('phone')
    def validate_phone(cls, v):
        # Basic phone validation - can be enhanced based on country
        if not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Phone number must contain only digits, spaces, hyphens, or plus sign')
        return v

class UserCreate(UserBase):
    password: str
    role: str = "user"
    device_token: str = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    blood_group: Optional[str] = None
    allergies: Optional[List[str]] = None
    medical_conditions: Optional[List[str]] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    device_token: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PhoneVerification(BaseModel):
    phone: str
    verification_code: str

class UserResponse(BaseModel):
    id: int
    email: str
    phone: str
    first_name: str
    last_name: str
    role: str
    device_token: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    blood_group: Optional[str] = None
    allergies: Optional[List[str]] = None
    medical_conditions: Optional[List[str]] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_phone_verified: bool
    is_email_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 