import os
import asyncio
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload


from db import (
    SessionLocal,
    User, UserCreate, UserResponse, Token,
    ProductCategory, ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryTranslation,
    ProductSubcategory, ProductSubcategoryCreate, ProductSubcategoryUpdate, ProductSubcategoryTranslation,
    Product, ProductCreate, ProductUpdate, ProductTranslation, 
    ProductFeature, ProductFeatureTranslation,
    News, NewsCreate, NewsUpdate, NewsTranslation, NewsFeatures, NewsFeaturesTranslation, 
    NewsAuthor, NewsAuthorTranslation,
    NewsAuthorCreate, NewsAuthorUpdate
)

from helpers import AppHelpers
import schemas

fastapi_app = FastAPI(
    title="Veterinary Pharmacy API",
    description="API for veterinary drugs and pet supplies store",
    version="2.0.0",
    root_path="/api",
)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://palyan.onrender.com",
        "https://palyan.am"
    ],    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ==================== DEPENDENCIES ====================

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

# ==================== AUTH ROUTES ====================

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

# ==================== PUBLIC ROUTES ====================

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

# --- Categories ---
@fastapi_app.get("/categories", tags=["public"])
def list_categories(lang: Optional[str] = None, db: Session = Depends(get_db)):
    items = db.query(ProductCategory)\
        .options(
            joinedload(ProductCategory.translations),
            joinedload(ProductCategory.subcategories).joinedload(ProductSubcategory.translations)
        ).order_by(ProductCategory.id).all()
    
    result = []
    for item in items:
        # Build name map
        name_map = {}
        for trans in item.translations:
            name_map[trans.language.value] = trans.name
        
        # If lang is specified, flatten to just that language
        if lang and lang in name_map:
            category_name = name_map[lang]
        else:
            category_name = name_map
        
        # Build subcategories
        subcats = []
        for sc in item.subcategories:
            subcat_name_map = {}
            for trans in sc.translations:
                subcat_name_map[trans.language.value] = trans.name
            
            # If lang is specified, flatten to just that language
            if lang and lang in subcat_name_map:
                subcat_name = subcat_name_map[lang]
            else:
                subcat_name = subcat_name_map
            
            subcats.append({
                "id": sc.id,
                "name": subcat_name
            })
        
        result.append({
            "id": item.id,
            "name": category_name,
            "subcategories": subcats
        })
    return result

@fastapi_app.get("/categories/{id}", tags=["public"])
def get_category(id: int, lang: Optional[str] = None, db: Session = Depends(get_db)):
    item = db.query(ProductCategory)\
        .options(
            joinedload(ProductCategory.translations),
            joinedload(ProductCategory.subcategories).joinedload(ProductSubcategory.translations)
        )\
        .filter(ProductCategory.id == id)\
        .first()
    if not item:
        raise HTTPException(404, "Category not found")
    
    # Build name map
    name_map = {}
    for trans in item.translations:
        name_map[trans.language.value] = trans.name
    
    # If lang is specified, flatten to just that language
    if lang and lang in name_map:
        category_name = name_map[lang]
    else:
        category_name = name_map
    
    # Build subcategories
    subcats = []
    for sc in item.subcategories:
        subcat_name_map = {}
        for trans in sc.translations:
            subcat_name_map[trans.language.value] = trans.name
        
        # If lang is specified, flatten to just that language
        if lang and lang in subcat_name_map:
            subcat_name = subcat_name_map[lang]
        else:
            subcat_name = subcat_name_map
        
        subcats.append({
            "id": sc.id,
            "name": subcat_name
        })
    
    return {
        "id": item.id,
        "name": category_name,
        "subcategories": subcats
    }

