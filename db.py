import enum
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text,
    DateTime, ForeignKey, Boolean, Enum as SQLEnum,
    UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from typing import Optional, Dict, List
from pydantic import BaseModel as PydanticBaseModel


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
    
    # Relationship back to category
    category = relationship("ProductCategory", back_populates="translations")

class ProductSubcategory(Base):
    __tablename__ = "product_subcategories"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("product_categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255))  # Fallback name
    translations = relationship("ProductSubcategoryTranslation", back_populates="subcategory", cascade="all, delete-orphan")


class ProductSubcategoryTranslation(Base):
    __tablename__ = "product_subcategories_translations"
    __table_args__ = (UniqueConstraint("subcategory_id", "language"),)
    id = Column(Integer, primary_key=True, index=True)
    subcategory_id = Column(Integer, ForeignKey("product_subcategories.id", ondelete="CASCADE"), nullable=False)
    language = Column(SQLEnum(LanguageEnum), nullable=False)
    name = Column(String(255))    
    
    # Relationship back to subcategory
    subcategory = relationship("ProductSubcategory", back_populates="translations")

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
    subcategory_id = Column(Integer, ForeignKey("product_subcategories.id", ondelete="SET NULL"), nullable=True)
    
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
    description = Column(Text, nullable=True)
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
    subcategory_id: Optional[int] = None
    translations: Dict[str, Dict[str, str]]
    features: Optional[List[Dict[str, str]]] = []

class ProductUpdate(PydanticBaseModel):
    name: str
    price: Optional[float] = None
    stock: int = 0
    manufacturer: Optional[str] = None
    image_url: Optional[str] = None
    is_new: bool = False
    types_id: Optional[int] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    translations: Dict[str, Dict[str, str]]
    features: Optional[List[Dict[str, str]]] = []

# --- News ---
class NewsFeatureCreate(PydanticBaseModel):
    title: str
    translations: Dict[str, Dict[str, str]]

class NewsCreate(PydanticBaseModel):
    image_url: Optional[str] = None
    author_id: Optional[int] = None
    translations: Dict[str, Dict[str, str]]
    features: Optional[List[Dict[str, str]]] = []


class NewsUpdate(PydanticBaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    author_id: Optional[int] = None
    image_url: Optional[str] = None
    translations: Optional[Dict[str, Dict[str, str]]] = None




# CREATE TABLE products (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(255) NOT NULL,
#     price FLOAT,
#     stock INTEGER DEFAULT 0,
#     manufacturer VARCHAR(255),
#     image_url VARCHAR(500),
#     is_new BOOLEAN DEFAULT FALSE,
#     created_at TIMESTAMP DEFAULT now(),
#     types_id INTEGER REFERENCES animal_types(id) ON DELETE SET NULL,
#     category_id INTEGER REFERENCES product_categories(id) ON DELETE SET NULL
# );

# CREATE TABLE product_translations (
#     id SERIAL PRIMARY KEY,
#     product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
#     language languageenum NOT NULL,
#     name VARCHAR(255),
#     description TEXT,
#     UNIQUE (product_id, language)
# );

# CREATE TABLE product_features (
#     id SERIAL PRIMARY KEY,
#     product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
#     title VARCHAR(255)
# );

# CREATE TABLE product_features_translations (
#     id SERIAL PRIMARY KEY,
#     feature_id INTEGER REFERENCES product_features(id) ON DELETE CASCADE,
#     language languageenum NOT NULL,
#     title VARCHAR(255),
#     description TEXT,
#     UNIQUE (feature_id, language)
# );




# CREATE TABLE news_authors (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(200) NOT NULL,
#     image_url VARCHAR(500)
# );

# CREATE TABLE news_author_translations (
#     id SERIAL PRIMARY KEY,
#     author_id INTEGER NOT NULL REFERENCES news_authors(id) ON DELETE CASCADE,
#     language languageenum NOT NULL,
#     name VARCHAR(200) NOT NULL,
#     position VARCHAR(200),
#     bio TEXT,
#     UNIQUE (author_id, language)
# );




# CREATE TABLE news (
#     id SERIAL PRIMARY KEY,
#     title VARCHAR(300),
#     image_url VARCHAR(500),
#     author_id INTEGER REFERENCES news_authors(id) ON DELETE SET NULL,
#     published_at TIMESTAMPTZ DEFAULT now(),
#     created_at TIMESTAMPTZ DEFAULT now(),
#     updated_at TIMESTAMPTZ DEFAULT now()
# );

# CREATE TABLE news_translations (
#     id SERIAL PRIMARY KEY,
#     news_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
#     language languageenum NOT NULL,
#     title VARCHAR(300) NOT NULL,
#     summary TEXT,
#     UNIQUE (news_id, language)
# );

# CREATE TABLE news_features (
#     id SERIAL PRIMARY KEY,
#     news_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
#     title VARCHAR(300) NOT NULL
# );

# CREATE TABLE news_features_translations (
#     id SERIAL PRIMARY KEY,
#     feature_id INTEGER NOT NULL REFERENCES news_features(id) ON DELETE CASCADE,
#     language languageenum NOT NULL,
#     title VARCHAR(300) NOT NULL,
#     description TEXT,
#     UNIQUE (feature_id, language)
# );





# {
#   "title": "Կարմիր տզերի վտանգի մասին նախազգուշացում",
#   "content": "Թռչնամսի արտադրողներին կոչ է արվում զգույշ լինել կարմիր տզերի բռնկումներից ...",
#   "summary": "Կարմիր տզերը կարող են վնասել թռչունների առողջությունը և արտադրողականությունը, հատկապես փակ տարածքներում։",
#   "image_url": "https://example.com/news_image.jpg",
#   "author_id": 1,
#   "published_at": "2025-12-26T12:06:43.149Z",
#   "translations": {
#     "hy": {
#       "title": "Կարմիր տզերի վտանգի մասին նախազգուշացում",
#       "content": "Թռչնամսի արտադրողներին կոչ է արվում զգույշ լինել կարմիր տզերի բռնկումներից ...",
#       "summary": "Կարմիր տզերը կարող են վնասել թռչունների առողջությունը և արտադրողականությունը, հատկապես փակ տարածքներում։"
#     },
#     "ru": {
#       "title": "Предупреждение об угрозе заражения красным клещом",
#       "content": "Производителей птицы призывают внимательно следить за вспышками красного клеща ...",
#       "summary": "Красный клещ может навредить здоровью и продуктивности птиц, особенно в закрытых помещениях."
#     },
#     "en": {
#       "title": "Red mite threat warning during bird flu housing order",
#       "content": "Poultry producers are being urged to watch out for red mite outbreaks ...",
#       "summary": "Red mites can harm bird health and productivity, especially in confined indoor spaces."
#     }
#   },
#   "features": [
#     {
#       "title": "Կարմիր տզերի ախտանիշները",
#       "description": "Կարմիր տզից վարակված թռչունները կարող են ցուցաբերել անհանգստություն ...",
#       "translations": "{\"hy\":{\"title\":\"Կարմիր տզերի ախտանիշները\",\"description\":\"Կարմիր տզից վարակված թռչունները կարող են ցուցաբերել անհանգստություն ...\"},\"ru\":{\"title\":\"Симптомы красного клеща\",\"description\":\"У птиц, поражённых красным клещом, могут наблюдаться беспокойство ...\"},\"en\":{\"title\":\"Red mite symptoms\",\"description\":\"Birds affected by red mite can display restlessness ...\"}}"
#     },
#     {
#       "title": "Կարմիր տզերի թակարդներ",
#       "description": "Արտադրողները կարող են ստեղծել իրենց սեփական պարզ կարմիր տզերի թակարդները ...",
#       "translations": "{\"hy\":{\"title\":\"Կարմիր տզերի թակարդներ\",\"description\":\"Արտադրողները կարող են ստեղծել իրենց սեփական պարզ կարմիր տզերի թակարդները ...\"},\"ru\":{\"title\":\"Ловушки для красного клеща\",\"description\":\"Фермеры могут изготовить простые ловушки ...\"},\"en\":{\"title\":\"Red mite traps\",\"description\":\"Producers can create their own simple red mite traps ...\"}}"
#     },
#     {
#       "title": "Կենսաանվտանգություն",
#       "description": "Մոնիթորինգին զուգահեռ, կարևոր են կանխարգելիչ կենսաբանական անվտանգության միջոցառումները ...",
#       "translations": "{\"hy\":{\"title\":\"Կենսաանվտանգություն\",\"description\":\"Մոնիթորինգին զուգահեռ, կարևոր են կանխարգելիչ կենսաբանական անվտանգության միջոցառումները ...\"},\"ru\":{\"title\":\"Биобезопасность\",\"description\":\"Наряду с мониторингом крайне важны превентивные меры ...\"},\"en\":{\"title\":\"Biosecurity\",\"description\":\"Alongside monitoring, proactive biosecurity measures are essential ...\"}}"
#     }
#   ]
# }
