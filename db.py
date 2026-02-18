import enum
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text,
    DateTime, ForeignKey, Boolean, Enum as SQLEnum,
    UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from typing import Optional, Dict, List, Any
from pydantic import BaseModel as PydanticBaseModel

# try:
from config import Config
# except ImportError:
#     class Config:
#         database = {"SQLALCHEMY_DATABASE_URL": "sqlite:///./vetpharmacy.db"}

# Database initialization
engine = create_engine(
    Config.database["SQLALCHEMY_DATABASE_URL"],
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# Supported languages enum
class LanguageEnum(str, enum.Enum):
    en = "en"
    ru = "ru"
    hy = "hy"

# ==================== USER MODELS ====================

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ==================== CATEGORY MODELS ====================

class ProductCategory(Base):
    __tablename__ = "product_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    translations = relationship("ProductCategoryTranslation", back_populates="category", cascade="all, delete-orphan")
    subcategories = relationship("ProductSubcategory", back_populates="category", cascade="all, delete-orphan")

class ProductCategoryTranslation(Base):
    __tablename__ = "product_categories_translations"
    __table_args__ = (UniqueConstraint("category_id", "language"),)
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("product_categories.id", ondelete="CASCADE"), nullable=False)
    language = Column(SQLEnum(LanguageEnum), nullable=False)
    name = Column(String(255))
    category = relationship("ProductCategory", back_populates="translations")

# ==================== SUBCATEGORY MODELS ====================

class ProductSubcategory(Base):
    __tablename__ = "product_subcategories"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("product_categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255))
    translations = relationship("ProductSubcategoryTranslation", back_populates="subcategory", cascade="all, delete-orphan")
    category = relationship("ProductCategory", back_populates="subcategories")

class ProductSubcategoryTranslation(Base):
    __tablename__ = "product_subcategories_translations"
    __table_args__ = (UniqueConstraint("subcategory_id", "language"),)
    id = Column(Integer, primary_key=True, index=True)
    subcategory_id = Column(Integer, ForeignKey("product_subcategories.id", ondelete="CASCADE"), nullable=False)
    language = Column(SQLEnum(LanguageEnum), nullable=False)
    name = Column(String(255))
    subcategory = relationship("ProductSubcategory", back_populates="translations")

# ==================== PRODUCT MODELS ====================

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=True)
    stock = Column(Integer, default=0)
    manufacturer = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=True)
    is_new = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    category_id = Column(Integer, ForeignKey("product_categories.id", ondelete="SET NULL"), nullable=True)
    subcategory_id = Column(Integer, ForeignKey("product_subcategories.id", ondelete="SET NULL"), nullable=True)
    
    translations = relationship("ProductTranslation", back_populates="product", cascade="all, delete-orphan")
    features = relationship("ProductFeature", back_populates="product", order_by="ProductFeature.id", cascade="all, delete-orphan")

class ProductTranslation(Base):
    __tablename__ = "product_translations"
    __table_args__ = (UniqueConstraint("product_id", "language"),)
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    language = Column(SQLEnum(LanguageEnum), nullable=False)
    name = Column(String(255))
    description = Column(Text)
    product = relationship("Product", back_populates="translations")

class ProductFeature(Base):
    __tablename__ = "product_features"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    title = Column(String(255))
    product = relationship("Product", back_populates="features")
    translations = relationship("ProductFeatureTranslation", back_populates="feature", cascade="all, delete-orphan")

class ProductFeatureTranslation(Base):
    __tablename__ = "product_features_translations"
    __table_args__ = (UniqueConstraint("feature_id", "language"),)
    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("product_features.id", ondelete="CASCADE"))
    language = Column(SQLEnum(LanguageEnum), nullable=False)
    title = Column(String(255))
    description = Column(Text)
    feature = relationship("ProductFeature", back_populates="translations")

# ==================== NEWS MODELS ====================

class NewsAuthor(Base):
    __tablename__ = "news_authors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    image_url = Column(String(500), nullable=True)
    news = relationship("News", back_populates="author")
    translations = relationship("NewsAuthorTranslation", cascade="all, delete-orphan", back_populates="author")

