from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database Connection URL
# Using your credentials: root / NIVAK / churn_db
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:NIVAK@localhost:3306/churn_db"

# Create the SQLAlchemy engine
# pool_pre_ping=True helps maintain the connection to MySQL if it's idle
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True
)

# Create a SessionLocal class for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models to inherit from
Base = declarative_base()

# Dependency: This function ensures the database connection is closed after every request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()