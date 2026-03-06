from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from .database import Base
import datetime

class Subscription(Base):
    __tablename__ = "subscriptions"

    # Core Identity
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(150), nullable=False)
    
    # Professional Contact Details (New)
    email = Column(String(255), unique=True, index=True, nullable=False)
    contact_phone = Column(String(50), nullable=True)
    company_address = Column(Text, nullable=True) # Professional addition for billing
    
    # Subscription Metadata
    plan_type = Column(String(50), nullable=False)  # Basic, Pro, Enterprise
    monthly_fee = Column(Float, nullable=False)
    status = Column(String(20), default="active")    # active, cancelled
    
    # Chronology
    # Note: Using timezone-aware UTC is best practice for SaaS apps
    signup_date = Column(DateTime, default=datetime.datetime.utcnow)
    cancellation_date = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)