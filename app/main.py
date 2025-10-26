"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.bank_router import (
    auth_router,
    account_router,
    transaction_router
)
from app.config import init_db

app = FastAPI(
    title="Modular Banking Backend System",
    description="A secure banking backend with JWT auth, role-based access, and audit logging",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database connection
@app.on_event("startup")
async def startup_event():
    await init_db()

# Include consolidated routers
app.include_router(auth_router)
app.include_router(account_router)
app.include_router(transaction_router)

@app.get("/")
async def root():
    return {
        "message": "🏦 Modular Banking Backend System",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}