# --- Products ---
@fastapi_app.get("/products", tags=["public"])
def list_products(
    lang: Optional[str] = None,
    category_id: Optional[int] = None,
    subcategory_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
):
    """
    List products with optional filters:
    - category_id, subcategory_id
    - search (partial match against fallback product.name)
    - pagination via page & per_page
    """
    query = db.query(Product).options(
        joinedload(Product.translations),
        joinedload(Product.features).joinedload(ProductFeature.translations),
    ).order_by(Product.id)

    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if subcategory_id is not None:
        query = query.filter(Product.subcategory_id == subcategory_id)
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
            joinedload(Product.features).joinedload(ProductFeature.translations),
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

# ==================== ADMIN ROUTES ====================

@fastapi_app.post("/upload", tags=["admin"])
async def upload_image(file: UploadFile = File(...),  db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    file_bytes = await file.read()

    upload_result = AppHelpers.image_manager.files.upload(
        file=file_bytes,
        file_name=file.filename,
        folder="/uploads",
    )

    return {
        "url": upload_result.url,
        "fileId": upload_result.file_id,
        "thumbnail_url": upload_result.thumbnail_url,
    }

# --- Categories ---

@fastapi_app.post("/admin/categories", tags=["admin"])
def create_category(data: ProductCategoryCreate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    # Extract fallback name from multilingual dict
    fallback_name = next(iter(data.name.values())) if data.name else ""
    
    # Create category
    db_obj = ProductCategory(name=fallback_name)
    db.add(db_obj)
    db.flush()
    
    # Add category translations (name is multilingual dict)
    AppHelpers.save_translations(db, db_obj, data.name, ProductCategoryTranslation, "category_id", name_field="name")
    
    # Add subcategories if provided
    if data.subcategories:
        for subcat_data in data.subcategories:
            # Extract name from multilingual dict
            subcat_name_dict = subcat_data.get("name", {})
            subcat_fallback_name = next(iter(subcat_name_dict.values())) if isinstance(subcat_name_dict, dict) and subcat_name_dict else ""
            
            subcat = ProductSubcategory(category_id=db_obj.id, name=subcat_fallback_name)
            db.add(subcat)
            db.flush()
            
            # Add subcategory translations (name is multilingual dict)
            if isinstance(subcat_name_dict, dict) and subcat_name_dict:
                AppHelpers.save_translations(db, subcat, subcat_name_dict, ProductSubcategoryTranslation, "subcategory_id", name_field="name")
    
    db.commit()
    db.refresh(db_obj)
    return AppHelpers.apply_language_filter(db_obj)

@fastapi_app.put("/admin/categories/{id}", tags=["admin"])
def update_category(id: int, data: ProductCategoryUpdate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(ProductCategory, id)
    if not db_obj: 
        raise HTTPException(404, "Not found")
    
    # Update name if provided (multilingual dict)
    if data.name:
        # Update fallback name from first value
        fallback_name = next(iter(data.name.values())) if data.name else ""
        db_obj.name = fallback_name
        # Update translations
        AppHelpers.save_translations(db, db_obj, data.name, ProductCategoryTranslation, "category_id", name_field="name")
    
    # Update subcategories if provided
    if data.subcategories is not None:
        # Delete existing subcategories and recreate
        db.query(ProductSubcategory).filter(ProductSubcategory.category_id == db_obj.id).delete(synchronize_session=False)
        
        for subcat_data in data.subcategories:
            # Extract name from multilingual dict
            subcat_name_dict = subcat_data.get("name", {})
            subcat_fallback_name = next(iter(subcat_name_dict.values())) if isinstance(subcat_name_dict, dict) and subcat_name_dict else ""
            
            subcat = ProductSubcategory(category_id=db_obj.id, name=subcat_fallback_name)
            db.add(subcat)
            db.flush()
            
            # Add subcategory translations (name is multilingual dict)
            if isinstance(subcat_name_dict, dict) and subcat_name_dict:
                AppHelpers.save_translations(db, subcat, subcat_name_dict, ProductSubcategoryTranslation, "subcategory_id", name_field="name")
    
    db.commit()
    db.refresh(db_obj)
    return AppHelpers.apply_language_filter(db_obj)

@fastapi_app.delete("/admin/categories/{id}", tags=["admin"])
def delete_category(id: int, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(ProductCategory, id)
    if not db_obj: 
        raise HTTPException(404, "Not found")
    db.delete(db_obj)
    db.commit()
    return {"status": "deleted"}

# --- Subcategories ---

@fastapi_app.post("/admin/subcategories", tags=["admin"])
def create_subcategory(data: ProductSubcategoryCreate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    # Verify category exists
    category = db.get(ProductCategory, data.category_id)
    if not category:
        raise HTTPException(404, "Category not found")
    
    # Extract fallback name from multilingual dict
    fallback_name = next(iter(data.name.values())) if data.name else ""
    
    # Create subcategory
    db_obj = ProductSubcategory(category_id=data.category_id, name=fallback_name)
    db.add(db_obj)
    db.flush()
    
    # Add translations (name is multilingual dict)
    AppHelpers.save_translations(db, db_obj, data.name, ProductSubcategoryTranslation, "subcategory_id", name_field="name")
    
    db.commit()
    db.refresh(db_obj)
    return AppHelpers.apply_language_filter(db_obj)

@fastapi_app.put("/admin/subcategories/{id}", tags=["admin"])
def update_subcategory(id: int, data: ProductSubcategoryUpdate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(ProductSubcategory, id)
    if not db_obj:
        raise HTTPException(404, "Not found")
    
    # Update name if provided (multilingual dict)
    if data.name:
        # Update fallback name from first value
        fallback_name = next(iter(data.name.values())) if data.name else ""
        db_obj.name = fallback_name
        # Update translations
        AppHelpers.save_translations(db, db_obj, data.name, ProductSubcategoryTranslation, "subcategory_id", name_field="name")
    
    db.commit()
    db.refresh(db_obj)
    return AppHelpers.apply_language_filter(db_obj)

@fastapi_app.delete("/admin/subcategories/{id}", tags=["admin"])
def delete_subcategory(id: int, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(ProductSubcategory, id)
    if not db_obj:
        raise HTTPException(404, "Not found")
    db.delete(db_obj)
    db.commit()
    return {"status": "deleted"}

# --- Products ---

@fastapi_app.post("/admin/products", tags=["admin"])
def create_product(product_in: schemas.ProductCreate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    # Extract name from multilingual dict (use first available value as fallback)
    fallback_name = ""
    if product_in.name and isinstance(product_in.name, dict):
        fallback_name = next(iter(product_in.name.values())) if product_in.name else ""
    elif isinstance(product_in.name, str):
        fallback_name = product_in.name
    
    # 1. Create Product
    new_product = Product(
        name=fallback_name,
        price=product_in.price,
        stock=product_in.stock,
        manufacturer=product_in.manufacturer,
        image_url=product_in.image_url,
        is_new=product_in.is_new,
        category_id=product_in.category_id,
        subcategory_id=product_in.subcategory_id
    )
    db.add(new_product)
    db.flush()  # Populates new_product.id

    # 2. Add Translations for name and description
    if product_in.name and isinstance(product_in.name, dict):
        AppHelpers.save_translations(db, new_product, product_in.name, ProductTranslation, "product_id", name_field="name")
    
    # Description is required, so always save it
    if product_in.description and isinstance(product_in.description, dict):
        AppHelpers.save_translations(db, new_product, product_in.description, ProductTranslation, "product_id", name_field="description")

    # 3. Add Features
    if product_in.features:
        for feature_in in product_in.features:
            f_title = feature_in.get("title") if isinstance(feature_in, dict) else None
            f_description = feature_in.get("description") if isinstance(feature_in, dict) else None
            
            # If title is a dict (multilingual), use first value as fallback
            if isinstance(f_title, dict):
                f_title_fallback = next(iter(f_title.values())) if f_title else ""
                f_title_trans = f_title
            else:
                f_title_fallback = f_title or ""
                f_title_trans = None
            
            # If description is a dict (multilingual), use first value as fallback
            if isinstance(f_description, dict):
                f_description_fallback = next(iter(f_description.values())) if f_description else None
                f_description_trans = f_description
            else:
                f_description_fallback = f_description
                f_description_trans = None
            
            new_feature = ProductFeature(
                product_id=new_product.id,
                title=f_title_fallback
            )
            db.add(new_feature)
            db.flush()

            # Add title translations
            if f_title_trans and isinstance(f_title_trans, dict):
                AppHelpers.save_translations(db, new_feature, f_title_trans, ProductFeatureTranslation, "feature_id", name_field="title")
            
            # Add description translations
            if f_description_trans and isinstance(f_description_trans, dict):
                AppHelpers.save_translations(db, new_feature, f_description_trans, ProductFeatureTranslation, "feature_id", name_field="description")

    db.commit()
    db.refresh(new_product)
    return AppHelpers.apply_language_filter(new_product)

@fastapi_app.put("/admin/products/{id}", tags=["admin"])
def update_product(id: int, data: schemas.ProductUpdate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(Product, id)
    if not db_obj: 
        raise HTTPException(404, "Not found")
    
    # Update scalar fields (only those provided, excluding name and description which are translations)
    update_data = data.dict(exclude={"name", "description", "features"}, exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_obj, key, value)

    # Handle name translations: if name dict provided, sync translations for ProductTranslation
    if data.name and isinstance(data.name, dict):
        AppHelpers.save_translations(db, db_obj, data.name, ProductTranslation, "product_id", name_field="name")

    # Handle description translations: if description dict provided, sync translations for ProductTranslation
    if data.description and isinstance(data.description, dict):
        AppHelpers.save_translations(db, db_obj, data.description, ProductTranslation, "product_id", name_field="description")

    # Handle features: create, update, delete
    # If features is provided (even empty list), sync features to match client-provided list
    if data.features is not None:
        incoming = data.features or []

        # Load existing features from DB
        existing_features = db.query(ProductFeature).filter(ProductFeature.product_id == db_obj.id).all()
        existing_by_id = {f.id: f for f in existing_features}

        incoming_ids = set()

        for f_in in incoming:
            # accept dict-like format
            f_id = f_in.get("id") if isinstance(f_in, dict) else None
            f_title = f_in.get("title") if isinstance(f_in, dict) else None
            f_description = f_in.get("description") if isinstance(f_in, dict) else None
            f_trans_title = None
            f_trans_desc = None

            # If title is a dict (multilingual), use it as translations for title field
            if isinstance(f_title, dict):
                f_trans_title = f_title
                # Use first language value as fallback title
                f_title = next(iter(f_title.values())) if f_title else None

            # If description is a dict (multilingual), use it as translations for description field
            if isinstance(f_description, dict):
                f_trans_desc = f_description
                # Use first language value as fallback description
                f_description = next(iter(f_description.values())) if f_description else None

            if f_id:
                incoming_ids.add(f_id)
                feature_obj = existing_by_id.get(f_id) or db.get(ProductFeature, f_id)
                if not feature_obj:
                    continue
                
                # Update title if provided
                if f_title is not None:
                    feature_obj.title = f_title
                
                db.flush()
                
                # Update title translations
                if f_trans_title and isinstance(f_trans_title, dict):
                    AppHelpers.save_translations(db, feature_obj, f_trans_title, ProductFeatureTranslation, "feature_id", name_field="title")
                
                # Update description translations
                if f_trans_desc and isinstance(f_trans_desc, dict):
                    AppHelpers.save_translations(db, feature_obj, f_trans_desc, ProductFeatureTranslation, "feature_id", name_field="description")
            else:
                # Create new feature
                new_feature = ProductFeature(product_id=db_obj.id, title=f_title or "")
                db.add(new_feature)
                db.flush()
                
                # Add title translations if provided
                if f_trans_title and isinstance(f_trans_title, dict):
                    AppHelpers.save_translations(db, new_feature, f_trans_title, ProductFeatureTranslation, "feature_id", name_field="title")
                
                # Add description translations if provided
                if f_trans_desc and isinstance(f_trans_desc, dict):
                    AppHelpers.save_translations(db, new_feature, f_trans_desc, ProductFeatureTranslation, "feature_id", name_field="description")

        # Delete features that are not present in incoming_ids
        for existing in existing_features:
            if existing.id not in incoming_ids:
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

# ==================== NEWS AUTHORS ====================

@fastapi_app.post("/admin/authors", tags=["admin"])
def create_author(data: NewsAuthorCreate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    # Extract fallback name from multilingual dict
    fallback_name = next(iter(data.name.values())) if data.name else ""
    
    # Create author
    author_obj = NewsAuthor(name=fallback_name, image_url=data.image)
    db.add(author_obj)
    db.flush()
    
    # Add translations for name, bio, position
    if data.name and isinstance(data.name, dict):
        AppHelpers.save_translations(db, author_obj, data.name, NewsAuthorTranslation, "author_id", name_field="name")
    
    if data.bio and isinstance(data.bio, dict):
        AppHelpers.save_translations(db, author_obj, data.bio, NewsAuthorTranslation, "author_id", name_field="bio")
    
    if data.position and isinstance(data.position, dict):
        AppHelpers.save_translations(db, author_obj, data.position, NewsAuthorTranslation, "author_id", name_field="position")
    
    db.commit()
    db.refresh(author_obj)
    return AppHelpers.apply_language_filter(author_obj)


@fastapi_app.put("/admin/authors/{id}", tags=["admin"])
def update_author(id: int, data: NewsAuthorUpdate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    author_obj = db.get(NewsAuthor, id)
    if not author_obj:
        raise HTTPException(404, "Author not found")
    
    # Update image if provided
    if data.image:
        author_obj.image_url = data.image
    
    # Update name if provided
    if data.name and isinstance(data.name, dict):
        fallback_name = next(iter(data.name.values())) if data.name else ""
        author_obj.name = fallback_name
        AppHelpers.save_translations(db, author_obj, data.name, NewsAuthorTranslation, "author_id", name_field="name")
    
    # Update bio if provided
    if data.bio and isinstance(data.bio, dict):
        AppHelpers.save_translations(db, author_obj, data.bio, NewsAuthorTranslation, "author_id", name_field="bio")
    
    # Update position if provided
    if data.position and isinstance(data.position, dict):
        AppHelpers.save_translations(db, author_obj, data.position, NewsAuthorTranslation, "author_id", name_field="position")
    
    db.commit()
    db.refresh(author_obj)
    return AppHelpers.apply_language_filter(author_obj)


@fastapi_app.get("/admin/authors/{id}", tags=["admin"])
def get_author(id: int, lang: Optional[str] = None, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    author_obj = db.query(NewsAuthor)\
        .options(joinedload(NewsAuthor.translations))\
        .filter(NewsAuthor.id == id)\
        .first()
    if not author_obj:
        raise HTTPException(404, "Author not found")
    return AppHelpers.apply_language_filter(author_obj, lang)


@fastapi_app.delete("/admin/authors/{id}", tags=["admin"])
def delete_author(id: int, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    author_obj = db.get(NewsAuthor, id)
    if not author_obj:
        raise HTTPException(404, "Author not found")
    db.delete(author_obj)
    db.commit()
    return {"status": "deleted"}

# ==================== NEWS ====================

@fastapi_app.post("/admin/news", tags=["admin"])
def create_news(data: schemas.NewsCreate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    # Extract name/title from multilingual dict (use first available value as fallback)
    fallback_name = ""
    if data.name and isinstance(data.name, dict):
        fallback_name = next(iter(data.name.values())) if data.name else ""
    elif isinstance(data.name, str):
        fallback_name = data.name
    
    # Handle author: Priority is "author" object > "author_id"
    # If "author" object provided: create new author and use it
    # Else if "author_id" provided: use existing author
    # Else: news has no author (author_id is None)
    author_id = None
    
    if data.author:
        # Priority 1: Create new author from provided author object
        author_fallback_name = next(iter(data.author.name.values())) if data.author.name else ""
        author_obj = NewsAuthor(name=author_fallback_name, image_url=data.author.image)
        db.add(author_obj)
        db.flush()
        
        # Add author translations
        if data.author.name and isinstance(data.author.name, dict):
            AppHelpers.save_translations(db, author_obj, data.author.name, NewsAuthorTranslation, "author_id", name_field="name")
        
        if data.author.bio and isinstance(data.author.bio, dict):
            AppHelpers.save_translations(db, author_obj, data.author.bio, NewsAuthorTranslation, "author_id", name_field="bio")
        
        if data.author.position and isinstance(data.author.position, dict):
            AppHelpers.save_translations(db, author_obj, data.author.position, NewsAuthorTranslation, "author_id", name_field="position")
        
        author_id = author_obj.id
    elif data.author_id:
        # Priority 2: Use existing author by ID
        author_id = data.author_id
    
    # 1. Create core News
    news_obj = News(
        title=fallback_name,
        image_url=data.image_url,
        author_id=author_id
    )
    db.add(news_obj)
    db.flush()  # Populate news_obj.id

    # 2. Add Translations for name/title and description
    if data.name and isinstance(data.name, dict):
        AppHelpers.save_translations(db, news_obj, data.name, NewsTranslation, "news_id", name_field="title")
    
    if data.description and isinstance(data.description, dict):
        AppHelpers.save_translations(db, news_obj, data.description, NewsTranslation, "news_id", name_field="description")

    # 3. Add features and their translations
    if data.features:
        for feature_in in data.features:
            f_title = feature_in.get("title") if isinstance(feature_in, dict) else None
            f_description = feature_in.get("description") if isinstance(feature_in, dict) else None
            
            # If title is a dict (multilingual), use first value as fallback
            if isinstance(f_title, dict):
                f_title_fallback = next(iter(f_title.values())) if f_title else ""
                f_title_trans = f_title
            else:
                f_title_fallback = f_title or ""
                f_title_trans = None
            
            # If description is a dict (multilingual), use first value as fallback
            if isinstance(f_description, dict):
                f_description_fallback = next(iter(f_description.values())) if f_description else None
                f_description_trans = f_description
            else:
                f_description_fallback = f_description
                f_description_trans = None
            
            feature_obj = NewsFeatures(news_id=news_obj.id, title=f_title_fallback)
            db.add(feature_obj)
            db.flush()

            # Add title translations
            if f_title_trans and isinstance(f_title_trans, dict):
                AppHelpers.save_translations(db, feature_obj, f_title_trans, NewsFeaturesTranslation, "feature_id", name_field="title")
            
            # Add description translations
            if f_description_trans and isinstance(f_description_trans, dict):
                AppHelpers.save_translations(db, feature_obj, f_description_trans, NewsFeaturesTranslation, "feature_id", name_field="description")

    db.commit()
    db.refresh(news_obj)
    return AppHelpers.apply_language_filter(news_obj)


@fastapi_app.put("/admin/news/{id}", tags=["admin"])
def update_news(id: int, data: schemas.NewsUpdate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    db_obj = db.get(News, id)
    if not db_obj:
        raise HTTPException(404, "Not found")

    # Update scalar fields (excluding multilingual fields and author-related)
    update_data = data.dict(exclude={"name", "description", "features", "author", "author_id"}, exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_obj, key, value)

    # Handle author: Priority is "author" object > "author_id"
    # If "author" object provided: update existing author or create new one
    # Else if "author_id" provided: switch to different author
    # Else: leave author unchanged
    if data.author:
        # Priority 1: Update or create author from provided author object
        if db_obj.author:
            # Update existing author associated with this news
            author_obj = db_obj.author
            if data.author.image:
                author_obj.image_url = data.author.image
            
            if data.author.name and isinstance(data.author.name, dict):
                fallback_name = next(iter(data.author.name.values())) if data.author.name else ""
                author_obj.name = fallback_name
                AppHelpers.save_translations(db, author_obj, data.author.name, NewsAuthorTranslation, "author_id", name_field="name")
            
            if data.author.bio and isinstance(data.author.bio, dict):
                AppHelpers.save_translations(db, author_obj, data.author.bio, NewsAuthorTranslation, "author_id", name_field="bio")
            
            if data.author.position and isinstance(data.author.position, dict):
                AppHelpers.save_translations(db, author_obj, data.author.position, NewsAuthorTranslation, "author_id", name_field="position")
        else:
            # Create new author since news doesn't have one
            author_fallback_name = next(iter(data.author.name.values())) if data.author.name else ""
            author_obj = NewsAuthor(name=author_fallback_name, image_url=data.author.image)
            db.add(author_obj)
            db.flush()
            
            if data.author.name and isinstance(data.author.name, dict):
                AppHelpers.save_translations(db, author_obj, data.author.name, NewsAuthorTranslation, "author_id", name_field="name")
            
            if data.author.bio and isinstance(data.author.bio, dict):
                AppHelpers.save_translations(db, author_obj, data.author.bio, NewsAuthorTranslation, "author_id", name_field="bio")
            
            if data.author.position and isinstance(data.author.position, dict):
                AppHelpers.save_translations(db, author_obj, data.author.position, NewsAuthorTranslation, "author_id", name_field="position")
            
            db_obj.author_id = author_obj.id
    elif data.author_id is not None:
        # Priority 2: Switch to different author by ID
        db_obj.author_id = data.author_id

    # Handle name/title translations: if name dict provided, sync translations for NewsTranslation
    if data.name and isinstance(data.name, dict):
        AppHelpers.save_translations(db, db_obj, data.name, NewsTranslation, "news_id", name_field="title")

    # Handle description translations: if description dict provided, sync translations for NewsTranslation
    if data.description and isinstance(data.description, dict):
        AppHelpers.save_translations(db, db_obj, data.description, NewsTranslation, "news_id", name_field="description")

    # Handle features: create, update, delete
    if data.features is not None:
        incoming = data.features or []

        # Load existing features from DB
        existing_features = db.query(NewsFeatures).filter(NewsFeatures.news_id == db_obj.id).all()
        existing_by_id = {f.id: f for f in existing_features}

        incoming_ids = set()

        for f_in in incoming:
            # accept dict-like format
            f_id = f_in.get("id") if isinstance(f_in, dict) else None
            f_title = f_in.get("title") if isinstance(f_in, dict) else None
            f_description = f_in.get("description") if isinstance(f_in, dict) else None
            f_trans_title = None
            f_trans_desc = None

            # If title is a dict (multilingual), use it as translations for title field
            if isinstance(f_title, dict):
                f_trans_title = f_title
                # Use first language value as fallback title
                f_title = next(iter(f_title.values())) if f_title else None

            # If description is a dict (multilingual), use it as translations for description field
            if isinstance(f_description, dict):
                f_trans_desc = f_description
                # Use first language value as fallback description
                f_description = next(iter(f_description.values())) if f_description else None

            if f_id:
                incoming_ids.add(f_id)
                feature_obj = existing_by_id.get(f_id) or db.get(NewsFeatures, f_id)
                if not feature_obj:
                    continue
                
                # Update title if provided
                if f_title is not None:
                    feature_obj.title = f_title
                
                db.flush()
                
                # Update title translations
                if f_trans_title and isinstance(f_trans_title, dict):
                    AppHelpers.save_translations(db, feature_obj, f_trans_title, NewsFeaturesTranslation, "feature_id", name_field="title")
                
                # Update description translations
                if f_trans_desc and isinstance(f_trans_desc, dict):
                    AppHelpers.save_translations(db, feature_obj, f_trans_desc, NewsFeaturesTranslation, "feature_id", name_field="description")
            else:
                # Create new feature
                new_feature = NewsFeatures(news_id=db_obj.id, title=f_title or "")
                db.add(new_feature)
                db.flush()
                
                # Add title translations if provided
                if f_trans_title and isinstance(f_trans_title, dict):
                    AppHelpers.save_translations(db, new_feature, f_trans_title, NewsFeaturesTranslation, "feature_id", name_field="title")
                
                # Add description translations if provided
                if f_trans_desc and isinstance(f_trans_desc, dict):
                    AppHelpers.save_translations(db, new_feature, f_trans_desc, NewsFeaturesTranslation, "feature_id", name_field="description")

        # Delete features that are not present in incoming_ids
        for existing in existing_features:
            if existing.id not in incoming_ids:
                db.delete(existing)

    # Final commit and refresh
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
        "total_categories": db.query(ProductCategory).count(),
        "total_products": db.query(Product).count(),
        "total_news": db.query(News).count(),
    }



@fastapi_app.get("/")
def root():
    return {"message":"Veterinary Pharmacy API","version":"2.0.0"}

def create_wsgi_app(asgi_app):
    def application(environ, start_response):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0) or 0)
            body = environ["wsgi.input"].read(content_length) if content_length > 0 else b""
            
            scope = {
                "type": "http", 
                "asgi": {"version": "3.0"}, 
                "http_version": "1.1",
                "method": environ["REQUEST_METHOD"], 
                "scheme": environ.get("wsgi.url_scheme", "http"),
                "path": environ.get("PATH_INFO", "/"), 
                "query_string": environ.get("QUERY_STRING", "").encode(),
                "headers": _build_headers(environ),
                "server": (environ.get("SERVER_NAME", "localhost"), int(environ.get("SERVER_PORT", 80))),
            }
            
            response = {"status": 200, "headers": [], "body": []}
            
            async def receive(): 
                return {"type": "http.request", "body": body, "more_body": False}
            
            async def send(message):
                if message["type"] == "http.response.start":
                    response["status"] = message["status"]
                    response["headers"] = message.get("headers", [])
                elif message["type"] == "http.response.body":
                    response["body"].append(message.get("body", b""))
            
            loop.run_until_complete(asgi_app(scope, receive, send))
            
            # Convert headers and ensure CORS headers are present
            headers = []
            cors_headers_added = False
            
            for k, v in response["headers"]:
                key = k.decode() if isinstance(k, bytes) else k
                value = v.decode() if isinstance(v, bytes) else v
                headers.append((key, value))
                if key.lower() == 'access-control-allow-origin':
                    cors_headers_added = True
            
            # If CORS headers weren't added by middleware, add them manually
            # This ensures CORS works even if middleware fails
            if not cors_headers_added:
                origin = environ.get('HTTP_ORIGIN', '')
                if origin:
                    headers.append(('Access-Control-Allow-Origin', origin))
                    headers.append(('Access-Control-Allow-Credentials', 'true'))
                    headers.append(('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'))
                    headers.append(('Access-Control-Allow-Headers', '*'))
            
            start_response(f"{response['status']} {_get_status_phrase(response['status'])}", headers)
            return [b"".join(response["body"])]
            
        except Exception as e:
            # IMPORTANT: Add CORS headers even for error responses
            error_headers = [
                ("Content-Type", "text/plain"),
                ("Access-Control-Allow-Origin", environ.get('HTTP_ORIGIN', '*')),
                ("Access-Control-Allow-Credentials", "true"),
            ]
            start_response("500 Internal Server Error", error_headers)
            return [f"Internal Server Error: {str(e)}".encode()]
        finally: 
            loop.close()
    return application
    
def _build_headers(environ):
    headers = []
    for key, value in environ.items():
        if key.startswith("HTTP_"): headers.append((key[5:].replace("_", "-").lower().encode(), value.encode()))
        elif key in ("CONTENT_TYPE", "CONTENT_LENGTH"): headers.append((key.replace("_", "-").lower().encode(), value.encode()))
    return headers

def _get_status_phrase(code):
    return {200: "OK", 201: "Created", 400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found", 500: "Internal Server Error"}.get(code, "Unknown")


application = create_wsgi_app(fastapi_app)