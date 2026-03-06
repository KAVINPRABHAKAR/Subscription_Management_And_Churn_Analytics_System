import random
import string
from datetime import datetime, timedelta
from app.database import SessionLocal, engine
from app import models

# Initialize session
db = SessionLocal()

# Configuration for realistic data
customer_names = [
    "TechNova Solutions", "Blue Horizon Inc", "Nexus Logistics", "Quantum Systems",
    "Apex Marketing", "Ironclad Security", "Summit Analytics", "Velocity SaaS",
    "Ember Media", "Starlight Retail", "Oasis Wellness", "Prism Consulting"
]

plans = ["Basic", "Pro", "Enterprise"]
fees = {"Basic": 10.0, "Pro": 30.0, "Enterprise": 100.0}
statuses = ["active", "active", "active", "cancelled"] 

def generate_random_phone():
    """Generates a professional looking US-style phone number."""
    return f"+1 ({random.randint(200, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"

def seed_data():
    print("🚀 Initializing Professional Seed Protocol...")
    
    # NOTE: If you haven't manually dropped the table in MySQL, 
    # run: db.execute("DROP TABLE subscriptions") here or in your SQL terminal.
    models.Base.metadata.create_all(bind=engine)

    # Clear any leftover data for a clean professional start
    db.query(models.Subscription).delete()

    for i in range(40):
        # Professional Metadata Generation
        base_name = random.choice(customer_names)
        safe_email_name = base_name.lower().replace(" ", ".")
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        
        plan = random.choice(plans)
        status = random.choice(statuses)
        
        # Chronology Logic
        random_days = random.randint(0, 180)
        signup_date = datetime.utcnow() - timedelta(days=random_days)
        
        new_sub = models.Subscription(
            customer_name=f"{base_name} #{i+1}",
            email=f"ops.{safe_email_name}_{i}@network-{random_suffix}.com", # New Field
            contact_phone=generate_random_phone(),                        # New Field
            company_address=f"{random.randint(100, 9999)} Innovation Blvd, Suite {random.randint(10, 500)}", # New Field
            plan_type=plan,
            monthly_fee=fees[plan],
            status=status,
            signup_date=signup_date,
            last_updated=datetime.utcnow()
        )
        db.add(new_sub)
    
    db.commit()
    print(f"✅ Success: 40 Professional Entities synchronized to the database.")

if __name__ == "__main__":
    seed_data()