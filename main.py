from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from db import (
    Base, engine, SessionLocal,
    User, UserCreate, UserResponse, Token,
    AnimalTypes, AnimalTypesCreate, AnimalTypesUpdate, AnimalTypesTranslation,
    ProductCategory, ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryTranslation,
    Product, ProductCreate, ProductUpdate, ProductTranslation, 
    ProductFeature, ProductFeatureTranslation,
    News, NewsCreate, NewsUpdate, NewsTranslation, NewsFeatures, NewsFeaturesTranslation, NewsAuthor
)
from helpers import AppHelpers
import schemas

# ---------------- INIT ----------------
# Ensure tables exist
# with engine.begin() as conn:
#     # Drop all tables with CASCADE
#     conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
#     conn.execute(text("DROP TABLE IF EXISTS animal_types CASCADE"))
#     conn.execute(text("DROP TABLE IF EXISTS animal_types_translations CASCADE"))
#     conn.execute(text("DROP TABLE IF EXISTS product_categories CASCADE"))
#     conn.execute(text("DROP TABLE IF EXISTS product_categories_translations CASCADE"))
#     conn.execute(text("DROP TABLE IF EXISTS products CASCADE"))
#     conn.execute(text("DROP TABLE IF EXISTS product_translations CASCADE"))
#     conn.execute(text("DROP TABLE IF EXISTS product_features CASCADE"))
#     conn.execute(text("DROP TABLE IF EXISTS product_features_translations CASCADE"))
#     conn.execute(text("DROP TABLE IF EXISTS news_authors CASCADE"))
#     conn.execute(text("DROP TABLE IF EXISTS news_author_translations CASCADE"))
#     conn.execute(text("DROP TABLE IF EXISTS news CASCADE"))
#     conn.execute(text("DROP TABLE IF EXISTS news_translations CASCADE"))
#     conn.execute(text("DROP TABLE IF EXISTS news_features CASCADE"))
#     conn.execute(text("DROP TABLE IF EXISTS news_features_translations CASCADE"))

# Base.metadata.create_all(bind=engine)

fastapi_app = FastAPI(title="Veterinary Pharmacy API", version="2.0.0")

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ---------------- DEPENDENCIES ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return AppHelpers.get_user_by_token(db, token)

