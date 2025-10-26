"""
Consolidated API routes for the banking system
All routes in a single file for easier management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from app.models.bank_model import (
    # User models
    UserRegister, UserLogin, TokenResponse, UserResponse,
    # Account models
    AccountCreate, AccountResponse, BalanceResponse,
    # Transaction models
    TransferRequest, TransactionResponse, TransactionStatus
)
from app.config import get_database
from app.utils.password import hash_password, verify_password
from app.utils.jwt_handler import create_access_token
from app.utils.auth_middleware import require_role
from app.utils.helpers import generate_account_number, serialize_document
from app.services.audit_service import create_audit_log

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user: UserRegister,
    current_user: dict = Depends(require_role(["admin"]))   # ← ONLY ADMIN
):
    """Only a Bank-Admin can register new users."""
    db = get_database()

    # ----- existing validation (email uniqueness) -----
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # ----- hash & store -----
    user_doc = {
        "name": user.name,
        "email": user.email,
        "password": hash_password(user.password),
        "role": user.role.value,
        "created_at": datetime.utcnow()
    }
    result = await db.users.insert_one(user_doc)

    # ----- JWT -----
    token = create_access_token(
        user_id=str(result.inserted_id),
        email=user.email,
        role=user.role.value
    )

    # ----- response -----
    user_response = UserResponse(
        id=str(result.inserted_id),
        name=user.name,
        email=user.email,
        role=user.role.value,
        created_at=user_doc["created_at"]
    )
    await create_audit_log(
        user_id=current_user["user_id"],
        action="ADMIN_REGISTER_USER",
        resource_type="user",
        resource_id=str(result.inserted_id)
    )
    return TokenResponse(access_token=token, user=user_response)

@auth_router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login with email and password, return JWT token"""
    db = get_database()
    
    # Find user
    user = await db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create JWT token
    token = create_access_token(
        user_id=str(user["_id"]),
        email=user["email"],
        role=user["role"]
    )
    
    # Prepare response
    user_response = UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        role=user["role"],
        created_at=user["created_at"]
    )
    
    return TokenResponse(access_token=token, user=user_response)

# ============================================================================
# ACCOUNT ROUTES
# ============================================================================

account_router = APIRouter(prefix="/accounts", tags=["Accounts"])

@account_router.post("/", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    user_id: str = Query(..., description="User ID to create account for"),
    current_user: dict = Depends(require_role(["admin"]))   # ← ONLY ADMIN
):
    """Bank-Admin creates an account for a given user."""
    db = get_database()

    # verify user exists
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    account_doc = {
        "user_id": user_id,
        "account_number": generate_account_number(),
        "account_type": account.account_type.value,
        "balance": account.initial_deposit,
        "daily_transfer_limit": 10000.0,  # Configurable default
        "daily_transferred": 0.0,
        "is_active": True,
        "created_at": datetime.utcnow()
    }

    result = await db.accounts.insert_one(account_doc)

    await create_audit_log(
        user_id=current_user["user_id"],
        action="ADMIN_CREATE_ACCOUNT",
        resource_type="account",
        resource_id=str(result.inserted_id),
        details={"for_user": user_id}
    )

    account_doc["id"] = str(result.inserted_id)
    return AccountResponse(**account_doc)

@account_router.get("/", response_model=List[AccountResponse])
async def get_accounts(current_user: dict = Depends(require_role(["customer", "admin", "auditor"]))):
    """Get list of accounts (filtered by role)"""
    db = get_database()
    query = {}
    if current_user["role"] == "customer":
        query["user_id"] = current_user["user_id"]
    
    accounts = await db.accounts.find(query).to_list(None)
    return [AccountResponse(**serialize_document(a)) for a in accounts]

@account_router.get("/{account_number}/balance", response_model=BalanceResponse)
async def get_balance(account_number: str, current_user: dict = Depends(require_role(["customer", "admin"]))):
    """Get account balance"""
    db = get_database()
    query = {"account_number": account_number}
    if current_user["role"] == "customer":
        query["user_id"] = current_user["user_id"]
    
    account = await db.accounts.find_one(query)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    await create_audit_log(
        user_id=current_user["user_id"],
        action="VIEW_BALANCE",
        resource_type="account",
        resource_id=str(account["_id"])
    )
    
    return BalanceResponse(
        account_number=account["account_number"],
        balance=account["balance"],
        account_type=account["account_type"]
    )

# ============================================================================
# TRANSACTION ROUTES
# ============================================================================

transaction_router = APIRouter(prefix="/transactions", tags=["Transactions"])

@transaction_router.post("/transfer", response_model=TransactionResponse)
async def transfer_funds(transfer: TransferRequest, current_user: dict = Depends(require_role(["customer"]))):
    """Perform money transfer with limits and atomicity"""
    db = get_database()
    user_id = current_user["user_id"]
    
    # Find sender and receiver accounts
    sender = await db.accounts.find_one({"account_number": transfer.from_account, "user_id": user_id})
    if not sender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sender account not found")
    
    receiver = await db.accounts.find_one({"account_number": transfer.to_account})
    if not receiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver account not found")
    
    # Check balance and limits
    if sender["balance"] < transfer.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
    
    if sender["daily_transferred"] + transfer.amount > sender["daily_transfer_limit"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Daily transfer limit exceeded")
    
    # Atomic transaction
    async with await db.client.start_session() as session:
        async with session.start_transaction():
            await db.accounts.update_one(
                {"_id": sender["_id"]},
                {"$inc": {"balance": -transfer.amount, "daily_transferred": transfer.amount}},
                session=session
            )
            await db.accounts.update_one(
                {"_id": receiver["_id"]},
                {"$inc": {"balance": transfer.amount}},
                session=session
            )
            
            trans_doc = {
                "from_account": transfer.from_account,
                "to_account": transfer.to_account,
                "amount": transfer.amount,
                "transaction_type": TransactionType.TRANSFER.value,
                "status": TransactionStatus.COMPLETED.value,
                "description": transfer.description,
                "created_at": datetime.utcnow()
            }
            
            result = await db.transactions.insert_one(trans_doc, session=session)
    
    await create_audit_log(
        user_id=user_id,
        action="TRANSFER_FUNDS",
        resource_type="transaction",
        resource_id=str(result.inserted_id),
        details={"amount": transfer.amount, "from": transfer.from_account, "to": transfer.to_account}
    )
    
    return TransactionResponse(id=str(result.inserted_id), **trans_doc)

@transaction_router.get("/", response_model=List[TransactionResponse])
async def get_transactions(account_number: Optional[str] = Query(None), current_user: dict = Depends(require_role(["customer", "admin", "auditor"]))):
    """Get transaction history (filtered by role/account)"""
    db = get_database()
    query = {}
    if current_user["role"] == "customer":
        query["$or"] = [{"from_account": account_number}, {"to_account": account_number}]
        # Validate user owns the account
        account = await db.accounts.find_one({"account_number": account_number, "user_id": current_user["user_id"]})
        if not account:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to account")
    
    transactions = await db.transactions.find(query).sort("created_at", -1).limit(100).to_list(100)
    return [TransactionResponse(**serialize_document(t)) for t in transactions]

