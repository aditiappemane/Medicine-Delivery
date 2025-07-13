from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MedicineBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float
    stock: int = 0
    prescription_required: bool = False
    manufacturer: Optional[str] = None
    image_url: Optional[str] = None
    is_available: bool = True

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    prescription_required: Optional[bool] = None
    manufacturer: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None

class MedicineStockUpdate(BaseModel):
    stock: int

class MedicineResponse(MedicineBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MedicineSearchQuery(BaseModel):
    q: Optional[str] = None
    category: Optional[str] = None
    prescription_required: Optional[bool] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None 