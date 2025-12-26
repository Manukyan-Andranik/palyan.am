from datetime import datetime
import enum

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text,
    DateTime, ForeignKey, Boolean, Enum as SQLEnum,
    UniqueConstraint
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from pydantic import BaseModel as PydanticBaseModel
from typing import Optional, Dict, List

# Assuming config is in a separate file, or define basic config here
try:
    from config import Config
except ImportError:
    # Fallback if config.py is missing
    class Config:
        database = {"SQLALCHEMY_DATABASE_URL": "sqlite:///./vetpharmacy.db"}

# ==================== DATABASE INIT ====================

engine = create_engine(
    Config.database["SQLALCHEMY_DATABASE_URL"],
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ==================== ENUMS ====================

class LanguageEnum(str, enum.Enum):
    en = "en"
    ru = "ru"
    hy = "hy"

# ==================== SQLALCHEMY MODELS ====================

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- Animal Types ---
class AnimalTypes(Base):
    __tablename__ = "animal_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))  # Fallback name
    image_url = Column(String(500), nullable=True)
    
    translations = relationship("AnimalTypesTranslation", back_populates="type_obj", cascade="all, delete-orphan")

class AnimalTypesTranslation(Base):
    __tablename__ = "animal_types_translations"
    __table_args__ = (UniqueConstraint("types_id", "language"),)
    id = Column(Integer, primary_key=True, index=True)
    types_id = Column(Integer, ForeignKey("animal_types.id", ondelete="CASCADE"), nullable=False)
    language = Column(SQLEnum(LanguageEnum), nullable=False)
    name = Column(String(255))
    description = Column(Text, nullable=True)
    
    type_obj = relationship("AnimalTypes", back_populates="translations")

# --- Product Categories ---
class ProductCategory(Base):
    __tablename__ = "product_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))  # Fallback name
    
    translations = relationship("ProductCategoryTranslation", back_populates="category", cascade="all, delete-orphan")

class ProductCategoryTranslation(Base):
    __tablename__ = "product_categories_translations"
    __table_args__ = (UniqueConstraint("category_id", "language"),)
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("product_categories.id", ondelete="CASCADE"), nullable=False)
    language = Column(SQLEnum(LanguageEnum), nullable=False)
    name = Column(String(255))
    description = Column(Text, nullable=True)
    
    category = relationship("ProductCategory", back_populates="translations")

# --- Product Models ---
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # Fallback name
    price = Column(Float, nullable=True)
    stock = Column(Integer, default=0)
    manufacturer = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=True)
    is_new = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    types_id = Column(Integer, ForeignKey("animal_types.id", ondelete="SET NULL"), nullable=True)
    category_id = Column(Integer, ForeignKey("product_categories.id", ondelete="SET NULL"), nullable=True)

    translations = relationship("ProductTranslation", back_populates="product", cascade="all, delete-orphan")
    features = relationship("ProductFeature", back_populates="product", cascade="all, delete-orphan")

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
    title = Column(String(255))  # Internal reference name

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

# --- News Models ---
class NewsAuthor(Base):
    __tablename__ = "news_authors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)  # Fallback
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
    title = Column(String(300))  # Fallback title
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
    summary = Column(Text, nullable=True)
    news = relationship("News", back_populates="translations")

class NewsFeatures(Base):
    __tablename__ = "news_features"
    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(300), nullable=False)  # Fallback
    
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

# --- Animal Types ---
class AnimalTypesCreate(PydanticBaseModel):
    name: str
    image_url: Optional[str] = None
    translations: Dict[str, Dict[str, str]]  # {"en": {"name": "...", "description": "..."}}

class AnimalTypesUpdate(PydanticBaseModel):
    name: Optional[str] = None
    image_url: Optional[str] = None
    translations: Optional[Dict[str, Dict[str, str]]] = None

# --- Product Category ---
class ProductCategoryCreate(PydanticBaseModel):
    name: str
    translations: Dict[str, Dict[str, str]]

class ProductCategoryUpdate(PydanticBaseModel):
    name: Optional[str] = None
    translations: Optional[Dict[str, Dict[str, str]]] = None

# --- Product ---
class ProductCreate(PydanticBaseModel):
    name: str
    price: Optional[float] = None
    stock: int = 0
    manufacturer: Optional[str] = None
    image_url: Optional[str] = None
    is_new: bool = False
    types_id: Optional[int] = None
    category_id: Optional[int] = None
    translations: Dict[str, Dict[str, str]]
    features: Optional[List[Dict[str, str]]] = []

class ProductUpdate(PydanticBaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    manufacturer: Optional[str] = None
    image_url: Optional[str] = None
    translations: Optional[Dict[str, Dict[str, str]]] = None

# --- News ---
class NewsCreate(PydanticBaseModel):
    title: str  # Fallback
    image_url: Optional[str] = None
    author_id: Optional[int] = None
    translations: Dict[str, Dict[str, str]]
    features: Optional[List[Dict[str, str]]] = []

class NewsUpdate(PydanticBaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    author_id: Optional[int] = None
    translations: Optional[Dict[str, Dict[str, str]]] = None