from pydantic import BaseModel
from typing import Optional, Dict, List, Any

# --- Product Schemas ---
class ProductCreate(BaseModel):
    name: Dict[str, str]  # Required Multilingual: {"en": "...", "ru": "...", "hy": "..."}
    price: Optional[float] = None
    stock: int = 0
    manufacturer: Optional[str] = None
    image_url: Optional[str] = None
    is_new: bool = False
    types_id: Optional[int] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    description: Dict[str, str]  # Required Multilingual: {"en": "...", "ru": "...", "hy": "..."}
    features: Optional[List[Dict[str, Any]]] = []  # Each feature has {id, title, description}


class ProductUpdate(BaseModel):
    name: Optional[Dict[str, str]] = None  # Multilingual: {"en": "...", "ru": "...", "hy": "..."}
    price: Optional[float] = None
    stock: Optional[int] = None
    manufacturer: Optional[str] = None
    image_url: Optional[str] = None
    is_new: Optional[bool] = None
    types_id: Optional[int] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    description: Optional[Dict[str, str]] = None  # Multilingual descriptions
    features: Optional[List[Dict[str, Any]]] = None  # Each feature has {id, title, description}


class ProductResponse(BaseModel):
    id: int
    name: str
    price: Optional[float]
    stock: int
    manufacturer: Optional[str]
    image_url: Optional[str]
    is_new: bool
    types_id: Optional[int]
    category_id: Optional[int]
    subcategory_id: Optional[int]
    
    class Config:
        from_attributes = True


# --- News Schemas ---
class NewsCreate(BaseModel):
    name: Dict[str, str]  # Required Multilingual: {"en": "...", "ru": "...", "hy": "..."}
    image_url: Optional[str] = None
    author_id: Optional[int] = None
    description: Dict[str, str]  # Required Multilingual descriptions
    features: Optional[List[Dict[str, Any]]] = []  # Each feature has {id, title, description}


class NewsUpdate(BaseModel):
    name: Optional[Dict[str, str]] = None  # Multilingual: {"en": "...", "ru": "...", "hy": "..."}
    image_url: Optional[str] = None
    author_id: Optional[int] = None
    description: Optional[Dict[str, str]] = None  # Multilingual descriptions
    features: Optional[List[Dict[str, Any]]] = None  # Each feature has {id, title, description}


class NewsResponse(BaseModel):
    id: int
    title: str
    image_url: Optional[str]
    author_id: Optional[int]
    
    class Config:
        from_attributes = True

