from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PrescriptionBase(BaseModel):
    description: Optional[str] = None

class PrescriptionCreate(PrescriptionBase):
    pass

class PrescriptionVerify(BaseModel):
    status: str  # "verified" or "rejected"
    notes: Optional[str] = None

class PrescriptionMedicineResponse(BaseModel):
    id: int
    medicine_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    quantity: int
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PrescriptionResponse(BaseModel):
    id: int
    user_id: int
    image_url: str
    description: Optional[str] = None
    is_verified: bool
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PrescriptionWithMedicinesResponse(PrescriptionResponse):
    medicines: List[PrescriptionMedicineResponse] = [] 