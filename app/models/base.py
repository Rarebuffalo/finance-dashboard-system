from sqlalchemy.orm import declarative_base

# The declarative_base() object acts as a catalog.
# Every database model we create (like User or FinanceRecord) will inherit from this Base.
# Later, Alembic (our migration tool) will inspect this Base to see our schema 
# and automatically generate SQL scripts to build the tables in PostgreSQL.
Base = declarative_base() 
