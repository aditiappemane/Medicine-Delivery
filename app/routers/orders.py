from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.order import Order, OrderItem
from app.models.cart import Cart, CartItem
from app.models.medicine import Medicine
from app.models.prescription import Prescription
from app.models.delivery import DeliveryTracking, DeliveryProof
from app.schemas.order import (
    OrderCreate, OrderResponse, OrderStatusUpdate, OrderItemResponse,
    DeliveryTrackingResponse, DeliveryProofCreate, DeliveryProofResponse
)
from app.dependencies import get_current_active_user
from app.utils.file_upload import save_uploaded_file, get_file_url
from app.utils.notifications import send_push_notification
from app.models.user import User

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order_from_cart(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Create order from cart with delivery details."""
    # Get user's cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate total and create order
    total_amount = 0.0
    order_items = []
    for item in cart_items:
        medicine = db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
        if not medicine or not medicine.is_available or medicine.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Medicine {item.medicine_id} not available")
        total_amount += medicine.price * item.quantity
        order_items.append({
            "medicine_id": item.medicine_id,
            "quantity": item.quantity,
            "price": medicine.price,
            "prescription_id": item.prescription_id
        })
        # Deduct stock
        medicine.stock -= item.quantity
    
    order = Order(
        user_id=current_user.id,
        delivery_address=order_data.delivery_address,
        status="pending",
        total_amount=total_amount
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Add order items
    for oi in order_items:
        order_item = OrderItem(
            order_id=order.id,
            medicine_id=oi["medicine_id"],
            quantity=oi["quantity"],
            price=oi["price"],
            prescription_id=oi["prescription_id"]
        )
        db.add(order_item)
    db.commit()
    
    # Clear cart
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.delete(cart)
    db.commit()
    
    # Create delivery tracking
    tracking = DeliveryTracking(order_id=order.id, current_status="pending")
    db.add(tracking)
    db.commit()
    
    # Prepare response
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    items_response = [OrderItemResponse(
        id=oi.id,
        medicine_id=oi.medicine_id,
        quantity=oi.quantity,
        price=oi.price,
        prescription_id=oi.prescription_id,
        medicine_name=db.query(Medicine).filter(Medicine.id == oi.medicine_id).first().name,
        medicine_image_url=db.query(Medicine).filter(Medicine.id == oi.medicine_id).first().image_url
    ) for oi in items]
    
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        delivery_address=order.delivery_address,
        status=order.status,
        total_amount=order.total_amount,
        items=items_response,
        created_at=order.created_at,
        updated_at=order.updated_at
    )

@router.get("/", response_model=List[OrderResponse])
def get_user_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Get user's orders with delivery status."""
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()
    responses = []
    for order in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        items_response = [OrderItemResponse(
            id=oi.id,
            medicine_id=oi.medicine_id,
            quantity=oi.quantity,
            price=oi.price,
            prescription_id=oi.prescription_id,
            medicine_name=db.query(Medicine).filter(Medicine.id == oi.medicine_id).first().name,
            medicine_image_url=db.query(Medicine).filter(Medicine.id == oi.medicine_id).first().image_url
        ) for oi in items]
        responses.append(OrderResponse(
            id=order.id,
            user_id=order.user_id,
            delivery_address=order.delivery_address,
            status=order.status,
            total_amount=order.total_amount,
            items=items_response,
            created_at=order.created_at,
            updated_at=order.updated_at
        ))
    return responses

@router.get("/{id}", response_model=OrderResponse)
def get_order_details(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Get specific order details."""
    order = db.query(Order).filter(Order.id == id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    items_response = [OrderItemResponse(
        id=oi.id,
        medicine_id=oi.medicine_id,
        quantity=oi.quantity,
        price=oi.price,
        prescription_id=oi.prescription_id,
        medicine_name=db.query(Medicine).filter(Medicine.id == oi.medicine_id).first().name,
        medicine_image_url=db.query(Medicine).filter(Medicine.id == oi.medicine_id).first().image_url
    ) for oi in items]
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        delivery_address=order.delivery_address,
        status=order.status,
        total_amount=order.total_amount,
        items=items_response,
        created_at=order.created_at,
        updated_at=order.updated_at
    )

@router.patch("/{id}/status", response_model=OrderResponse)
def update_order_status(
    id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Update order status (pharmacy/delivery partner)."""
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status_update.status
    db.commit()
    db.refresh(order)
    # Update tracking
    tracking = db.query(DeliveryTracking).filter(DeliveryTracking.order_id == id).first()
    if tracking:
        tracking.current_status = status_update.status
        tracking.last_updated = datetime.utcnow()
        db.commit()
    # Send push notification to user
    user = db.query(User).filter(User.id == order.user_id).first()
    if user and user.device_token:
        send_push_notification(user.device_token, "Order Update", f"Your order #{order.id} status: {order.status}")
    # Prepare response
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    items_response = [OrderItemResponse(
        id=oi.id,
        medicine_id=oi.medicine_id,
        quantity=oi.quantity,
        price=oi.price,
        prescription_id=oi.prescription_id,
        medicine_name=db.query(Medicine).filter(Medicine.id == oi.medicine_id).first().name,
        medicine_image_url=db.query(Medicine).filter(Medicine.id == oi.medicine_id).first().image_url
    ) for oi in items]
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        delivery_address=order.delivery_address,
        status=order.status,
        total_amount=order.total_amount,
        items=items_response,
        created_at=order.created_at,
        updated_at=order.updated_at
    )

@router.get("/{id}/track", response_model=DeliveryTrackingResponse)
def track_order(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Real-time order tracking."""
    tracking = db.query(DeliveryTracking).filter(DeliveryTracking.order_id == id).first()
    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")
    return tracking

@router.post("/{id}/delivery-proof", response_model=DeliveryProofResponse)
async def upload_delivery_proof(
    id: int,
    file: Optional[UploadFile] = File(None),
    signature: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Upload delivery confirmation (image or signature)."""
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    image_url = None
    if file:
        file_path = save_uploaded_file(file, "delivery_proofs")
        image_url = get_file_url(file_path)
    proof = db.query(DeliveryProof).filter(DeliveryProof.order_id == id).first()
    if not proof:
        proof = DeliveryProof(order_id=id, image_url=image_url, signature=signature, delivered_at=datetime.utcnow())
        db.add(proof)
    else:
        proof.image_url = image_url
        proof.signature = signature
        proof.delivered_at = datetime.utcnow()
    db.commit()
    db.refresh(proof)
    # Send push notification to user
    user = db.query(User).filter(User.id == order.user_id).first()
    if user and user.device_token:
        send_push_notification(user.device_token, "Order Delivered", f"Your order #{order.id} has been delivered.")
    return proof 