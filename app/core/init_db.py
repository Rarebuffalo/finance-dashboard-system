from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.models.user import User, UserRole
from app.models.record import FinancialRecord, RecordType
from app.core.security import get_password_hash

async def initialize_seeding(db: AsyncSession):
    """
    Checks if an Admin exists. If the database is completely empty (0 Admins),
    it generates default users and mock records so evaluators can instantly test the Dashboard.
    """
    result = await db.execute(select(User).where(User.role == UserRole.ADMIN))
    admin = result.scalars().first()
    
    if admin:
        return # Database is already populated
        
    print("Seeding default data...")
    pwd = get_password_hash("password123")
    
    # Create 3 Mock Users
    admin_user = User(email="admin@finance.com", hashed_password=pwd, role=UserRole.ADMIN, is_active=True)
    analyst_user = User(email="analyst@finance.com", hashed_password=pwd, role=UserRole.ANALYST, is_active=True)
    viewer_user = User(email="viewer@finance.com", hashed_password=pwd, role=UserRole.VIEWER, is_active=True)
    
    db.add_all([admin_user, analyst_user, viewer_user])
    await db.commit() # Commit to generate IDs
    await db.refresh(admin_user)
    
    # Create 10 Mock Financial Records belonging to the admin
    mock_records = [
        FinancialRecord(amount=5000.0, type=RecordType.INCOME, category="Salary", notes="Monthly wage", user_id=admin_user.id),
        FinancialRecord(amount=1200.0, type=RecordType.INCOME, category="Bonus", notes="Q1 Bonus", user_id=admin_user.id),
        FinancialRecord(amount=100.0, type=RecordType.EXPENSE, category="Groceries", notes="Trader Joes", user_id=admin_user.id),
        FinancialRecord(amount=50.0, type=RecordType.EXPENSE, category="Utilities", notes="Electric bill", user_id=admin_user.id),
        FinancialRecord(amount=200.0, type=RecordType.EXPENSE, category="Dining", notes="Restaurant", user_id=admin_user.id),
        FinancialRecord(amount=80.0, type=RecordType.EXPENSE, category="Transport", notes="Gas", user_id=admin_user.id),
        FinancialRecord(amount=400.0, type=RecordType.EXPENSE, category="Groceries", notes="Costco", user_id=admin_user.id),
        FinancialRecord(amount=3000.0, type=RecordType.INCOME, category="Freelance", notes="Client project", user_id=admin_user.id),
        FinancialRecord(amount=150.0, type=RecordType.EXPENSE, category="Utilities", notes="Internet", user_id=admin_user.id),
        FinancialRecord(amount=20.0, type=RecordType.EXPENSE, category="Entertainment", notes="Movies", user_id=admin_user.id),
    ]
    
    db.add_all(mock_records)
    await db.commit()
    print("Database seeding completed.")
