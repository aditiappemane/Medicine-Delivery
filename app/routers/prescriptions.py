from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.prescription import Prescription
from app.models.prescription_medicine import PrescriptionMedicine
from app.schemas.prescription import (
    PrescriptionCreate, PrescriptionVerify, PrescriptionResponse, 
    PrescriptionWithMedicinesResponse, PrescriptionMedicineResponse
)
from app.dependencies import get_current_active_user, get_current_pharmacist_user
from app.utils.file_upload import save_uploaded_file, validate_image_file, get_file_url

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])

@router.post("/upload", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
async def upload_prescription(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Upload prescription image."""
    
    # Validate file
    if not validate_image_file(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file"
        )
    
    # Save file
    try:
        file_path = save_uploaded_file(file, "prescriptions")
        image_url = get_file_url(file_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save prescription image: {str(e)}"
        )
    
    # Create prescription record
    prescription_data = {
        "user_id": current_user.id,
        "image_url": image_url,
        "description": description
    }
    
    db_prescription = Prescription(**prescription_data)
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    
    return db_prescription

@router.get("/", response_model=List[PrescriptionResponse])
def get_user_prescriptions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Get user's prescriptions."""
    prescriptions = db.query(Prescription).filter(
        Prescription.user_id == current_user.id
    ).order_by(Prescription.created_at.desc()).all()
    return prescriptions

@router.get("/{id}", response_model=PrescriptionWithMedicinesResponse)
def get_prescription_details(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Get specific prescription details."""
    prescription = db.query(Prescription).filter(
        Prescription.id == id,
        Prescription.user_id == current_user.id
    ).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    return prescription

@router.put("/{id}/verify", response_model=PrescriptionResponse)
def verify_prescription(
    id: int,
    verification: PrescriptionVerify,
    db: Session = Depends(get_db),
    pharmacist=Depends(get_current_pharmacist_user)
):
    """Verify prescription (pharmacist only)."""
    prescription = db.query(Prescription).filter(Prescription.id == id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    if prescription.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prescription already verified"
        )
    
    # Update prescription
    prescription.is_verified = verification.status == "verified"
    prescription.verified_by = pharmacist.id
    prescription.verified_at = datetime.utcnow()
    prescription.status = verification.status
    prescription.notes = verification.notes
    
    db.commit()
    db.refresh(prescription)
    
    return prescription

@router.get("/{id}/medicines", response_model=List[PrescriptionMedicineResponse])
def get_prescription_medicines(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Get medicines from prescription."""
    # Check if prescription exists and belongs to user
    prescription = db.query(Prescription).filter(
        Prescription.id == id,
        Prescription.user_id == current_user.id
    ).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    # Get medicines from prescription
    medicines = db.query(PrescriptionMedicine).filter(
        PrescriptionMedicine.prescription_id == id
    ).all()
    
    return medicines 