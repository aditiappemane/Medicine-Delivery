from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Pharmacy(Base):
    __tablename__ = "pharmacies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(Text, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=func.now())
    updated_at = Column(String, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Pharmacy(id={self.id}, name='{self.name}')>" 