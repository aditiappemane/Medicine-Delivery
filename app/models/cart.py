from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    created_at = Column(String, default=func.now())
    updated_at = Column(String, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id})>"

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    prescription_required = Column(Boolean, default=False)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=True)
    created_at = Column(String, default=func.now())
    updated_at = Column(String, default=func.now(), onupdate=func.now())

    # Relationships
    cart = relationship("Cart", back_populates="items")
    medicine = relationship("Medicine")
    prescription = relationship("Prescription")

    def __repr__(self):
        return f"<CartItem(id={self.id}, cart_id={self.cart_id}, medicine_id={self.medicine_id}, quantity={self.quantity})>" 