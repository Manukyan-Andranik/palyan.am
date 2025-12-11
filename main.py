import jwt
from sqlalchemy.orm import Session
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials

from db import (
    User, UserCreate, UserResponse,
    AnimalSpecies, AnimalSpeciesCreate, AnimalSpeciesResponse,
    ProductCategory, ProductCategoryCreate, ProductCategoryResponse,
    Product, ProductCreate, ProductUpdate, ProductResponse,
    News, NewsCreate, NewsUpdate, NewsResponse,
    Token, SessionLocal
)

from config import Config

# ==================== FASTAPI APP ====================
app = FastAPI(
    title="Animal Store API",
    version="1.0.0",
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
    return Config.security["pwd_context"].hash(password)

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
def get_home_data(db: Session = Depends(get_db)):
    species = db.query(AnimalSpecies).all()
    news = db.query(News).order_by(News.published_at.desc()).limit(6).all()
    new_products = db.query(Product).filter(Product.is_new == True).limit(8).all()
    
    return {
        "animal_species": species,
        "latest_news": news,
        "new_products": new_products
    }

# ==================== ANIMAL SPECIES ENDPOINTS ====================
@app.get("/api/species", response_model=List[AnimalSpeciesResponse], tags=["public"])
def get_all_species(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(AnimalSpecies).offset(skip).limit(limit).all()

@app.get("/api/species/{species_id}", response_model=AnimalSpeciesResponse, tags=["public"])
def get_species_by_id(species_id: int, db: Session = Depends(get_db)):
    species = db.query(AnimalSpecies).filter(AnimalSpecies.id == species_id).first()
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    return species

@app.post("/api/admin/species", response_model=AnimalSpeciesResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def create_species(species: AnimalSpeciesCreate, db: Session = Depends(get_db)):
    db_species = AnimalSpecies(**species.dict())
    db.add(db_species)
    db.commit()
    db.refresh(db_species)
    return db_species

@app.put("/api/admin/species/{species_id}", response_model=AnimalSpeciesResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def update_species(species_id: int, species: AnimalSpeciesCreate, db: Session = Depends(get_db)):
    db_species = db.query(AnimalSpecies).filter(AnimalSpecies.id == species_id).first()
    if not db_species:
        raise HTTPException(status_code=404, detail="Species not found")
    for key, value in species.dict().items():
        setattr(db_species, key, value)
    db.commit()
    db.refresh(db_species)
    return db_species

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
def get_all_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ProductCategory).offset(skip).limit(limit).all()

@app.post("/api/admin/categories", response_model=ProductCategoryResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def create_category(category: ProductCategoryCreate, db: Session = Depends(get_db)):
    db_category = ProductCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.put("/api/admin/categories/{category_id}", response_model=ProductCategoryResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def update_category(category_id: int, category: ProductCategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(ProductCategory).filter(ProductCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in category.dict().items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category

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
    db: Session = Depends(get_db)
):
    query = db.query(Product)
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
    return query.offset(skip).limit(limit).all()

@app.get("/api/products/new", response_model=List[ProductResponse], tags=["public"])
def get_new_products(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.is_new == True).offset(skip).limit(limit).all()

@app.get("/api/products/{product_id}", response_model=ProductResponse, tags=["public"])
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/api/admin/products", response_model=ProductResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.put("/api/admin/products/{product_id}", response_model=ProductResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

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
def get_all_news(skip: int = 0, limit: int = 100, search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(News).order_by(News.published_at.desc())
    if search:
        query = query.filter(News.title.contains(search) | News.content.contains(search))
    return query.offset(skip).limit(limit).all()

@app.get("/api/news/{news_id}", response_model=NewsResponse, tags=["public"])
def get_news_by_id(news_id: int, db: Session = Depends(get_db)):
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news

@app.post("/api/admin/news", response_model=NewsResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def create_news(news: NewsCreate, db: Session = Depends(get_db)):
    db_news = News(**news.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

@app.put("/api/admin/news/{news_id}", response_model=NewsResponse, tags=["admin"], dependencies=[Depends(get_admin_user)])
def update_news(news_id: int, news: NewsUpdate, db: Session = Depends(get_db)):
    db_news = db.query(News).filter(News.id == news_id).first()
    if not db_news:
        raise HTTPException(status_code=404, detail="News not found")
    for key, value in news.dict(exclude_unset=True).items():
        setattr(db_news, key, value)
    db.commit()
    db.refresh(db_news)
    return db_news

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
    return {"message": "Animal Store API", "version": "1.0.0", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