class NewsAuthorTranslation(Base):
    __tablename__ = "news_author_translations"
    __table_args__ = (UniqueConstraint("author_id", "language"),)
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("news_authors.id", ondelete="CASCADE"), nullable=False)
    language = Column(SQLEnum(LanguageEnum), nullable=False)
    name = Column(String(200), nullable=False)
    position = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    author = relationship("NewsAuthor", back_populates="translations")

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300))
    image_url = Column(String(500), nullable=True)
    author_id = Column(Integer, ForeignKey("news_authors.id", ondelete="SET NULL"), nullable=True)
    published_at = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    author = relationship("NewsAuthor", back_populates="news")
    features = relationship("NewsFeatures", cascade="all, delete-orphan", back_populates="news")
    translations = relationship("NewsTranslation", cascade="all, delete-orphan", back_populates="news")

class NewsTranslation(Base):
    __tablename__ = "news_translations"
    __table_args__ = (UniqueConstraint("news_id", "language"),)
    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id", ondelete="CASCADE"), nullable=False)
    language = Column(SQLEnum(LanguageEnum), nullable=False)
    title = Column(String(300), nullable=False)
    news = relationship("News", back_populates="translations")

class NewsFeatures(Base):
    __tablename__ = "news_features"
    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(300), nullable=False)
    news = relationship("News", back_populates="features")
    translations = relationship("NewsFeaturesTranslation", cascade="all, delete-orphan", back_populates="feature")

class NewsFeaturesTranslation(Base):
    __tablename__ = "news_features_translations"
    __table_args__ = (UniqueConstraint("feature_id", "language"),)
    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("news_features.id", ondelete="CASCADE"), nullable=False)
    language = Column(SQLEnum(LanguageEnum), nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    feature = relationship("NewsFeatures", back_populates="translations")

# ==================== PYDANTIC SCHEMAS ====================

class UserCreate(PydanticBaseModel):
    username: str
    email: str
    password: str
    is_admin: bool = False

class UserResponse(PydanticBaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(PydanticBaseModel):
    access_token: str
    token_type: str

# Categories
class ProductCategoryCreate(PydanticBaseModel):
    name: Dict[str, str]
    subcategories: Optional[List[Dict[str, Any]]] = None

class ProductCategoryUpdate(PydanticBaseModel):
    name: Optional[Dict[str, str]] = None
    subcategories: Optional[List[Dict[str, Any]]] = None

# Subcategories
class ProductSubcategoryCreate(PydanticBaseModel):
    category_id: int
    name: Dict[str, str]

class ProductSubcategoryUpdate(PydanticBaseModel):
    name: Optional[Dict[str, str]] = None

# Products
class ProductCreate(PydanticBaseModel):
    name: Dict[str, str]
    price: Optional[float] = None
    stock: int = 0
    manufacturer: Optional[str] = None
    image_url: Optional[str] = None
    is_new: bool = False
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    description: Dict[str, str]
    features: Optional[List[Dict[str, Any]]] = []

class ProductUpdate(PydanticBaseModel):
    name: Optional[Dict[str, str]] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    manufacturer: Optional[str] = None
    image_url: Optional[str] = None
    is_new: Optional[bool] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    description: Optional[Dict[str, str]] = None
    features: Optional[List[Dict[str, Any]]] = []

# NewsAuthor
class NewsAuthorCreate(PydanticBaseModel):
    name: Dict[str, str]  # Multilingual: {"en": "...", "ru": "...", "hy": "..."}
    bio: Dict[str, str]  # Multilingual: {"en": "...", "ru": "...", "hy": "..."}
    position: Dict[str, str]  # Multilingual: {"en": "...", "ru": "...", "hy": "..."}
    image: Optional[str] = None


class NewsAuthorUpdate(PydanticBaseModel):
    name: Optional[Dict[str, str]] = None  # Multilingual: {"en": "...", "ru": "...", "hy": "..."}
    bio: Optional[Dict[str, str]] = None  # Multilingual: {"en": "...", "ru": "...", "hy": "..."}
    position: Optional[Dict[str, str]] = None  # Multilingual: {"en": "...", "ru": "...", "hy": "..."}
    image: Optional[str] = None


# News
class NewsCreate(PydanticBaseModel):
    name: Dict[str, str]  # Multilingual: {"en": "...", "ru": "...", "hy": "..."}
    image_url: Optional[str] = None
    author: Optional[NewsAuthorCreate] = None  # Create/update author inline or use author_id
    author_id: Optional[int] = None
    features: Optional[List[Dict[str, Any]]] = []


class NewsUpdate(PydanticBaseModel):
    name: Optional[Dict[str, str]] = None  # Multilingual: {"en": "...", "ru": "...", "hy": "..."}
    image_url: Optional[str] = None
    author: Optional[NewsAuthorUpdate] = None  # Update author inline or use author_id
    author_id: Optional[int] = None
    features: Optional[List[Dict[str, Any]]] = None
