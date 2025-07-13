from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class EmergencyDeliveryRequest(Base):
    __tablename__ = "emergency_delivery_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    urgency = Column(String, default="high")  # high, critical
    status = Column(String, default="pending")  # pending, assigned, completed, cancelled
    delivery_partner_id = Column(Integer, ForeignKey("delivery_partners.id"), nullable=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id"), nullable=True)
    delivery_address = Column(Text, nullable=False)
    dynamic_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<EmergencyDeliveryRequest(id={self.id}, user_id={self.user_id}, status='{self.status}')>" 