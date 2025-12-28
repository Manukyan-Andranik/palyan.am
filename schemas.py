from pydantic import BaseModel
from typing import Optional, Dict, List

# --- Feature Translations ---
class ProductFeatureTranslationCreate(BaseModel):
    title: str
    description: str

# --- Features ---
class ProductFeatureCreate(BaseModel):
    title: str  # Internal reference or label
    translations: Dict[str, ProductFeatureTranslationCreate]

# --- Product Translations ---
class ProductTranslationCreate(BaseModel):
    name: str
    description: str

# --- Main Product Schema ---
class ProductCreate(BaseModel):
    name: str
    price: Optional[float] = None
    stock: int = 0
    manufacturer: Optional[str] = None
    image_url: Optional[str] = None
    is_new: bool = False
    types_id: Optional[int] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    
    # Nested dictionaries for multi-language support
    translations: Dict[str, ProductTranslationCreate]
    features: List[ProductFeatureCreate] = []

class ProductResponse(ProductCreate):
    id: int
    
    class Config:
        from_attributes = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    manufacturer: Optional[str] = None
    image_url: Optional[str] = None
    is_new: Optional[bool] = None
    types_id: Optional[int] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    translations: Optional[Dict[str, ProductTranslationCreate]] = None
    features: Optional[List[ProductFeatureCreate]] = None


# --- News ---


class NewsFeatureTranslationCreate(BaseModel):
    title: str
    description: str

class NewsFeatureCreate(BaseModel):
    translations: Dict[str, NewsFeatureTranslationCreate]

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    author_id: Optional[int] = None
    translations: Optional[Dict[str, Dict[str, str]]] = None

class NewsCreate(BaseModel):
    image_url: Optional[str] = None
    author_id: Optional[int] = None
    translations: Dict[str, Dict[str, str]]
    features: Optional[List[NewsFeatureCreate]] = []

class NewsResponse(NewsCreate):
    id: int
    
    class Config:
        from_attributes = True