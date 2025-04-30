"""
Module: customer_value.py

Purpose: Calculate customer LTV and set aggressive affiliate terms for early growth. Includes a function for LTV and revenue share calculation.
"""

def calculate_customer_ltv(annual_price, churn_rate):
    """
    Estimate customer lifetime value (LTV).
    LTV = annual_price / churn_rate
    """
    if churn_rate == 0:
        return float('inf')
    return annual_price / churn_rate

def suggest_affiliate_terms(ltv, share=0.5):
    """
    Suggest an aggressive affiliate revenue share (default 50%).
    Returns the affiliate payout per customer.
    """
    return ltv * share 