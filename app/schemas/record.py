from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from app.models.record import RecordType

class RecordBase(BaseModel):
    amount: float = Field(..., gt=0, description="The amount must be strictly greater than zero.")
    type: RecordType
    category: str = Field(..., min_length=1, max_length=100)
    date: Optional[datetime] = None
    notes: Optional[str] = None

class RecordCreate(RecordBase):
    pass

class RecordUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[RecordType] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    date: Optional[datetime] = None
    notes: Optional[str] = None

class RecordResponse(RecordBase):
    id: int
    user_id: int
    date: datetime

    # The ConfigDict allows Pydantic to read from SQLAlchemy objects (ORM mapping)
    model_config = ConfigDict(from_attributes=True)
