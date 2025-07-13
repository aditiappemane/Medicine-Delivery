from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class PrescriptionMedicine(Base):
    __tablename__ = "prescription_medicines"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False)
    medicine_name = Column(String, nullable=False)
    dosage = Column(String, nullable=True)
    frequency = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    quantity = Column(Integer, default=1)
    notes = Column(String, nullable=True)
    created_at = Column(String, default=func.now())

    # Relationships
    prescription = relationship("Prescription", back_populates="medicines")

    def __repr__(self):
        return f"<PrescriptionMedicine(id={self.id}, prescription_id={self.prescription_id}, medicine_name='{self.medicine_name}')>" 