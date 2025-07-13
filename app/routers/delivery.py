from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

from app.database import get_db
from app.models.delivery_partner import DeliveryPartner
from app.models.pharmacy import Pharmacy
from app.models.medicine import Medicine
from app.models.emergency_delivery import EmergencyDeliveryRequest
from app.schemas.delivery import (
    DeliveryPartnerResponse, PharmacyResponse, EmergencyDeliveryRequestCreate, EmergencyDeliveryRequestResponse,
    DeliveryEstimateRequest, DeliveryEstimateResponse
)
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/delivery", tags=["delivery"])

# Haversine formula for distance in km
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

@router.get("/estimate", response_model=DeliveryEstimateResponse)
def get_delivery_estimate(
    user_latitude: float,
    user_longitude: float,
    medicine_id: int,
    db: Session = Depends(get_db)
):
    """Get delivery time estimate based on user location, partner, and pharmacy."""
    # Find pharmacies with stock
    pharmacies = db.query(Pharmacy).filter(Pharmacy.is_active == True).all()
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine or not medicine.is_available or medicine.stock < 1:
        return DeliveryEstimateResponse(
            estimated_time_minutes=0,
            estimated_distance_km=0.0,
            dynamic_price=0.0,
            message="Medicine not available"
        )
    # Find nearest pharmacy with stock
    best_pharmacy = None
    min_distance = float('inf')
    for pharmacy in pharmacies:
        dist = haversine(user_latitude, user_longitude, pharmacy.latitude, pharmacy.longitude)
        if dist < min_distance:
            min_distance = dist
            best_pharmacy = pharmacy
    # Find nearest available delivery partner
    partners = db.query(DeliveryPartner).filter(DeliveryPartner.is_available == True).all()
    best_partner = None
    min_partner_distance = float('inf')
    for partner in partners:
        dist = haversine(best_pharmacy.latitude, best_pharmacy.longitude, partner.latitude, partner.longitude)
        if dist < min_partner_distance:
            min_partner_distance = dist
            best_partner = partner
    # Estimate time: 2 min/km, min 10, max 30
    estimated_time = min(max(int((min_distance + min_partner_distance) * 2), 10), 30)
    # Dynamic pricing: base + urgency
    dynamic_price = medicine.price * (1.2 if estimated_time <= 15 else 1.0)
    return DeliveryEstimateResponse(
        estimated_time_minutes=estimated_time,
        estimated_distance_km=round(min_distance + min_partner_distance, 2),
        dynamic_price=round(dynamic_price, 2),
        partner_id=best_partner.id if best_partner else None,
        pharmacy_id=best_pharmacy.id if best_pharmacy else None,
        message="Estimate calculated"
    )

@router.get("/partners", response_model=List[DeliveryPartnerResponse])
def get_delivery_partners(db: Session = Depends(get_db)):
    """Get available delivery partners."""
    partners = db.query(DeliveryPartner).filter(DeliveryPartner.is_available == True).all()
    return partners

@router.post("/emergency", response_model=EmergencyDeliveryRequestResponse, status_code=status.HTTP_201_CREATED)
def create_emergency_delivery(
    req: EmergencyDeliveryRequestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Create emergency medicine delivery request."""
    # Find nearest pharmacy with stock
    pharmacies = db.query(Pharmacy).filter(Pharmacy.is_active == True).all()
    medicine = db.query(Medicine).filter(Medicine.id == req.medicine_id).first()
    if not medicine or not medicine.is_available or medicine.stock < 1:
        raise HTTPException(status_code=400, detail="Medicine not available")
    best_pharmacy = None
    min_distance = float('inf')
    for pharmacy in pharmacies:
        dist = 0  # Assume user provides pharmacy or use location if available
        if dist < min_distance:
            min_distance = dist
            best_pharmacy = pharmacy
    # Find available partner
    partners = db.query(DeliveryPartner).filter(DeliveryPartner.is_available == True).all()
    best_partner = partners[0] if partners else None
    # Dynamic pricing
    dynamic_price = medicine.price * (1.5 if req.urgency == "critical" else 1.2)
    # Create request
    emergency = EmergencyDeliveryRequest(
        user_id=current_user.id,
        medicine_id=req.medicine_id,
        urgency=req.urgency,
        status="pending",
        delivery_partner_id=best_partner.id if best_partner else None,
        pharmacy_id=best_pharmacy.id if best_pharmacy else None,
        delivery_address=req.delivery_address,
        dynamic_price=dynamic_price
    )
    db.add(emergency)
    db.commit()
    db.refresh(emergency)
    return emergency

@router.get("/nearby-pharmacies", response_model=List[PharmacyResponse])
def get_nearby_pharmacies(
    user_latitude: float,
    user_longitude: float,
    medicine_id: int,
    db: Session = Depends(get_db)
):
    """Find nearby pharmacies with stock for a medicine."""
    pharmacies = db.query(Pharmacy).filter(Pharmacy.is_active == True).all()
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine or not medicine.is_available or medicine.stock < 1:
        return []
    # Sort pharmacies by distance
    pharmacies_with_distance = [
        (pharmacy, haversine(user_latitude, user_longitude, pharmacy.latitude, pharmacy.longitude))
        for pharmacy in pharmacies
    ]
    pharmacies_with_distance.sort(key=lambda x: x[1])
    # Return top 5 nearby pharmacies
    return [pharmacy for pharmacy, dist in pharmacies_with_distance[:5]] 