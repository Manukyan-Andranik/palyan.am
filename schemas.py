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
    
    # Nested dictionaries for multi-language support
    translations: Dict[str, ProductTranslationCreate]
    features: List[ProductFeatureCreate] = []

class ProductResponse(ProductCreate):
    id: int
    
    class Config:
        from_attributes = True