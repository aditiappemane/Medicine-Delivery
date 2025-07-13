from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True, index=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    prescription_required = Column(Boolean, default=False)
    manufacturer = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(String, default=func.now())
    updated_at = Column(String, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Medicine(id={self.id}, name='{self.name}')>" 