def get_admin_user(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

# ---------------- AUTH ROUTES ----------------
@fastapi_app.post("/auth/register", response_model=UserResponse, tags=["auth"])
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=AppHelpers.get_password_hash(user.password),
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@fastapi_app.post("/auth/login", response_model=Token, tags=["auth"])
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not AppHelpers.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = AppHelpers.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@fastapi_app.get("/auth/me", response_model=UserResponse, tags=["auth"])
def get_me(user: User = Depends(get_current_user)):
    return user

# ---------------- PUBLIC ROUTES ----------------
@fastapi_app.get("/home", tags=["public"])
def home(lang: Optional[str] = None, db: Session = Depends(get_db)):
    # Fetch new products
    products = db.query(Product)\
        .options(
            joinedload(Product.translations), 
            joinedload(Product.features).joinedload(ProductFeature.translations)
        )\
        .filter(Product.is_new == True)\
        .limit(8).all()

    # Fetch latest news
    news = db.query(News)\
        .options(
            joinedload(News.translations), 
            joinedload(News.author).joinedload(NewsAuthor.translations),
            joinedload(News.features).joinedload(NewsFeatures.translations)
        )\
        .order_by(News.published_at.desc())\
        .limit(6).all()

    return {
        "new_products": [AppHelpers.apply_language_filter(p, lang) for p in products],
        "latest_news": [AppHelpers.apply_language_filter(n, lang) for n in news],
    }

# --- Types ---
@fastapi_app.get("/types", tags=["public"])
def list_types(lang: Optional[str] = None, db: Session = Depends(get_db)):
    items = db.query(AnimalTypes).options(joinedload(AnimalTypes.translations)).all()
    return [AppHelpers.apply_language_filter(i, lang) for i in items]

@fastapi_app.get("/types/{id}", tags=["public"])
def get_type(id: int, lang: Optional[str] = None, db: Session = Depends(get_db)):
    item = db.query(AnimalTypes)\
        .options(joinedload(AnimalTypes.translations))\
        .filter(AnimalTypes.id == id)\
        .first()
    if not item:
        raise HTTPException(404, "Species not found")
    return AppHelpers.apply_language_filter(item, lang)

# --- Categories ---
@fastapi_app.get("/categories", tags=["public"])
def list_categories(lang: Optional[str] = None, db: Session = Depends(get_db)):
    items = db.query(ProductCategory).options(joinedload(ProductCategory.translations)).all()
    return [AppHelpers.apply_language_filter(i, lang) for i in items]

@fastapi_app.get("/categories/{id}", tags=["public"])
def get_category(id: int, lang: Optional[str] = None, db: Session = Depends(get_db)):
    item = db.query(ProductCategory)\
        .options(joinedload(ProductCategory.translations))\
        .filter(ProductCategory.id == id)\
        .first()
    if not item:
        raise HTTPException(404, "Category not found")
    return AppHelpers.apply_language_filter(item, lang)

# --- Products ---
@fastapi_app.get("/products", tags=["public"])
def list_products(
    lang: Optional[str] = None,
    category_id: Optional[int] = None,
    subcategory_id: Optional[int] = None,
    types_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
):
    """
    List products with optional filters:
    - category_id, subcategory_id, types_id
    - search (partial match against fallback product.name)
    - pagination via page & per_page
    """
    query = db.query(Product).options(
        joinedload(Product.translations),
        joinedload(Product.features).joinedload(ProductFeature.translations),
    )

    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if subcategory_id is not None:
        query = query.filter(Product.subcategory_id == subcategory_id)
    if types_id is not None:
        query = query.filter(Product.types_id == types_id)
    if search:
        # Search against fallback name; optionally could join translations for i18n search
        like_str = f"%{search}%"
        query = query.filter(Product.name.ilike(like_str))

    # Pagination
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 20

    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return [AppHelpers.apply_language_filter(i, lang) for i in items]

@fastapi_app.get("/products/{id}", tags=["public"])
def get_product(id: int, lang: Optional[str] = None, db: Session = Depends(get_db)):
    item = db.query(Product)\
        .options(
            joinedload(Product.translations), 
            joinedload(Product.features).joinedload(ProductFeature.translations)
        )\
        .filter(Product.id == id)\
        .first()
    if not item:
        raise HTTPException(404, "Product not found")
    return AppHelpers.apply_language_filter(item, lang)

# --- News ---
@fastapi_app.get("/news", tags=["public"])
def list_news(lang: Optional[str] = None, db: Session = Depends(get_db)):
    items = db.query(News)\
        .options(
            joinedload(News.translations), 
            joinedload(News.author).joinedload(NewsAuthor.translations),
            joinedload(News.features).joinedload(NewsFeatures.translations)
        )\
        .all()
    return [AppHelpers.apply_language_filter(i, lang) for i in items]

@fastapi_app.get("/news/{id}", tags=["public"])
def get_news_detail(id: int, lang: Optional[str] = None, db: Session = Depends(get_db)):
    item = db.query(News)\
        .options(
            joinedload(News.translations), 
            joinedload(News.author).joinedload(NewsAuthor.translations),
            joinedload(News.features).joinedload(NewsFeatures.translations)
        )\
        .filter(News.id == id)\
        .first()
    if not item:
        raise HTTPException(404, "News not found")
    return AppHelpers.apply_language_filter(item, lang)

# ---------------- ADMIN ROUTES ----------------
# --- Types ---
@fastapi_app.post("/admin/types", tags=["admin"])
def create_type(data: AnimalTypesCreate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = AnimalTypes(name=data.name, image_url=data.image_url)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    AppHelpers.save_translations(db, db_obj, data.translations, AnimalTypesTranslation, "types_id")
    return AppHelpers.apply_language_filter(db_obj)

@fastapi_app.put("/admin/types/{id}", tags=["admin"])
def update_type(id: int, data: AnimalTypesUpdate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(AnimalTypes, id)
    if not db_obj:
        raise HTTPException(404, "Not found")
    
    if data.name: 
        db_obj.name = data.name
    if data.image_url: 
        db_obj.image_url = data.image_url
    
    db.commit()
    if data.translations:
        AppHelpers.save_translations(db, db_obj, data.translations, AnimalTypesTranslation, "types_id")
    
    return AppHelpers.apply_language_filter(db_obj)

@fastapi_app.delete("/admin/types/{id}", tags=["admin"])
def delete_type(id: int, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(AnimalTypes, id)
    if not db_obj: 
        raise HTTPException(404, "Not found")
    db.delete(db_obj)
    db.commit()
    return {"status": "deleted"}

# --- Categories ---
@fastapi_app.post("/admin/categories", tags=["admin"])
def create_category(data: ProductCategoryCreate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = ProductCategory(name=data.name)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    AppHelpers.save_translations(db, db_obj, data.translations, ProductCategoryTranslation, "category_id")
    return AppHelpers.apply_language_filter(db_obj)

@fastapi_app.put("/admin/categories/{id}", tags=["admin"])
def update_category(id: int, data: ProductCategoryUpdate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(ProductCategory, id)
    if not db_obj: 
        raise HTTPException(404, "Not found")
    
    if data.name: 
        db_obj.name = data.name
    db.commit()
    
    if data.translations:
        AppHelpers.save_translations(db, db_obj, data.translations, ProductCategoryTranslation, "category_id")
    return AppHelpers.apply_language_filter(db_obj)

@fastapi_app.delete("/admin/categories/{id}", tags=["admin"])
def delete_category(id: int, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(ProductCategory, id)
    if not db_obj: 
        raise HTTPException(404, "Not found")
    db.delete(db_obj)
    db.commit()
    return {"status": "deleted"}

# --- Products ---
@fastapi_app.post("/admin/products", tags=["admin"])
def create_product(product_in: schemas.ProductCreate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    # 1. Create Product (price, types_id, category_id can be None)
    new_product = Product(
        name=product_in.name,
        price=product_in.price,
        stock=product_in.stock,
        manufacturer=product_in.manufacturer,
        image_url=product_in.image_url,
        is_new=product_in.is_new,
        types_id=product_in.types_id,
        category_id=product_in.category_id,
        subcategory_id=product_in.subcategory_id
    )
    db.add(new_product)
    db.flush()  # Populates new_product.id

    # 2. Add Translations
    for lang, trans_data in product_in.translations.items():
        db.add(ProductTranslation(
            product_id=new_product.id,
            language=lang,
            name=trans_data.name,
            description=trans_data.description
        ))

    # 3. Add Features
    for feature_in in product_in.features:
        new_feature = ProductFeature(
            product_id=new_product.id,
            title=feature_in.title
        )
        db.add(new_feature)
        db.flush()

        for lang, f_trans in feature_in.translations.items():
            db.add(ProductFeatureTranslation(
                feature_id=new_feature.id,
                language=lang,
                title=f_trans.title,
                description=f_trans.description
            ))

    db.commit()
    db.refresh(new_product)
    return AppHelpers.apply_language_filter(new_product)

@fastapi_app.put("/admin/products/{id}", tags=["admin"])
def update_product(id: int, data: schemas.ProductUpdate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(Product, id)
    if not db_obj: 
        raise HTTPException(404, "Not found")
    
    # Update scalar fields (only those provided)
    update_data = data.dict(exclude={"translations", "features"}, exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)

    # Handle translations (will replace existing translations)
    if getattr(data, "translations", None):
        AppHelpers.save_translations(db, db_obj, data.translations, ProductTranslation, "product_id")

    # Handle features: create, update, delete
    # If features is provided (even empty list), sync features to match client-provided list
    if hasattr(data, "features"):
        incoming = data.features or []

        # Load existing features from DB
        existing_features = db.query(ProductFeature).filter(ProductFeature.product_id == db_obj.id).all()
        existing_by_id = {f.id: f for f in existing_features}

        incoming_ids = set()

        for f_in in incoming:
            # accept either dict-like or pydantic object
            f_id = None
            if isinstance(f_in, dict):
                f_id = f_in.get("id")
                f_title = f_in.get("title")
                f_trans = f_in.get("translations")
            else:
                f_id = getattr(f_in, "id", None)
                f_title = getattr(f_in, "title", None)
                f_trans = getattr(f_in, "translations", None)

            if f_id:
                incoming_ids.add(f_id)
                feature_obj = existing_by_id.get(f_id) or db.get(ProductFeature, f_id)
                if not feature_obj:
                    # skip invalid id
                    continue
                if f_title is not None:
                    feature_obj.title = f_title
                db.flush()
                if f_trans:
                    AppHelpers.save_translations(db, feature_obj, f_trans, ProductFeatureTranslation, "feature_id")
            else:
                # create new feature
                new_feature = ProductFeature(product_id=db_obj.id, title=f_title)
                db.add(new_feature)
                db.flush()
                if f_trans:
                    AppHelpers.save_translations(db, new_feature, f_trans, ProductFeatureTranslation, "feature_id")

        # Delete features that are not present in incoming_ids
        for existing in existing_features:
            if existing.id not in incoming_ids and (incoming is not None):
                db.delete(existing)

    # Final commit and refresh
    db.commit()
    db.refresh(db_obj)

    return AppHelpers.apply_language_filter(db_obj)

@fastapi_app.delete("/admin/products/{id}", tags=["admin"])
def delete_product(id: int, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(Product, id)
    if not db_obj: 
        raise HTTPException(404, "Not found")
    db.delete(db_obj)
    db.commit()
    return {"status": "deleted"}

# --- News ---
# --- News ---
def _extract_title_from_translations(trans_map) -> str:
    """Utility: derive a fallback title from a translations map (prefer 'en').
    Accepts dicts or pydantic-like objects.
    """
    if not trans_map:
        return ""
    try:
        if isinstance(trans_map, dict):
            candidate = trans_map.get("en") or next(iter(trans_map.values()))
            if isinstance(candidate, dict):
                return candidate.get("title", "") or ""
            return getattr(candidate, "title", "") or ""
        en = getattr(trans_map, "en", None)
        candidate = en or next(iter(vars(trans_map).values()))
        return getattr(candidate, "title", "") or ""
    except Exception:
        return ""

@fastapi_app.post("/admin/news", tags=["admin"])
def create_news(data: schemas.NewsCreate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    # 1. Create core News
    news_obj = News(
        image_url=data.image_url,
        author_id=data.author_id
    )
    db.add(news_obj)
    db.flush()  # Populate news_obj.id

    # 2. Add translations
    for lang, trans_data in data.translations.items():
        db.add(NewsTranslation(
            news_id=news_obj.id,
            language=lang,
            title=trans_data.get("title", ""),
            description=trans_data.get("description", "")
        ))

    # 3. Add features and their translations
    for feature_in in data.features or []:
        trans_map = getattr(feature_in, "translations", None) or (feature_in.get("translations") if isinstance(feature_in, dict) else None)
        title_val = _extract_title_from_translations(trans_map)
        feature_obj = NewsFeatures(news_id=news_obj.id, title=title_val)
        db.add(feature_obj)
        db.flush()  # Populate feature_obj.id

        # iterate translations (handle dict or pydantic values)
        for lang, f_trans in (trans_map or {}).items():
            if isinstance(f_trans, dict):
                t_title = f_trans.get("title", "")
                t_desc = f_trans.get("description", "")
            else:
                t_title = getattr(f_trans, "title", "")
                t_desc = getattr(f_trans, "description", "")

            db.add(NewsFeaturesTranslation(
                feature_id=feature_obj.id,
                language=lang,
                title=t_title,
                description=t_desc
            ))

    db.commit()
    db.refresh(news_obj)
    return AppHelpers.apply_language_filter(news_obj)


@fastapi_app.put("/admin/news/{id}", tags=["admin"])
def update_news(id: int, data: schemas.NewsUpdate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(News, id)
    if not db_obj:
        raise HTTPException(404, "Not found")

    update_data = data.dict(exclude={"translations", "features"}, exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)

    db.commit()

    # Update translations
    if data.translations:
        AppHelpers.save_translations(db, db_obj, data.translations, NewsTranslation, "news_id")

    # Update features and their translations
    if data.features:
        for feature_in in data.features:
            if hasattr(feature_in, "id") and feature_in.id:
                feature_obj = db.get(NewsFeatures, feature_in.id)
            else:
                trans_map = getattr(feature_in, "translations", None) or (feature_in.get("translations") if isinstance(feature_in, dict) else None)
                title_val = _extract_title_from_translations(trans_map)
                feature_obj = NewsFeatures(news_id=db_obj.id, title=title_val)
                db.add(feature_obj)
                db.flush()
            # feature_in.translations expected to be a dict of language -> {title, description}
            if getattr(feature_in, "translations", None):
                AppHelpers.save_translations(
                    db,
                    feature_obj,
                    feature_in.translations,
                    NewsFeaturesTranslation,
                    "feature_id",
                )

    db.commit()
    db.refresh(db_obj)
    return AppHelpers.apply_language_filter(db_obj)


@fastapi_app.delete("/admin/news/{id}", tags=["admin"])
def delete_news(id: int, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(News, id)
    if not db_obj:
        raise HTTPException(404, "Not found")
    db.delete(db_obj)
    db.commit()
    return {"status": "deleted"}

@fastapi_app.get("/admin/statistics", tags=["admin"])
def statistics(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    return {
        "total_users": db.query(User).count(),
        "total_types": db.query(AnimalTypes).count(),
        "total_categories": db.query(ProductCategory).count(),
        "total_products": db.query(Product).count(),
        "total_news": db.query(News).count(),
    }