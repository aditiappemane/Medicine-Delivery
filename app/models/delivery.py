from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class DeliveryTracking(Base):
    __tablename__ = "delivery_tracking"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    current_status = Column(String, default="pending")
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="tracking")

    def __repr__(self):
        return f"<DeliveryTracking(order_id={self.order_id}, status='{self.current_status}')>"

class DeliveryProof(Base):
    __tablename__ = "delivery_proofs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    image_url = Column(String, nullable=True)
    signature = Column(Text, nullable=True)
    delivered_at = Column(DateTime, default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="delivery_proof")

    def __repr__(self):
        return f"<DeliveryProof(order_id={self.order_id})>" 