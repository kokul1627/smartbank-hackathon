"""
Audit logging service
"""
from datetime import datetime
from typing import Optional, Dict, Any
from app.config import get_database

async def create_audit_log(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
):
    """
    Create an audit log entry
    """
    db = get_database()
    
    audit_log = {
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": details,
        "ip_address": ip_address,
        "timestamp": datetime.utcnow()
    }
    
    await db.audit_logs.insert_one(audit_log)