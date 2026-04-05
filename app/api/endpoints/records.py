from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.record import FinancialRecord, RecordType
from app.schemas.record import RecordCreate, RecordUpdate, RecordResponse
from app.api.dependencies import get_current_user, RequireRole

router = APIRouter()

# CREATE: Only ADMIN can create records
@router.post("/", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
async def create_record(
    record_in: RecordCreate,
    current_user: User = Depends(RequireRole([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new financial record. Only permitted to Admins.
    """
    record_data = record_in.model_dump()
    new_record = FinancialRecord(**record_data, user_id=current_user.id)
    
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    return new_record

# READ ALL: Admin and Analyst
from datetime import datetime

@router.get("/", response_model=List[RecordResponse])
async def read_records(
    skip: int = 0,
    limit: int = 100,
    type: Optional[RecordType] = Query(None, description="Filter by INCOME or EXPENSE"),
    category: Optional[str] = Query(None, description="Filter by category string"),
    start_date: Optional[datetime] = Query(None, description="Filter records from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter records up to this date"),
    current_user: User = Depends(RequireRole([UserRole.ADMIN, UserRole.ANALYST])),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Retrieve all financial records. Supports pagination and filtering. 
    Accessible by Admins and Analysts.
    """
    query = select(FinancialRecord).where(FinancialRecord.is_deleted == False)
    
    if type:
        query = query.where(FinancialRecord.type == type)
    if category:
        query = query.where(FinancialRecord.category.ilike(f"%{category}%"))
    if start_date:
        query = query.where(FinancialRecord.date >= start_date)
    if end_date:
        query = query.where(FinancialRecord.date <= end_date)
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    records = result.scalars().all()
    return records

# READ ONE
@router.get("/{record_id}", response_model=RecordResponse)
async def read_record(
    record_id: int,
    current_user: User = Depends(RequireRole([UserRole.ADMIN, UserRole.ANALYST])),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Retrieve a specific record by ID. Access: Admins and Analysts.
    """
    result = await db.execute(
        select(FinancialRecord).where(
            FinancialRecord.id == record_id, 
            FinancialRecord.is_deleted == False
        )
    )
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

# UPDATE: Only ADMIN
@router.put("/{record_id}", response_model=RecordResponse)
async def update_record(
    record_id: int,
    record_in: RecordUpdate,
    current_user: User = Depends(RequireRole([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update a specific record. Only Admins.
    """
    result = await db.execute(
        select(FinancialRecord).where(
            FinancialRecord.id == record_id, 
            FinancialRecord.is_deleted == False
        )
    )
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    update_data = record_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
        
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record

# DELETE: Only ADMIN
@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(
    record_id: int,
    current_user: User = Depends(RequireRole([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific record. Only Admins.
    """
    result = await db.execute(
        select(FinancialRecord).where(
            FinancialRecord.id == record_id, 
            FinancialRecord.is_deleted == False
        )
    )
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    record.is_deleted = True
    db.add(record)
    await db.commit()
