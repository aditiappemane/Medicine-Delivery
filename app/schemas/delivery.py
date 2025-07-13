from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DeliveryPartnerResponse(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    is_available: bool
    status: str
    last_active: Optional[str]
    class Config:
        from_attributes = True

class PharmacyResponse(BaseModel):
    id: int
    name: str
    address: str
    latitude: Optional[float]
    longitude: Optional[float]
    is_active: bool
    class Config:
        from_attributes = True

class EmergencyDeliveryRequestCreate(BaseModel):
    medicine_id: int
    urgency: str
    delivery_address: str

class EmergencyDeliveryRequestResponse(BaseModel):
    id: int
    user_id: int
    medicine_id: int
    urgency: str
    status: str
    delivery_partner_id: Optional[int]
    pharmacy_id: Optional[int]
    delivery_address: str
    dynamic_price: float
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class DeliveryEstimateRequest(BaseModel):
    user_latitude: float
    user_longitude: float
    medicine_id: int

class DeliveryEstimateResponse(BaseModel):
    estimated_time_minutes: int
    estimated_distance_km: float
    dynamic_price: float
    partner_id: Optional[int]
    pharmacy_id: Optional[int]
    message: Optional[str] = None 