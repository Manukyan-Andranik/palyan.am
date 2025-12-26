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
with engine.begin() as conn:
    # Drop all tables with CASCADE
    conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS animal_types CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS animal_types_translations CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS product_categories CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS product_categories_translations CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS products CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS product_translations CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS product_features CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS product_features_translations CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS news_authors CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS news_author_translations CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS news CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS news_translations CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS news_features CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS news_features_translations CASCADE"))
Base.metadata.create_all(bind=engine)

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
def list_products(lang: Optional[str] = None, db: Session = Depends(get_db)):
    items = db.query(Product)\
        .options(
            joinedload(Product.translations),
            joinedload(Product.features).joinedload(ProductFeature.translations)
        )\
        .all()
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
        category_id=product_in.category_id
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
def update_product(id: int, data: ProductUpdate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(Product, id)
    if not db_obj: 
        raise HTTPException(404, "Not found")
    
    update_data = data.dict(exclude={"translations"}, exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    
    db.commit()
    if data.translations:
        AppHelpers.save_translations(db, db_obj, data.translations, ProductTranslation, "product_id")
        
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
@fastapi_app.post("/admin/news", tags=["admin"])
def create_news(data: NewsCreate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    # Core News
    db_obj = News(title=data.title, image_url=data.image_url, author_id=data.author_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # Translations
    AppHelpers.save_translations(db, db_obj, data.translations, NewsTranslation, "news_id")
    
    # Features (if any)
    if data.features:
        for feat in data.features:
            db_feat = NewsFeatures(news_id=db_obj.id, title=feat.get("title", ""))
            db.add(db_feat)
            db.commit()
            db.refresh(db_feat)
            AppHelpers.save_translations(db, db_feat, feat.get("translations", {}), NewsFeaturesTranslation, "feature_id")

    return AppHelpers.apply_language_filter(db_obj)

@fastapi_app.put("/admin/news/{id}", tags=["admin"])
def update_news(id: int, data: NewsUpdate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(News, id)
    if not db_obj: 
        raise HTTPException(404, "Not found")
    
    if data.title: 
        db_obj.title = data.title
    if data.image_url: 
        db_obj.image_url = data.image_url
    if data.author_id: 
        db_obj.author_id = data.author_id
    
    db.commit()
    if data.translations:
        AppHelpers.save_translations(db, db_obj, data.translations, NewsTranslation, "news_id")
        
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