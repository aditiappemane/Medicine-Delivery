from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.database import get_db
from app.models.medicine import Medicine
from app.schemas.medicine import (
    MedicineCreate, MedicineUpdate, MedicineStockUpdate, MedicineResponse
)
from app.dependencies import get_current_admin_user, get_current_active_user

router = APIRouter(prefix="/medicines", tags=["medicines"])

@router.get("/", response_model=List[MedicineResponse])
def get_all_medicines(db: Session = Depends(get_db)):
    medicines = db.query(Medicine).all()
    return medicines

@router.post("/", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
def add_medicine(
    medicine: MedicineCreate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    db_medicine = Medicine(**medicine.dict())
    try:
        db.add(db_medicine)
        db.commit()
        db.refresh(db_medicine)
        return db_medicine
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to add medicine")

@router.put("/{id}", response_model=MedicineResponse)
def update_medicine(
    id: int,
    medicine_update: MedicineUpdate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    medicine = db.query(Medicine).filter(Medicine.id == id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    for field, value in medicine_update.dict(exclude_unset=True).items():
        setattr(medicine, field, value)
    try:
        db.commit()
        db.refresh(medicine)
        return medicine
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to update medicine")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medicine(
    id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    medicine = db.query(Medicine).filter(Medicine.id == id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db.delete(medicine)
    db.commit()
    return

@router.get("/search", response_model=List[MedicineResponse])
def search_medicines(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    prescription_required: Optional[bool] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Medicine)
    if q:
        query = query.filter(Medicine.name.ilike(f"%{q}%"))
    if category:
        query = query.filter(Medicine.category == category)
    if prescription_required is not None:
        query = query.filter(Medicine.prescription_required == prescription_required)
    if min_price is not None:
        query = query.filter(Medicine.price >= min_price)
    if max_price is not None:
        query = query.filter(Medicine.price <= max_price)
    return query.all()

@router.get("/{id}/alternatives", response_model=List[MedicineResponse])
def get_alternative_medicines(id: int, db: Session = Depends(get_db)):
    medicine = db.query(Medicine).filter(Medicine.id == id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    # Alternatives: same category, not the same id
    alternatives = db.query(Medicine).filter(
        Medicine.category == medicine.category,
        Medicine.id != id
    ).all()
    return alternatives

@router.patch("/{id}/stock", response_model=MedicineResponse)
def update_medicine_stock(
    id: int,
    stock_update: MedicineStockUpdate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    medicine = db.query(Medicine).filter(Medicine.id == id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    medicine.stock = stock_update.stock
    db.commit()
    db.refresh(medicine)
    return medicine 