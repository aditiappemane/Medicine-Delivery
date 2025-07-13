from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class OrderItemBase(BaseModel):
    medicine_id: int
    quantity: int
    price: float
    prescription_id: Optional[int] = None

class OrderItemResponse(OrderItemBase):
    id: int
    medicine_name: Optional[str] = None
    medicine_image_url: Optional[str] = None
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    delivery_address: str

class OrderResponse(BaseModel):
    id: int
    user_id: int
    delivery_address: str
    status: str
    total_amount: float
    items: List[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str

class DeliveryTrackingResponse(BaseModel):
    order_id: int
    current_status: str
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    last_updated: datetime
    class Config:
        from_attributes = True

class DeliveryProofCreate(BaseModel):
    image_url: Optional[str] = None
    signature: Optional[str] = None

class DeliveryProofResponse(BaseModel):
    order_id: int
    image_url: Optional[str] = None
    signature: Optional[str] = None
    delivered_at: datetime
    class Config:
        from_attributes = True 