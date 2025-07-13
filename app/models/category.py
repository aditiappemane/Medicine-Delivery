from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.sql import func
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(String, default=func.now())
    updated_at = Column(String, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>" 