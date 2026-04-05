import enum
from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import Base

class RecordType(str, enum.Enum):
    INCOME = "Income"
    EXPENSE = "Expense"

class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(Enum(RecordType), nullable=False)
    category = Column(String, index=True, nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    notes = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Optional: establishing relationship for complex queries if needed later.
    # user = relationship("User")
