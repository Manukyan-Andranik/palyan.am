from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean

from config import Config

engine = create_engine(
    Config.database["SQLALCHEMY_DATABASE_URL"],
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    products = relationship("Product", back_populates="species")

class ProductCategory(Base):
    __tablename__ = "product_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    stock = Column(Integer, default=0)
    image_url = Column(String)
    species_id = Column(Integer, ForeignKey("animal_species.id"))
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    is_new = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    species = relationship("AnimalSpecies", back_populates="products")
    category = relationship("ProductCategory", back_populates="products")

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    summary = Column(Text)
    image_url = Column(String)
    author = Column(String)
    published_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

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

class AnimalSpeciesCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class AnimalSpeciesResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    image_url: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProductCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProductCategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    image_url: Optional[str] = None
    species_id: int
    category_id: int
    is_new: bool = False

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    species_id: Optional[int] = None
    category_id: Optional[int] = None
    is_new: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    image_url: Optional[str]
    species_id: int
    category_id: int
    is_new: bool
    created_at: datetime
    species: Optional[AnimalSpeciesResponse]
    category: Optional[ProductCategoryResponse]
    model_config = ConfigDict(from_attributes=True)

class NewsCreate(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    image_url: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None

class NewsResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: Optional[str]
    image_url: Optional[str]
    author: Optional[str]
    published_at: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
