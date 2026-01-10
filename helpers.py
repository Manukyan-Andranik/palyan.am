import jwt
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import inspect as sa_inspect
from passlib.context import CryptContext
from datetime import datetime, timedelta

from db import User, LanguageEnum, Base

# Mocking config strictly for the helper if not present
try:
    from config import Config
except ImportError:
    class Config:
        security = {
            "SECRET_KEY": "replace_me_in_prod",
            "ALGORITHM": "HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES": 525600,  # 1 year (essentially infinity)
            "pwd_context": CryptContext(schemes=["bcrypt"], deprecated="auto")
        }

class AppHelpers:
    """
    Centralized helper class for Auth, DB Serialization and I18n.
    """

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return Config.security["pwd_context"].verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return Config.security["pwd_context"].hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=Config.security.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, Config.security["SECRET_KEY"], algorithm=Config.security["ALGORITHM"])

    @staticmethod
    def get_user_by_token(db: Session, token: str) -> User:
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
        """
        Generic function to save dictionary based translations to the DB.
        translations_dict can be:
        - {'en': {'name': 'X'}, 'ru': {'name': 'Y'}} (old format)
        - {'en': 'X', 'ru': 'Y'} (new simple format, will use name_field parameter)
        
        name_field: which translation field to update (default 'name', can be 'title', 'description', etc.)
        """
        if not translations_dict or (isinstance(translations_dict, str) and not translations_dict):
            return
        
        # Handle case where a string was passed instead of dict
        if isinstance(translations_dict, str):
            return
            
        # Load existing translations keyed by language value
        existing_q = db.query(ModelClass).filter(getattr(ModelClass, fk_field_name) == db_obj.id)
        existing = {getattr(t.language, "value", t.language): t for t in existing_q.all()}

        incoming_langs = []

        for lang_code, data in translations_dict.items():
            # Validate/normalize language code
            try:
                language = LanguageEnum(lang_code)
            except ValueError:
                # skip invalid language
                continue

            # Normalize data: if string, convert to dict with name_field
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
                # update existing translation
                trans_obj = existing[language.value]
                for k, v in data_map.items():
                    setattr(trans_obj, k, v)
            else:
                # create new translation
                trans_obj = ModelClass(language=language, **data_map)
                setattr(trans_obj, fk_field_name, db_obj.id)
                db.add(trans_obj)

        # Delete translations that are not in incoming set
        for lang_val, trans_obj in existing.items():
            if lang_val not in incoming_langs:
                db.delete(trans_obj)

        db.commit()

    @staticmethod
    def serialize_i18n(translations: List[Any], fields: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Transforms SQLAlchemy translation list into a dict:
        { "name": { "en": "Value", "ru": "Value" } }
        """
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
        
        # Fill missing languages with empty strings
        for field in fields:
            for lang in LanguageEnum.__members__.values():
                if lang.value not in result.get(field, {}):
                    if field not in result:
                        result[field] = {}
                    result[field][lang.value] = ""
        
        return result

    @staticmethod
    def apply_language_filter(obj: Base, lang: Optional[str] = None) -> Dict[str, Any]:
        """
        Smart serialization. 
        If lang is None: Returns object with nested translations {en:..., ru:...}.
        If lang is set: Flattens the object, replacing main fields with the translation of that language.
        """
        if not obj:
            return {}

        # 1. Get base columns excluding relationships
        mapper = sa_inspect(obj.__class__)
        data = {c.key: getattr(obj, c.key) for c in mapper.columns}
        
        # 2. Get Translations
        translations_map = {}
        if hasattr(obj, "translations"):
            for t in obj.translations:
                # Get fields from the translation table, excluding IDs
                t_mapper = sa_inspect(t.__class__)
                t_cols = {}
                for c in t_mapper.columns:
                    if c.key not in ["id", "language", "types_id", "category_id", "product_id", "news_id", "feature_id", "author_id"]:
                        t_cols[c.key] = getattr(t, c.key)
                translations_map[t.language.value] = t_cols

        # 3. Apply Language Filter
        if lang and lang in translations_map:
            # Overwrite base data with specific language data
            data.update(translations_map[lang])
            # Add language field
            data["language"] = lang
        else:
            # Structure for all languages mode
            translatable_keys = list(translations_map.values())[0].keys() if translations_map else []
            
            for key in translatable_keys:
                data[key] = {
                    lang_code: translations_map.get(lang_code, {}).get(key, "") 
                    for lang_code in LanguageEnum.__members__.keys()
                }

        # 4. Handle Nested Relationships
        # Handle Features (Product or News)
        if hasattr(obj, "features") and obj.features:
            data["features"] = []
            for f in obj.features:
                f_data = AppHelpers.apply_language_filter(f, lang)
                data["features"].append(f_data)

        # Handle Author (News)
        if hasattr(obj, "author") and obj.author:
            data["author"] = AppHelpers.apply_language_filter(obj.author, lang)
        
        return data