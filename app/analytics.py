import pandas as pd
import numpy as np
from datetime import datetime

def get_churn_stats(subscriptions):
    """
    Finalized Analytics Engine:
    Processes raw MySQL data into high-level business intelligence using Pandas.
    """
    current_time = datetime.utcnow()
    
    # 1. Structured Data Extraction
    data = [
        {
            "status": s.status, 
            "fee": s.monthly_fee,
            "plan": s.plan_type,
            "signup_date": s.signup_date
        } 
        for s in subscriptions
    ]
    
    # Handle empty database state
    if not data:
        return {
            "rate": 0, "mrr": 0, "active": 0, 
            "arpu": 0, "annual_projections": 0, "high_risk_count": 0
        }

    # 2. DataFrame Creation
    df = pd.DataFrame(data)
    
    # 3. Core Metric Calculations
    total_count = len(df)
    active_mask = df['status'] == 'active'
    active_df = df[active_mask].copy()
    
    cancelled_count = len(df[df['status'] == 'cancelled'])
    churn_rate = (cancelled_count / total_count) * 100
    
    # MRR Calculation
    mrr = active_df['fee'].sum()
    
    # 4. NumPy-Powered Advanced Metrics
    # ARPU (Average Revenue Per User)
    arpu = np.mean(active_df['fee']) if not active_df.empty else 0
    
    # Annual Projection (Run Rate)
    arr = mrr * 12

    # 5. Predictive Risk Scoring (The Professional Edge)
    # Calculate days since signup for each active customer
    if not active_df.empty:
        active_df['tenure'] = (current_time - pd.to_datetime(active_df['signup_date'])).dt.days
        
        # Identify "High Risk" as customers in their first 30 days (Onboarding phase)
        high_risk_mask = active_df['tenure'] <= 30
        high_risk_count = int(np.sum(high_risk_mask))
    else:
        high_risk_count = 0

    return {
        "rate": round(float(churn_rate), 1),
        "mrr": round(float(mrr), 2),
        "active": int(len(active_df)),
        "arpu": round(float(arpu), 2),
        "annual_projections": round(float(arr), 2),
        "high_risk_count": high_risk_count
    }