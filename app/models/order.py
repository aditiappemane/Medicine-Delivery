from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    delivery_address = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending, confirmed, dispatched, delivered, cancelled
    total_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    tracking = relationship("DeliveryTracking", back_populates="order", uselist=False)
    delivery_proof = relationship("DeliveryProof", back_populates="order", uselist=False)

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, status='{self.status}')>"

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float, default=0.0)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    order = relationship("Order", back_populates="items")
    medicine = relationship("Medicine")
    prescription = relationship("Prescription")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, medicine_id={self.medicine_id}, quantity={self.quantity})>" 