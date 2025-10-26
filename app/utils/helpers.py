"""
Helper utilities for the application
"""
import random
import string
from datetime import datetime, date

def generate_account_number() -> str:
    """
    Generate a unique 12-digit account number
    """
    return ''.join(random.choices(string.digits, k=12))

def serialize_document(doc: dict) -> dict:
    """
    Convert MongoDB document to JSON-serializable format
    """
    if doc is None:
        return None
    
    doc["id"] = str(doc.pop("_id"))
    
    # Convert datetime objects
    for key, value in doc.items():
        if isinstance(value, datetime):
            doc[key] = value
        elif isinstance(value, date):
            doc[key] = datetime.combine(value, datetime.min.time())
    
    return doc

def reset_daily_limits():
    """
    Helper to reset daily transfer limits (can be called via scheduler)
    """
    # This would be called by a cron job or scheduler
    pass