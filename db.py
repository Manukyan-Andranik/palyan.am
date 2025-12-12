from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
import enum

from config import Config

engine = create_engine(
    Config.database["SQLALCHEMY_DATABASE_URL"],
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Language Enum
class LanguageEnum(str, enum.Enum):
    EN = "en"
    RU = "ru"
    HY = "hy"  # Armenian

# ==================== MODELS ====================

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AnimalSpecies(Base):
    __tablename__ = "animal_species"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # Default language name
    description = Column(Text)  # Default language description
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    products = relationship("Product", back_populates="species")
    translations = relationship("AnimalSpeciesTranslation", back_populates="species", cascade="all, delete-orphan")

class AnimalSpeciesTranslation(Base):
    __tablename__ = "animal_species_translations"
    id = Column(Integer, primary_key=True, index=True)
    species_id = Column(Integer, ForeignKey("animal_species.id", ondelete="CASCADE"))
    language = Column(SQLEnum(LanguageEnum), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    species = relationship("AnimalSpecies", back_populates="translations")

class ProductCategory(Base):
    __tablename__ = "product_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # Default language name
    description = Column(Text)  # Default language description
    created_at = Column(DateTime, default=datetime.utcnow)
    products = relationship("Product", back_populates="category")
    translations = relationship("ProductCategoryTranslation", back_populates="category", cascade="all, delete-orphan")

class ProductCategoryTranslation(Base):
    __tablename__ = "product_category_translations"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("product_categories.id", ondelete="CASCADE"))
    language = Column(SQLEnum(LanguageEnum), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    category = relationship("ProductCategory", back_populates="translations")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # Default language name
    description = Column(Text)  # Default language description
    price = Column(Float)
    stock = Column(Integer, default=0)
    image_url = Column(String)
    species_id = Column(Integer, ForeignKey("animal_species.id"))
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    is_new = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    species = relationship("AnimalSpecies", back_populates="products")
    category = relationship("ProductCategory", back_populates="products")
    translations = relationship("ProductTranslation", back_populates="product", cascade="all, delete-orphan")

class ProductTranslation(Base):
    __tablename__ = "product_translations"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    language = Column(SQLEnum(LanguageEnum), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    product = relationship("Product", back_populates="translations")

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)  # Default language title
    content = Column(Text)  # Default language content
    summary = Column(Text)  # Default language summary
    image_url = Column(String)
    author = Column(String)
    published_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    translations = relationship("NewsTranslation", back_populates="news", cascade="all, delete-orphan")

class NewsTranslation(Base):
    __tablename__ = "news_translations"
    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id", ondelete="CASCADE"))
    language = Column(SQLEnum(LanguageEnum), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    news = relationship("News", back_populates="translations")

# Create all tables
Base.metadata.create_all(bind=engine)

# ==================== PYDANTIC SCHEMAS ====================

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    is_admin: bool = False

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

# Translation Schemas
class TranslationData(BaseModel):
    en: Optional[Dict[str, Optional[str]]] = None
    ru: Optional[Dict[str, Optional[str]]] = None
    hy: Optional[Dict[str, Optional[str]]] = None

class AnimalSpeciesTranslationSchema(BaseModel):
    language: LanguageEnum
    name: str
    description: Optional[str] = None

class AnimalSpeciesCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    translations: Optional[Dict[str, Dict[str, Optional[str]]]] = None
    # Example: {"en": {"name": "Dog", "description": "..."}, "ru": {"name": "Собака", "description": "..."}}

class AnimalSpeciesResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    image_url: Optional[str]
    created_at: datetime
    translations: Optional[Dict[str, Dict[str, Optional[str]]]] = None
    model_config = ConfigDict(from_attributes=True)

class ProductCategoryTranslationSchema(BaseModel):
    language: LanguageEnum
    name: str
    description: Optional[str] = None

class ProductCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    translations: Optional[Dict[str, Dict[str, Optional[str]]]] = None

class ProductCategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: Optional[datetime] = None
    translations: Optional[Dict[str, Dict[str, Optional[str]]]] = None
    model_config = ConfigDict(from_attributes=True)

class ProductTranslationSchema(BaseModel):
    language: LanguageEnum
    name: str
    description: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    image_url: Optional[str] = None
    species_id: int
    category_id: int
    is_new: bool = False
    translations: Optional[Dict[str, Dict[str, Optional[str]]]] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    species_id: Optional[int] = None
    category_id: Optional[int] = None
    is_new: Optional[bool] = None
    translations: Optional[Dict[str, Dict[str, Optional[str]]]] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    image_url: Optional[str]
    species_id: Optional[int]
    category_id: int
    is_new: bool
    created_at: datetime
    species: Optional[AnimalSpeciesResponse]
    category: Optional[ProductCategoryResponse]
    translations: Optional[Dict[str, Dict[str, Optional[str]]]] = None
    model_config = ConfigDict(from_attributes=True)

class NewsTranslationSchema(BaseModel):
    language: LanguageEnum
    title: str
    content: str
    summary: Optional[str] = None

class NewsCreate(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    translations: Optional[Dict[str, Dict[str, Optional[str]]]] = None

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    image_url: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    translations: Optional[Dict[str, Dict[str, Optional[str]]]] = None

class NewsResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: Optional[str]
    image_url: Optional[str]
    author: Optional[str]
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    translations: Optional[Dict[str, Dict[str, Optional[str]]]] = None
    model_config = ConfigDict(from_attributes=True)

# ==================== HELPER FUNCTIONS ====================

def get_translations_dict(translation_objects, fields: list) -> Dict[str, Dict[str, Optional[str]]]:
    """Convert translation objects to dictionary format."""
    result = {}
    for trans in translation_objects:
        lang = trans.language.value
        result[lang] = {field: getattr(trans, field, None) for field in fields}
    return result

def add_translations_to_object(db_object, translations_dict: Dict[str, Dict[str, Optional[str]]], translation_model):
    """Add translation objects to a database object."""
    if not translations_dict:
        return
    
    for lang, fields in translations_dict.items():
        if lang not in [l.value for l in LanguageEnum]:
            continue
        
        translation = translation_model(
            language=LanguageEnum(lang),
            **fields
        )
        db_object.translations.append(translation)