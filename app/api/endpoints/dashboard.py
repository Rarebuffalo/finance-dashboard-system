from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.record import FinancialRecord, RecordType
from app.api.dependencies import get_current_user, RequireRole

router = APIRouter()

# ALL authenticated roles (Viewer, Analyst, Admin) can view dashboard summarizations.
@router.get("/summary", response_model=Dict[str, float])
async def read_dashboard_summary(
    current_user: User = Depends(RequireRole([UserRole.ADMIN, UserRole.ANALYST, UserRole.VIEWER])),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Retrieve high-level dashboard summaries: Total Income, Total Expenses, and Net Balance.
    """
    # Summing Income
    income_query = select(func.coalesce(func.sum(FinancialRecord.amount), 0)).where(
        FinancialRecord.type == RecordType.INCOME,
        FinancialRecord.is_deleted == False
    )
    income_result = await db.execute(income_query)
    total_income = income_result.scalar() or 0.0

    # Summing Expense
    expense_query = select(func.coalesce(func.sum(FinancialRecord.amount), 0)).where(
        FinancialRecord.type == RecordType.EXPENSE,
        FinancialRecord.is_deleted == False
    )
    expense_result = await db.execute(expense_query)
    total_expense = expense_result.scalar() or 0.0

    net_balance = total_income - total_expense

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": net_balance
    }


@router.get("/categories", response_model=List[Dict[str, Any]])
async def read_category_summary(
    current_user: User = Depends(RequireRole([UserRole.ADMIN, UserRole.ANALYST, UserRole.VIEWER])),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Groups financial records by category and type to show category-wise totals.
    """
    query = (
        select(
            FinancialRecord.category,
            FinancialRecord.type,
            func.sum(FinancialRecord.amount).label("total")
        )
        .where(FinancialRecord.is_deleted == False)
        .group_by(FinancialRecord.category, FinancialRecord.type)
    )
    result = await db.execute(query)
    
    category_totals = []
    for row in result.all():
        category_totals.append({
            "category": row.category,
            "type": row.type.value,
            "total": float(row.total)
        })
        
    return category_totals

@router.get("/recent", response_model=List[Dict[str, Any]])
async def read_recent_activity(
    current_user: User = Depends(RequireRole([UserRole.ADMIN, UserRole.ANALYST, UserRole.VIEWER])),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Retrieves the 5 most recent financial records for a high-level overview.
    """
    query = (
        select(FinancialRecord)
        .where(FinancialRecord.is_deleted == False)
        .order_by(FinancialRecord.date.desc())
        .limit(5)
    )
    result = await db.execute(query)
    records = result.scalars().all()
    
    recent = []
    for r in records:
        recent.append({
            "id": r.id,
            "amount": r.amount,
            "type": r.type.value,
            "category": r.category,
            "date": r.date.isoformat(),
            "notes": r.notes
        })
    return recent
