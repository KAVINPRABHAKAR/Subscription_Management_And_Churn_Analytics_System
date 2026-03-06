from fastapi import FastAPI, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from . import models, database, analytics

# Initialize App
app = FastAPI(title="ChurnGuard Pro")

# Mount Static Files (CSS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize Templates
templates = Jinja2Templates(directory="app/templates")

# Create Database Tables on Startup
models.Base.metadata.create_all(bind=database.engine)

# Global fee structure for consistency across routes
FEE_STRUCTURE = {"Basic": 10.0, "Pro": 30.0, "Enterprise": 100.0}

# --- AUTHENTICATION LOGIC ---

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def handle_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    # SIMPLE MOCK AUTH (Admin credentials)
    if username == "admin" and password == "terminal2026":
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="terminal_session", value="authorized", httponly=True)
        return response
    
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "error": "INVALID CREDENTIALS // ACCESS DENIED"
    })

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("terminal_session")
    return response

# --- DASHBOARD ---

@app.get("/", response_class=HTMLResponse)
def read_dashboard(request: Request, db: Session = Depends(database.get_db)):
    """Main dashboard showing analytics and tier distribution."""
    if request.cookies.get("terminal_session") != "authorized":
        return RedirectResponse(url="/login")

    subscriptions = db.query(models.Subscription).all()
    stats = analytics.get_churn_stats(subscriptions)

    active_subs = [s for s in subscriptions if s.status == 'active']
    total_active = len(active_subs)

    if total_active > 0:
        basic_count = sum(1 for s in active_subs if s.plan_type.lower() == 'basic')
        pro_count = sum(1 for s in active_subs if s.plan_type.lower() == 'pro')
        ent_count = sum(1 for s in active_subs if s.plan_type.lower() == 'enterprise')

        stats["basic_pct"] = round((basic_count / total_active) * 100, 1)
        stats["pro_pct"] = round((pro_count / total_active) * 100, 1)
        stats["ent_pct"] = round((ent_count / total_active) * 100, 1)
    else:
        stats["basic_pct"] = stats["pro_pct"] = stats["ent_pct"] = 0

    return templates.TemplateResponse("dashboard.html", {"request": request, "stats": stats})

# --- CUSTOMER REGISTRY ---

@app.get("/customers")
def list_customers(request: Request, db: Session = Depends(database.get_db)):
    if request.cookies.get("terminal_session") != "authorized":
        return RedirectResponse(url="/login")

    customers = db.query(models.Subscription).all()
    return templates.TemplateResponse("customers.html", {"request": request, "customers": customers})

# --- PROVISIONING (CREATE) ---

@app.get("/add-customer")
def add_customer_page(request: Request):
    if request.cookies.get("terminal_session") != "authorized":
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("add_customer.html", {"request": request})

@app.post("/add-customer")
def handle_add_customer(
    customer_name: str = Form(...),
    email: str = Form(...),
    contact_phone: str = Form(None),
    company_address: str = Form(None),
    plan_type: str = Form(...),
    status: str = Form(...),
    db: Session = Depends(database.get_db)
):
    monthly_fee = FEE_STRUCTURE.get(plan_type, 0.0)
    new_subscription = models.Subscription(
        customer_name=customer_name, email=email, contact_phone=contact_phone,
        company_address=company_address, plan_type=plan_type, status=status, monthly_fee=monthly_fee
    )
    db.add(new_subscription)
    db.commit()
    return RedirectResponse(url="/customers?msg=updated", status_code=303)

# --- INSPECTION & CONFIGURATION ---

@app.get("/view/{customer_id}")
def view_customer(request: Request, customer_id: int, db: Session = Depends(database.get_db)):
    if request.cookies.get("terminal_session") != "authorized":
        return RedirectResponse(url="/login")
    customer = db.query(models.Subscription).filter(models.Subscription.id == customer_id).first()
    return templates.TemplateResponse("view_customer.html", {"request": request, "customer": customer}) if customer else RedirectResponse(url="/customers")

@app.get("/edit/{customer_id}")
def edit_customer_page(request: Request, customer_id: int, db: Session = Depends(database.get_db)):
    if request.cookies.get("terminal_session") != "authorized":
        return RedirectResponse(url="/login")
    customer = db.query(models.Subscription).filter(models.Subscription.id == customer_id).first()
    return templates.TemplateResponse("edit_customer.html", {"request": request, "customer": customer}) if customer else RedirectResponse(url="/customers")

@app.post("/edit/{customer_id}")
def handle_edit_customer(
    customer_id: int, customer_name: str = Form(...), email: str = Form(...),
    contact_phone: str = Form(None), company_address: str = Form(None),
    plan_type: str = Form(...), status: str = Form(...), db: Session = Depends(database.get_db)
):
    customer = db.query(models.Subscription).filter(models.Subscription.id == customer_id).first()
    if customer:
        customer.customer_name, customer.email = customer_name, email
        customer.contact_phone, customer.company_address = contact_phone, company_address
        customer.plan_type, customer.status = plan_type, status
        customer.monthly_fee = FEE_STRUCTURE.get(plan_type, 0.0)
        db.commit()
    return RedirectResponse(url="/customers?msg=updated", status_code=303)

@app.post("/delete/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(database.get_db)):
    customer = db.query(models.Subscription).filter(models.Subscription.id == customer_id).first()
    if customer:
        db.delete(customer)
        db.commit()
    return RedirectResponse(url="/customers", status_code=303)






