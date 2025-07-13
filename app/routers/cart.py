from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.cart import Cart, CartItem
from app.models.medicine import Medicine
from app.models.prescription import Prescription
from app.schemas.cart import (
    CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse,
    PrescriptionValidationRequest, PrescriptionValidationResponse, CartValidationResponse
)
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/cart", tags=["cart"])

def get_or_create_cart(user_id: int, db: Session) -> Cart:
    """Get existing cart or create new one for user."""
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

@router.get("/", response_model=CartResponse)
def get_user_cart(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Get user's cart with prescription validation."""
    cart = get_or_create_cart(current_user.id, db)
    
    # Get cart items with medicine details
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    
    # Calculate totals and add medicine details
    total_items = 0
    total_amount = 0.0
    items_response = []
    
    for item in cart_items:
        medicine = db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
        if medicine:
            item_total = medicine.price * item.quantity
            total_items += item.quantity
            total_amount += item_total
            
            item_response = CartItemResponse(
                id=item.id,
                cart_id=item.cart_id,
                medicine_id=item.medicine_id,
                quantity=item.quantity,
                prescription_required=item.prescription_required,
                prescription_id=item.prescription_id,
                created_at=item.created_at,
                updated_at=item.updated_at,
                medicine_name=medicine.name,
                medicine_price=medicine.price,
                medicine_image_url=medicine.image_url,
                total_price=item_total
            )
            items_response.append(item_response)
    
    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=items_response,
        total_items=total_items,
        total_amount=total_amount,
        created_at=cart.created_at,
        updated_at=cart.updated_at
    )

@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_medicine_to_cart(
    cart_item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Add medicine to cart."""
    # Check if medicine exists
    medicine = db.query(Medicine).filter(Medicine.id == cart_item.medicine_id).first()
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found"
        )
    
    # Check if medicine is available
    if not medicine.is_available or medicine.stock < cart_item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medicine not available in requested quantity"
        )
    
    # Get or create cart
    cart = get_or_create_cart(current_user.id, db)
    
    # Check if medicine already in cart
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.medicine_id == cart_item.medicine_id
    ).first()
    
    if existing_item:
        # Update quantity
        existing_item.quantity += cart_item.quantity
        existing_item.prescription_required = medicine.prescription_required
        if cart_item.prescription_id:
            existing_item.prescription_id = cart_item.prescription_id
        db.commit()
        db.refresh(existing_item)
        item = existing_item
    else:
        # Create new cart item
        new_item = CartItem(
            cart_id=cart.id,
            medicine_id=cart_item.medicine_id,
            quantity=cart_item.quantity,
            prescription_required=medicine.prescription_required,
            prescription_id=cart_item.prescription_id
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        item = new_item
    
    # Return response with medicine details
    return CartItemResponse(
        id=item.id,
        cart_id=item.cart_id,
        medicine_id=item.medicine_id,
        quantity=item.quantity,
        prescription_required=item.prescription_required,
        prescription_id=item.prescription_id,
        created_at=item.created_at,
        updated_at=item.updated_at,
        medicine_name=medicine.name,
        medicine_price=medicine.price,
        medicine_image_url=medicine.image_url,
        total_price=medicine.price * item.quantity
    )

@router.put("/items/{item_id}", response_model=CartItemResponse)
def update_cart_item_quantity(
    item_id: int,
    cart_item_update: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Update cart item quantity."""
    # Get cart
    cart = get_or_create_cart(current_user.id, db)
    
    # Get cart item
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Check medicine availability
    medicine = db.query(Medicine).filter(Medicine.id == cart_item.medicine_id).first()
    if not medicine or medicine.stock < cart_item_update.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested quantity not available"
        )
    
    # Update quantity
    cart_item.quantity = cart_item_update.quantity
    db.commit()
    db.refresh(cart_item)
    
    return CartItemResponse(
        id=cart_item.id,
        cart_id=cart_item.cart_id,
        medicine_id=cart_item.medicine_id,
        quantity=cart_item.quantity,
        prescription_required=cart_item.prescription_required,
        prescription_id=cart_item.prescription_id,
        created_at=cart_item.created_at,
        updated_at=cart_item.updated_at,
        medicine_name=medicine.name,
        medicine_price=medicine.price,
        medicine_image_url=medicine.image_url,
        total_price=medicine.price * cart_item.quantity
    )

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_medicine_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Remove medicine from cart."""
    cart = get_or_create_cart(current_user.id, db)
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    db.delete(cart_item)
    db.commit()
    return

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Clear entire cart."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if cart:
        db.delete(cart)
        db.commit()
    return

@router.post("/validate-prescriptions", response_model=CartValidationResponse)
def validate_prescription_medicines_in_cart(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Validate prescription medicines in cart."""
    cart = get_or_create_cart(current_user.id, db)
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    
    valid_items = []
    invalid_items = []
    requires_prescription = []
    total_valid_amount = 0.0
    
    for item in cart_items:
        medicine = db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
        if not medicine:
            invalid_items.append({
                "item_id": item.id,
                "medicine_id": item.medicine_id,
                "reason": "Medicine not found"
            })
            continue
        
        # Check if prescription is required but not provided
        if medicine.prescription_required and not item.prescription_id:
            requires_prescription.append(item.id)
            continue
        
        # Check if prescription is provided and valid
        if item.prescription_id:
            prescription = db.query(Prescription).filter(
                Prescription.id == item.prescription_id,
                Prescription.user_id == current_user.id,
                Prescription.is_verified == True
            ).first()
            
            if not prescription:
                invalid_items.append({
                    "item_id": item.id,
                    "medicine_id": item.medicine_id,
                    "reason": "Invalid or unverified prescription"
                })
                continue
        
        # Check stock availability
        if medicine.stock < item.quantity:
            invalid_items.append({
                "item_id": item.id,
                "medicine_id": item.medicine_id,
                "reason": f"Insufficient stock. Available: {medicine.stock}"
            })
            continue
        
        valid_items.append(item.id)
        total_valid_amount += medicine.price * item.quantity
    
    return CartValidationResponse(
        valid_items=valid_items,
        invalid_items=invalid_items,
        requires_prescription=requires_prescription,
        total_valid_amount=total_valid_amount
    ) 