import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi.security import HTTPBearer

load_dotenv()

class Config:
    security = {
        "SECRET_KEY": os.getenv("SECRET_KEY"),
        "ALGORITHM": os.getenv("ALGORITHM"),
        "pwd_context": CryptContext(schemes=["bcrypt"], deprecated="auto"),
        "bearer_scheme": HTTPBearer(auto_error=False)
    }
    
    database = {
        "SQLALCHEMY_DATABASE_URL": os.getenv("SQLALCHEMY_DATABASE_URL")
    }
