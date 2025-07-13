from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CartItemBase(BaseModel):
    medicine_id: int
    quantity: int = 1
    prescription_id: Optional[int] = None

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    cart_id: int
    medicine_id: int
    quantity: int
    prescription_required: bool
    prescription_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    # Medicine details
    medicine_name: Optional[str] = None
    medicine_price: Optional[float] = None
    medicine_image_url: Optional[str] = None
    
    # Calculated fields
    total_price: Optional[float] = None

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse] = []
    total_items: int = 0
    total_amount: float = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PrescriptionValidationRequest(BaseModel):
    prescription_id: int

class PrescriptionValidationResponse(BaseModel):
    prescription_id: int
    is_valid: bool
    message: str
    medicines: List[str] = []

class CartValidationResponse(BaseModel):
    valid_items: List[int] = []
    invalid_items: List[dict] = []
    requires_prescription: List[int] = []
    total_valid_amount: float = 0.0 