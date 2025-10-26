"""
Consolidated Pydantic models for the banking system
All models in a single file for easier management
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

# ============================================================================
# USER MODELS
# ============================================================================

class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    AUDITOR = "auditor"

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.CUSTOMER          # unchanged
    # NEW – only admin can set this flag
    admin_only: bool = Field(
        False,
        description="Set to True only when the request comes from a bank admin"
    )

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ============================================================================
# ACCOUNT MODELS
# ============================================================================

class AccountType(str, Enum):
    SAVINGS = "savings"
    CHECKING = "checking"
    BUSINESS = "business"

class AccountCreate(BaseModel):
    account_type: AccountType
    initial_deposit: float = Field(..., ge=0, description="Must be >= 0")

class AccountResponse(BaseModel):
    id: str
    user_id: str
    account_number: str
    account_type: str
    balance: float
    daily_transfer_limit: float
    daily_transferred: float
    is_active: bool
    created_at: datetime

class BalanceResponse(BaseModel):
    account_number: str
    balance: float
    account_type: str

# ============================================================================
# TRANSACTION MODELS
# ============================================================================

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    FLAGGED = "flagged"

class TransferRequest(BaseModel):
    from_account: str = Field(..., description="Sender account number")
    to_account: str = Field(..., description="Receiver account number")
    amount: float = Field(..., gt=0, description="Amount must be > 0")
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    from_account: str
    to_account: str
    amount: float
    transaction_type: str
    status: str
    description: Optional[str]
    created_at: datetime