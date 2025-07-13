from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    
    # Medical Profile
    date_of_birth = Column(DateTime, nullable=True)
    blood_group = Column(String, nullable=True)
    allergies = Column(Text, nullable=True)  # JSON string of allergies
    medical_conditions = Column(Text, nullable=True)  # JSON string of conditions
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    
    # Delivery Address
    address_line1 = Column(String, nullable=True)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Verification
    is_phone_verified = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # User role: 'user' or 'admin'
    role = Column(String, default='user', nullable=False)
    
    # Device token for push notifications
    device_token = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    prescriptions = relationship("Prescription", back_populates="user", foreign_keys="Prescription.user_id")
    cart = relationship("Cart", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', phone='{self.phone}')>" 