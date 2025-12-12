# main.py
import jwt
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List, Dict

from fastapi import FastAPI, HTTPException, Depends, Security, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials

from sqlalchemy.inspection import inspect as sa_inspect

from db import (
    User, UserCreate, UserResponse,
    AnimalSpecies, AnimalSpeciesCreate, AnimalSpeciesResponse, AnimalSpeciesTranslation,
    ProductCategory, ProductCategoryCreate, ProductCategoryResponse, ProductCategoryTranslation,
    Product, ProductCreate, ProductUpdate, ProductResponse, ProductTranslation,
    News, NewsCreate, NewsUpdate, NewsResponse, NewsTranslation,
    Token, SessionLocal, LanguageEnum,
    get_translations_dict, add_translations_to_object
)

from config import Config

# ---------- Helpers ----------
class AttrDict(dict):
    """A dict that supports attribute-style access: obj.key"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

# ==================== FASTAPI APP ====================
app = FastAPI(
    title="Animal Store API",
    version="2.0.0",
    openapi_tags=[
        {"name": "auth", "description": "Authentication endpoints"},
        {"name": "admin", "description": "Admin endpoints, require Bearer token"},
        {"name": "public", "description": "Public endpoints: User interface"}
    ],
    swagger_ui_init_oauth=None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== DEPENDENCIES ====================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return Config.security["pwd_context"].verify(plain_password, hashed_password)

def get_password_hash(password):
    return Config.hash(password)

def create_access_token(data: dict):
    return jwt.encode(data, Config.security["SECRET_KEY"], algorithm=Config.security["ALGORITHM"])

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(Config.security["bearer_scheme"]), db: Session = Depends(get_db)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization token missing")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, Config.security["SECRET_KEY"], algorithms=[Config.security["ALGORITHM"]])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

# ==================== TRANSLATION HELPERS ====================
def apply_language_filter(obj, lang: Optional[str] = None) -> Optional[AttrDict]:
    """
    Returns an AttrDict (dict with attribute access).
    - Does NOT modify SQLAlchemy relationships.
    - Produces a clean serializable object for FastAPI responses.
    - Adds 'translations' mapping for all available translations.
    - If lang is provided, overrides main fields with translation values when present.
    """
    if obj is None:
        return None

    # Collect ORM column keys
    mapper = sa_inspect(obj.__class__)
    column_keys = [col.key for col in mapper.columns]

    # Get translations list if present
    translations_list = getattr(obj, "translations", None)

    # Build translations mapping
    translations_dict: Dict[str, Dict[str, Optional[str]]] = {}
    if translations_list:
        for trans in translations_list:
            tmapper = sa_inspect(trans.__class__)
            tmap: Dict[str, Optional[str]] = {}
            for tcol in tmapper.columns:
                tkey = tcol.key
                # skip metadata/fks
                if tkey in ("id", "language", "created_at",
                            "species_id", "category_id", "product_id", "news_id"):
                    continue
                tmap[tkey] = getattr(trans, tkey, None)
            try:
                lang_code = trans.language.value
            except Exception:
                lang_code = str(getattr(trans, "language", "") or "")
            translations_dict[lang_code] = tmap

    # Base object data from columns
    data: Dict[str, Optional[object]] = {}
    for key in column_keys:
        data[key] = getattr(obj, key, None)

    # If specific language requested, override fields
    if lang and translations_list:
        translation = next(
            (t for t in translations_list if getattr(getattr(t, "language", None), "value", None) == lang),
            None
        )
        if not translation:
            translation = next((t for t in translations_list if getattr(t, "language", None) == lang), None)
        if translation:
            tmapper = sa_inspect(translation.__class__)
            for tcol in tmapper.columns:
                tkey = tcol.key
                if tkey not in data:
                    continue
                if tkey in ("id", "language", "created_at",
                            "species_id", "category_id", "product_id", "news_id"):
                    continue
                val = getattr(translation, tkey, None)
                if val is not None:
                    data[tkey] = val

    # Attach translations mapping
    data["translations"] = translations_dict

    return AttrDict(data)

def save_translations(db: Session, entity, translations_dict: dict, translation_model, foreign_key_field: str):
    """Save translations for an entity."""
    if not translations_dict:
        return
    
    # Delete existing translations
    db.query(translation_model).filter(
        getattr(translation_model, foreign_key_field) == entity.id
    ).delete()
    db.flush()
    
    # Add new translations
    for lang, fields in translations_dict.items():
        if lang not in [l.value for l in LanguageEnum]:
            continue
        
        translation_data = {
            foreign_key_field: entity.id,
            'language': LanguageEnum(lang),
            **fields
        }
        translation = translation_model(**translation_data)
        db.add(translation)
    
    db.commit()

# ==================== AUTH ENDPOINTS ====================
@app.post("/api/auth/register", response_model=UserResponse, tags=["auth"])
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password, is_admin=user.is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/auth/login", response_model=Token, tags=["auth"])
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse, tags=["auth"])
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# ==================== HOME PAGE ENDPOINTS ====================
@app.get("/api/home", tags=["public"])
def get_home_data(
    lang: Optional[str] = Query(None, description="Language code: en, ru, hy"),
    db: Session = Depends(get_db)
):
    species = db.query(AnimalSpecies).options(joinedload(AnimalSpecies.translations)).all()
    news = db.query(News).options(joinedload(News.translations)).order_by(News.published_at.desc()).limit(6).all()
    new_products = db.query(Product).options(
        joinedload(Product.translations),
        joinedload(Product.species).joinedload(AnimalSpecies.translations),
        joinedload(Product.category).joinedload(ProductCategory.translations)
    ).filter(Product.is_new == True).limit(8).all()
    
    # Apply language filter (returns AttrDict objects)
    species_out = [apply_language_filter(s, lang) for s in species]
    news_out = [apply_language_filter(n, lang) for n in news]
    products_out = [apply_language_filter(p, lang) for p in new_products]
    
    # Also apply language to nested objects for products
    for product in products_out:
        # original product from DB had species/category as ORM; but here we replaced top-product with AttrDict.
        # We need to fetch nested ORM objects from original DB result to apply translations,
        # so instead, iterate zipped pairs of (orm, filtered)
        pass

    # For nested translations we must map using original ORM results to avoid losing relationships.
    # Build mapping by id from ORM query results:
    product_map = {p.id: p for p in new_products}
    for p_out in products_out:
        orm_p = product_map.get(p_out.id)
        if orm_p is not None:
            if orm_p.species:
                p_out.species = apply_language_filter(orm_p.species, lang)
            else:
                p_out.species = None
            if orm_p.category:
                p_out.category = apply_language_filter(orm_p.category, lang)
            else:
                p_out.category = None

    return {
        "animal_species": species_out,
        "latest_news": news_out,
        "new_products": products_out
    }

# ==================== ANIMAL SPECIES ENDPOINTS ====================
@app.get("/api/species", response_model=List[AnimalSpeciesResponse], tags=["public"])
def get_all_species(
    skip: int = 0,
    limit: int = 100,
    lang: Optional[str] = Query(None, description="Language code: en, ru, hy"),
    db: Session = Depends(get_db)
):
    species_list = db.query(AnimalSpecies).options(joinedload(AnimalSpecies.translations)).offset(skip).limit(limit).all()
    return [apply_language_filter(s, lang) for s in species_list]

@app.get("/api/species/{species_id}", response_model=AnimalSpeciesResponse, tags=["public"])
def get_species_by_id(
    species_id: int,
    lang: Optional[str] = Query(None, description="Language code: en, ru, hy"),
    db: Session = Depends(get_db)
):
    species = db.query(AnimalSpecies).options(joinedload(AnimalSpecies.translations)).filter(AnimalSpecies.id == species_id).first()
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    return apply_language_filter(species, lang)

@app.post("/api/admin/species", response_model=AnimalSpeciesResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def create_species(species: AnimalSpeciesCreate, db: Session = Depends(get_db)):
    species_data = species.dict(exclude={'translations'})
    db_species = AnimalSpecies(**species_data)
    db.add(db_species)
    db.commit()
    db.refresh(db_species)
    
    # Save translations
    if species.translations:
        save_translations(db, db_species, species.translations, AnimalSpeciesTranslation, 'species_id')
        db.refresh(db_species)
    
    return apply_language_filter(db_species, None)

@app.put("/api/admin/species/{species_id}", response_model=AnimalSpeciesResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def update_species(species_id: int, species: AnimalSpeciesCreate, db: Session = Depends(get_db)):
    db_species = db.query(AnimalSpecies).filter(AnimalSpecies.id == species_id).first()
    if not db_species:
        raise HTTPException(status_code=404, detail="Species not found")
    
    species_data = species.dict(exclude={'translations'})
    for key, value in species_data.items():
        setattr(db_species, key, value)
    
    db.commit()
    
    # Update translations
    if species.translations:
        save_translations(db, db_species, species.translations, AnimalSpeciesTranslation, 'species_id')
    
    db.refresh(db_species)
    return apply_language_filter(db_species, None)

@app.delete("/api/admin/species/{species_id}", tags=["admin"], dependencies=[Depends(get_admin_user)])
def delete_species(species_id: int, db: Session = Depends(get_db)):
    db_species = db.query(AnimalSpecies).filter(AnimalSpecies.id == species_id).first()
    if not db_species:
        raise HTTPException(status_code=404, detail="Species not found")
    db.delete(db_species)
    db.commit()
    return {"message": "Species deleted successfully"}

# ==================== PRODUCT CATEGORY ENDPOINTS ====================
@app.get("/api/categories", response_model=List[ProductCategoryResponse], tags=["public"])
def get_all_categories(
    skip: int = 0,
    limit: int = 100,
    lang: Optional[str] = Query(None, description="Language code: en, ru, hy"),
    db: Session = Depends(get_db)
):
    categories = db.query(ProductCategory).options(joinedload(ProductCategory.translations)).offset(skip).limit(limit).all()
    return [apply_language_filter(c, lang) for c in categories]

@app.post("/api/admin/categories", response_model=ProductCategoryResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def create_category(category: ProductCategoryCreate, db: Session = Depends(get_db)):
    category_data = category.dict(exclude={'translations'})
    db_category = ProductCategory(**category_data)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    # Save translations
    if category.translations:
        save_translations(db, db_category, category.translations, ProductCategoryTranslation, 'category_id')
        db.refresh(db_category)
    
    return apply_language_filter(db_category, None)

@app.put("/api/admin/categories/{category_id}", response_model=ProductCategoryResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def update_category(category_id: int, category: ProductCategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(ProductCategory).filter(ProductCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    category_data = category.dict(exclude={'translations'})
    for key, value in category_data.items():
        setattr(db_category, key, value)
    
    db.commit()
    
    # Update translations
    if category.translations:
        save_translations(db, db_category, category.translations, ProductCategoryTranslation, 'category_id')
    
    db.refresh(db_category)
    return apply_language_filter(db_category, None)

@app.delete("/api/admin/categories/{category_id}", tags=["admin"], dependencies=[Depends(get_admin_user)])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(ProductCategory).filter(ProductCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}

# ==================== PRODUCT ENDPOINTS ====================
@app.get("/api/products", response_model=List[ProductResponse], tags=["public"])
def get_all_products(
    skip: int = 0,
    limit: int = 100,
    species_id: Optional[int] = None,
    category_id: Optional[int] = None,
    is_new: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    lang: Optional[str] = Query(None, description="Language code: en, ru, hy"),
    db: Session = Depends(get_db)
):
    query = db.query(Product).options(
        joinedload(Product.translations),
        joinedload(Product.species).joinedload(AnimalSpecies.translations),
        joinedload(Product.category).joinedload(ProductCategory.translations)
    )
    
    if species_id:
        query = query.filter(Product.species_id == species_id)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if is_new is not None:
        query = query.filter(Product.is_new == is_new)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if search:
        query = query.filter(Product.name.contains(search))
    
    products_orm = query.offset(skip).limit(limit).all()
    
    # Apply language filter and nested translations
    result = []
    for orm_p in products_orm:
        p_out = apply_language_filter(orm_p, lang)
        # nested species/category from ORM
        if orm_p.species:
            p_out.species = apply_language_filter(orm_p.species, lang)
        else:
            p_out.species = None
        if orm_p.category:
            p_out.category = apply_language_filter(orm_p.category, lang)
        else:
            p_out.category = None
        result.append(p_out)
    
    return result

@app.get("/api/products/new", response_model=List[ProductResponse], tags=["public"])
def get_new_products(
    skip: int = 0,
    limit: int = 20,
    lang: Optional[str] = Query(None, description="Language code: en, ru, hy"),
    db: Session = Depends(get_db)
):
    products_orm = db.query(Product).options(
        joinedload(Product.translations),
        joinedload(Product.species).joinedload(AnimalSpecies.translations),
        joinedload(Product.category).joinedload(ProductCategory.translations)
    ).filter(Product.is_new == True).offset(skip).limit(limit).all()
    
    result = []
    for orm_p in products_orm:
        p_out = apply_language_filter(orm_p, lang)
        if orm_p.species:
            p_out.species = apply_language_filter(orm_p.species, lang)
        else:
            p_out.species = None
        if orm_p.category:
            p_out.category = apply_language_filter(orm_p.category, lang)
        else:
            p_out.category = None
        result.append(p_out)
    
    return result

@app.get("/api/products/{product_id}", response_model=ProductResponse, tags=["public"])
def get_product_by_id(
    product_id: int,
    lang: Optional[str] = Query(None, description="Language code: en, ru, hy"),
    db: Session = Depends(get_db)
):
    orm_product = db.query(Product).options(
        joinedload(Product.translations),
        joinedload(Product.species).joinedload(AnimalSpecies.translations),
        joinedload(Product.category).joinedload(ProductCategory.translations)
    ).filter(Product.id == product_id).first()
    
    if not orm_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    p_out = apply_language_filter(orm_product, lang)
    if orm_product.species:
        p_out.species = apply_language_filter(orm_product.species, lang)
    else:
        p_out.species = None
    if orm_product.category:
        p_out.category = apply_language_filter(orm_product.category, lang)
    else:
        p_out.category = None
    
    return p_out

@app.post("/api/admin/products", response_model=ProductResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    product_data = product.dict(exclude={'translations'})
    db_product = Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Save translations
    if product.translations:
        save_translations(db, db_product, product.translations, ProductTranslation, 'product_id')
        db.refresh(db_product)
    
    # Return serializable object
    p_out = apply_language_filter(db_product, None)
    # add nested relations if exist
    if db_product.species:
        p_out.species = apply_language_filter(db_product.species, None)
    else:
        p_out.species = None
    if db_product.category:
        p_out.category = apply_language_filter(db_product.category, None)
    else:
        p_out.category = None
    return p_out

@app.put("/api/admin/products/{product_id}", response_model=ProductResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_data = product.dict(exclude_unset=True, exclude={'translations'})
    for key, value in product_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    
    # Update translations
    if product.translations:
        save_translations(db, db_product, product.translations, ProductTranslation, 'product_id')
    
    db.refresh(db_product)
    p_out = apply_language_filter(db_product, None)
    if db_product.species:
        p_out.species = apply_language_filter(db_product.species, None)
    else:
        p_out.species = None
    if db_product.category:
        p_out.category = apply_language_filter(db_product.category, None)
    else:
        p_out.category = None
    return p_out

@app.delete("/api/admin/products/{product_id}", tags=["admin"], dependencies=[Depends(get_admin_user)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}

# ==================== NEWS ENDPOINTS ====================
@app.get("/api/news", response_model=List[NewsResponse], tags=["public"])
def get_all_news(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    lang: Optional[str] = Query(None, description="Language code: en, ru, hy"),
    db: Session = Depends(get_db)
):
    query = db.query(News).options(joinedload(News.translations)).order_by(News.published_at.desc())
    
    if search:
        query = query.filter(News.title.contains(search) | News.content.contains(search))
    
    news_list = query.offset(skip).limit(limit).all()
    return [apply_language_filter(n, lang) for n in news_list]

@app.get("/api/news/{news_id}", response_model=NewsResponse, tags=["public"])
def get_news_by_id(
    news_id: int,
    lang: Optional[str] = Query(None, description="Language code: en, ru, hy"),
    db: Session = Depends(get_db)
):
    news = db.query(News).options(joinedload(News.translations)).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return apply_language_filter(news, lang)

@app.post("/api/admin/news", response_model=NewsResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def create_news(news: NewsCreate, db: Session = Depends(get_db)):
    news_data = news.dict(exclude={'translations'})
    db_news = News(**news_data)
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    
    # Save translations
    if news.translations:
        save_translations(db, db_news, news.translations, NewsTranslation, 'news_id')
        db.refresh(db_news)
    
    return apply_language_filter(db_news, None)

@app.put("/api/admin/news/{news_id}", response_model=NewsResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def update_news(news_id: int, news: NewsUpdate, db: Session = Depends(get_db)):
    db_news = db.query(News).filter(News.id == news_id).first()
    if not db_news:
        raise HTTPException(status_code=404, detail="News not found")
    
    news_data = news.dict(exclude_unset=True, exclude={'translations'})
    for key, value in news_data.items():
        setattr(db_news, key, value)
    
    db.commit()
    
    # Update translations
    if news.translations:
        save_translations(db, db_news, news.translations, NewsTranslation, 'news_id')
    
    db.refresh(db_news)
    return apply_language_filter(db_news, None)

@app.delete("/api/admin/news/{news_id}", tags=["admin"], dependencies=[Depends(get_admin_user)])
def delete_news(news_id: int, db: Session = Depends(get_db)):
    db_news = db.query(News).filter(News.id == news_id).first()
    if not db_news:
        raise HTTPException(status_code=404, detail="News not found")
    db.delete(db_news)
    db.commit()
    return {"message": "News deleted successfully"}

# ==================== STATISTICS ENDPOINTS ====================
@app.get("/api/admin/statistics", tags=["admin"], dependencies=[Depends(get_admin_user)])
def get_statistics(db: Session = Depends(get_db)):
    return {
        "total_products": db.query(Product).count(),
        "total_species": db.query(AnimalSpecies).count(),
        "total_categories": db.query(ProductCategory).count(),
        "total_news": db.query(News).count(),
        "new_products": db.query(Product).filter(Product.is_new == True).count()
    }

# Root endpoint
@app.get("/", tags=["public"])
def root():
    return {
        "message": "Animal Store API with Multi-Language Support",
        "version": "2.0.0",
        "docs": "/docs",
        "supported_languages": ["en", "ru", "hy"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
