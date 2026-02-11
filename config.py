import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi.security import HTTPBearer
from imagekitio import ImageKit

load_dotenv()

class Config:
    security = {
        "SECRET_KEY": os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
        "ALGORITHM": os.getenv("ALGORITHM", "HS256"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        "pwd_context": CryptContext(schemes=["bcrypt"], deprecated="auto"),
        "bearer_scheme": HTTPBearer(auto_error=False)
    }

    database = {
        "SQLALCHEMY_DATABASE_URL": os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./vetpharmacy.db")
    }

    imagekit = ImageKit(
        private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
    )

    IMAGEKIT_URL_ENDPOINT = os.getenv("IMAGEKIT_URL_ENDPOINT")

    @staticmethod
    def hash_password(password: str) -> str:
        return Config.security["pwd_context"].hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return Config.security["pwd_context"].verify(plain_password, hashed_password)