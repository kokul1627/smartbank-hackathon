
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "bankdb")
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", "3600"))

# MongoDB client
mongo_client = None
database = None

async def init_db():
    """Initialize MongoDB connection"""
    global mongo_client, database
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    database = mongo_client[DATABASE_NAME]
    
    # Create indexes
    await database.users.create_index("email", unique=True)
    await database.accounts.create_index("account_number", unique=True)
    await database.accounts.create_index("user_id")
    
    print("✅ Database connected and indexes created")

def get_database():
    """Get database instance"""
    return database