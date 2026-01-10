import jwt
from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import inspect as sa_inspect
from passlib.context import CryptContext
from datetime import datetime, timedelta

from db import User, LanguageEnum, Base

try:
    from config import Config
except ImportError:
    class Config:
        security = {
            "SECRET_KEY": "replace_me_in_prod",
            "ALGORITHM": "HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES": 525600,
            "pwd_context": CryptContext(schemes=["bcrypt"], deprecated="auto")
        }

class AppHelpers:
    """Helper functions for authentication, database serialization, and i18n"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        return Config.security["pwd_context"].verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password using bcrypt"""
        return Config.security["pwd_context"].hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=Config.security.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, Config.security["SECRET_KEY"], algorithm=Config.security["ALGORITHM"])

    @staticmethod
    def get_user_by_token(db: Session, token: str) -> User:
        """Validate JWT token and return user"""
        try:
            payload = jwt.decode(token, Config.security["SECRET_KEY"], algorithms=[Config.security["ALGORITHM"]])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token")
        except (jwt.DecodeError, jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception):
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user

    @staticmethod
    def save_translations(db: Session, db_obj: Base, translations_dict: dict, ModelClass, fk_field_name: str, name_field: str = "name") -> None:
        """Save multilingual translations to database using sync strategy"""
        if not translations_dict or (isinstance(translations_dict, str) and not translations_dict):
            return
        
        if isinstance(translations_dict, str):
            return
            
        existing_q = db.query(ModelClass).filter(getattr(ModelClass, fk_field_name) == db_obj.id)
        existing = {getattr(t.language, "value", t.language): t for t in existing_q.all()}

        incoming_langs = []

        for lang_code, data in translations_dict.items():
            try:
                language = LanguageEnum(lang_code)
            except ValueError:
                continue

            if isinstance(data, str):
                data_map = {name_field: data}
            elif hasattr(data, "dict") and callable(getattr(data, "dict")):
                data_map = data.dict()
            elif isinstance(data, dict):
                data_map = data
            else:
                try:
                    data_map = dict(data)
                except Exception:
                    data_map = {}

            incoming_langs.append(language.value)

            if language.value in existing:
                trans_obj = existing[language.value]
                for k, v in data_map.items():
                    setattr(trans_obj, k, v)
            else:
                # When creating new translation, preserve existing values from other languages
                # Get any existing translation to copy non-updated fields from
                any_existing = next((t for t in existing.values()), None)
                init_data = {}
                
                # Copy all fields from data_map
                init_data.update(data_map)
                
                # For fields not in data_map, try to get from existing translation
                if any_existing:
                    mapper = sa_inspect(ModelClass)
                    for col in mapper.columns:
                        if col.name not in init_data and col.name not in [fk_field_name, 'language', 'id']:
                            val = getattr(any_existing, col.name, None)
                            if val is not None:
                                init_data[col.name] = val
                
                trans_obj = ModelClass(language=language, **init_data)
                setattr(trans_obj, fk_field_name, db_obj.id)
                db.add(trans_obj)

        for lang_val, trans_obj in existing.items():
            if lang_val not in incoming_langs:
                db.delete(trans_obj)

        db.commit()

    @staticmethod
    def serialize_i18n(translations: List[Any], fields: List[str]) -> Dict[str, Dict[str, str]]:
        """Transform SQLAlchemy translation list into nested dict"""
        if not translations:
            return {f: {lang.value: "" for lang in LanguageEnum} for f in fields}
        
        result = {f: {} for f in fields}
        
        for t in translations:
            lang = t.language.value
            for field in fields:
                val = getattr(t, field, None)
                if val:
                    if field not in result:
                        result[field] = {}
                    result[field][lang] = val
        
        for field in fields:
            for lang in LanguageEnum.__members__.values():
                if lang.value not in result.get(field, {}):
                    if field not in result:
                        result[field] = {}
                    result[field][lang.value] = ""
        
        return result

    @staticmethod
    def apply_language_filter(obj: Base, lang: Optional[str] = None) -> Dict[str, Any]:
        """Smart serialization: returns multilingual or single-language view based on lang parameter"""
        if not obj:
            return {}

        mapper = sa_inspect(obj.__class__)
        data = {c.key: getattr(obj, c.key) for c in mapper.columns}
        
        translations_map = {}
        if hasattr(obj, "translations"):
            for t in obj.translations:
                t_mapper = sa_inspect(t.__class__)
                t_cols = {}
                for c in t_mapper.columns:
                    if c.key not in ["id", "language", "types_id", "category_id", "product_id", "news_id", "feature_id", "author_id"]:
                        t_cols[c.key] = getattr(t, c.key)
                translations_map[t.language.value] = t_cols

        if lang and lang in translations_map:
            data.update(translations_map[lang])
            data["language"] = lang
        else:
            translatable_keys = list(translations_map.values())[0].keys() if translations_map else []
            
            for key in translatable_keys:
                data[key] = {
                    lang_code: translations_map.get(lang_code, {}).get(key, "") 
                    for lang_code in LanguageEnum.__members__.keys()
                }

        if hasattr(obj, "features") and obj.features:
            data["features"] = []
            for f in obj.features:
                f_data = AppHelpers.apply_language_filter(f, lang)
                data["features"].append(f_data)

        if hasattr(obj, "author") and obj.author:
            data["author"] = AppHelpers.apply_language_filter(obj.author, lang)
        
        return data