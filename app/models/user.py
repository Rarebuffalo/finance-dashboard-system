import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.models.base import Base

class UserRole(str, enum.Enum):
    """
    Defining roles using Python Enums.
    This guarantees that the role is strictly one of these three strings
    throughout the entire application lifecycle (Database -> Business Logic -> JSON).
    """
    VIEWER = "Viewer"    # Read-only access to dashboard data
    ANALYST = "Analyst"  # Can view records and generate insights
    ADMIN = "Admin"      # Full system access (create/update/delete)

class User(Base):
    """
    SQLAlchemy Model representing the 'users' table in PostgreSQL.
    Subclassing `Base` automatically detects this structure for Alembic migrations.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # email is nullable=False because it's required. index=True for fast DB lookups.
    email = Column(String, unique=True, index=True, nullable=False)
    # We NEVER store plain text passwords. Only the hashed representation.
    hashed_password = Column(String, nullable=False)
    
    # We enforce the UserRole enum here
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True)
