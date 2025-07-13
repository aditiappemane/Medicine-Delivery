#!/usr/bin/env python3
"""
Database initialization script for Medicine Delivery API
"""

from app.database import engine
from app.models import User, Medicine, Category, Prescription, PrescriptionMedicine, Cart, CartItem, Order, OrderItem, DeliveryTracking, DeliveryProof, DeliveryPartner, Pharmacy, EmergencyDeliveryRequest
from app.utils.auth import get_password_hash

def init_database():
    """Initialize the database and create tables"""
    print("Creating database tables...")
    
    # Create all tables
    User.metadata.create_all(bind=engine)
    Medicine.metadata.create_all(bind=engine)
    Category.metadata.create_all(bind=engine)
    Prescription.metadata.create_all(bind=engine)
    PrescriptionMedicine.metadata.create_all(bind=engine)
    Cart.metadata.create_all(bind=engine)
    CartItem.metadata.create_all(bind=engine)
    Order.metadata.create_all(bind=engine)
    OrderItem.metadata.create_all(bind=engine)
    DeliveryTracking.metadata.create_all(bind=engine)
    DeliveryProof.metadata.create_all(bind=engine)
    DeliveryPartner.metadata.create_all(bind=engine)
    Pharmacy.metadata.create_all(bind=engine)
    EmergencyDeliveryRequest.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")
    print("You can now start the application with: python run.py")

if __name__ == "__main__":
    init_database() 