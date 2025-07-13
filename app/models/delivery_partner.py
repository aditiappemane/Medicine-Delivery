from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class DeliveryPartner(Base):
    __tablename__ = "delivery_partners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_available = Column(Boolean, default=True)
    current_order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    status = Column(String, default="available")  # available, on_delivery, offline
    last_active = Column(String, default=func.now())

    def __repr__(self):
        return f"<DeliveryPartner(id={self.id}, name='{self.name}', status='{self.status}')>" 