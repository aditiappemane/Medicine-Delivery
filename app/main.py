from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import auth_router, medicines_router, categories_router, prescriptions_router, cart_router, orders_router, delivery_router, help_router
from app.database import engine
from app.models import User, Medicine, Category, Prescription, PrescriptionMedicine, Cart, CartItem, Order, OrderItem, DeliveryTracking, DeliveryProof, DeliveryPartner, Pharmacy, EmergencyDeliveryRequest
from app.config import settings
import os

# Create database tables
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

# Create FastAPI app
app = FastAPI(
    title="Medicine Delivery API",
    description="Quick Commerce Medicine Delivery Platform API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded images
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(auth_router)
app.include_router(medicines_router)
app.include_router(categories_router)
app.include_router(prescriptions_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(delivery_router)
app.include_router(help_router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Medicine Delivery API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"} 