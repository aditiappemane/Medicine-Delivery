from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.dependencies import get_current_admin_user

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):
    """Get all medicine categories."""
    categories = db.query(Category).all()
    return categories

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    """Create a new medicine category (pharmacy admin only)."""
    db_category = Category(**category.dict())
    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

@router.put("/{id}", response_model=CategoryResponse)
def update_category(
    id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    """Update a medicine category (pharmacy admin only)."""
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    try:
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    """Delete a medicine category (pharmacy admin only)."""
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    db.delete(category)
    db.commit()
    return 