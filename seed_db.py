#seed_db.py
import random
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Import models from main.py
from db import engine, SessionLocal
from db import (
    Base, User, AnimalTypes, ProductCategory, Product, News,
    AnimalTypesTranslation, ProductCategoryTranslation, ProductTranslation, NewsTranslation,
    ProductSubcategory, ProductSubcategoryTranslation,
    NewsAuthor, NewsAuthorTranslation,
    NewsFeatures, NewsFeaturesTranslation,
    ProductFeature, ProductFeatureTranslation,
    LanguageEnum
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base.metadata.create_all(bind=engine)

def get_password_hash(password):
    return pwd_context.hash(password)

def clear_database(db):
    """Clear all existing data safely in reverse order of dependencies."""
    print("🗑️  Clearing existing data...")

    try:
        # Product features translations -> features -> product translations -> products
        db.query(ProductTranslation).delete(synchronize_session=False)
        db.query(Product).delete(synchronize_session=False)

        # News features translations -> features -> news translations -> news -> authors translations -> authors
        db.query(NewsFeaturesTranslation).delete(synchronize_session=False)
        db.query(NewsFeatures).delete(synchronize_session=False)
        db.query(NewsTranslation).delete(synchronize_session=False)
        db.query(News).delete(synchronize_session=False)
        db.query(NewsAuthorTranslation).delete(synchronize_session=False)
        db.query(NewsAuthor).delete(synchronize_session=False)

        # Animal types translations -> animal types
        db.query(AnimalTypesTranslation).delete(synchronize_session=False)
        db.query(AnimalTypes).delete(synchronize_session=False)

        # Product subcategories translations -> subcategories -> categories translations -> categories
        db.query(ProductSubcategoryTranslation).delete(synchronize_session=False)
        db.query(ProductSubcategory).delete(synchronize_session=False)
        db.query(ProductCategoryTranslation).delete(synchronize_session=False)
        db.query(ProductCategory).delete(synchronize_session=False)


        # Optional: clear users (if needed)
        # db.query(User).delete(synchronize_session=False)

        db.commit()
        print("✅ Database cleared!")

    except Exception as e:
        db.rollback()
        print(f"❌ Failed to clear database: {e}")


def seed_users(db):
    """Create sample users"""
    print("👥 Creating users...")
    
    # Idempotent: only create if not exists
    admin_username = "admin"
    existing = db.query(User).filter_by(username=admin_username).first()
    if existing:
        print("✅ Admin user already exists, skipping creation")
        return existing

    user = User(
        username=admin_username,
        email="admin@palyan.am",
        hashed_password=get_password_hash("admin"),
        is_admin=True
    )
    db.add(user)
    db.commit()
    print("✅ Created admin user")
    print("   - admin / admin (Admin)")
    return user

def seed_animal_types(db):
    """Create sample animal types with translations"""
    print("🐾 Creating animal types with translations...")
    
    types_list = [
        {
            "name": "Dogs",
            "description": "Man's best friend. Dogs are loyal, loving, and make wonderful companions for families and individuals alike.",
            "image_url": "https://images.unsplash.com/photo-1587300003388-59208cc962cb",
            "translations": {
                "ru": {
                    "name": "Собаки",
                    "description": "Лучший друг человека. Собаки верны, любящие и прекрасные компаньоны для семей и отдельных людей."
                },
                "hy": {
                    "name": "Շներ",
                    "description": "Մարդու լավագույն ընկերը: Շները հավատարիմ, սիրող և հիանալի ընկերներ են ընտանիքների և անհատների համար:"
                }
            }
        },
        {
            "name": "Cats",
            "description": "Independent and graceful pets. Cats are perfect for those who want a loving companion with a bit more independence.",
            "image_url": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba",
            "translations": {
                "ru": {
                    "name": "Кошки",
                    "description": "Независимые и грациозные питомцы. Кошки идеальны для тех, кто хочет любящего компаньона с большей независимостью."
                },
                "hy": {
                    "name": "Կատուներ",
                    "description": "Անկախ և նրբագեղ կենդանիներ: Կատուները կատարյալ են նրանց համար, ովքեր ուզում են սիրող ընկեր՝ ավելի շատ անկախությամբ:"
                }
            }
        },
        {
            "name": "Birds",
            "description": "Colorful and melodious companions. Birds bring joy with their songs and beautiful plumage.",
            "image_url": "https://images.unsplash.com/photo-1552728089-57bdde30beb3",
            "translations": {
                "ru": {
                    "name": "Птицы",
                    "description": "Красочные и мелодичные компаньоны. Птицы приносят радость своими песнями и красивым оперением."
                },
                "hy": {
                    "name": "Թռչուններ",
                    "description": "Գունազարդ և մեղեդային ընկերներ: Թռչունները ուրախություն են բերում իրենց երգերով և գեղեցիկ փետուրներով:"
                }
            }
        },
        {
            "name": "Fish",
            "description": "Peaceful aquatic pets. Fish create a calming atmosphere and are perfect for smaller living spaces.",
            "image_url": "https://images.unsplash.com/photo-1520990269312-e4e1bb9e0e01",
            "translations": {
                "ru": {
                    "name": "Рыбы",
                    "description": "Спокойные водные питомцы. Рыбы создают успокаивающую атмосферу и идеальны для небольших жилых помещений."
                },
                "hy": {
                    "name": "Ձկներ",
                    "description": "Խաղաղ ջրային կենդանիներ: Ձկները հանգստացնող մթնոլորտ են ստեղծում և կատարյալ են փոքր բնակելի տարածքների համար:"
                }
            }
        },
        {
            "name": "Rabbits",
            "description": "Gentle and social animals. Rabbits are affectionate pets that love to play and cuddle.",
            "image_url": "https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308",
            "translations": {
                "ru": {
                    "name": "Кролики",
                    "description": "Нежные и социальные животные. Кролики - ласковые питомцы, которые любят играть и обниматься."
                },
                "hy": {
                    "name": "Ճագարներ",
                    "description": "Նուրբ և սոցիալական կենդանիներ: Ճագարները սիրող կենդանիներ են, որոնք սիրում են խաղալ և փայփայվել:"
                }
            }
        },
        {
            "name": "Hamsters",
            "description": "Small and adorable rodents. Hamsters are easy to care for and perfect for children learning responsibility.",
            "image_url": "https://images.unsplash.com/photo-1425082661705-1834bfd09dca",
            "translations": {
                "ru": {
                    "name": "Хомяки",
                    "description": "Маленькие и очаровательные грызуны. Хомяки просты в уходе и идеальны для детей, изучающих ответственность."
                },
                "hy": {
                    "name": "Համստերներ",
                    "description": "Փոքր և սիրուն կրծողներ: Համստերներն հեշտ են խնամքի համար և կատարյալ են երեխաների համար՝ պատասխանատվություն սովորելու համար:"
                }
            }
        },
        {
            "name": "Reptiles",
            "description": "Exotic and fascinating creatures. Reptiles offer a unique pet ownership experience for enthusiasts.",
            "image_url": "https://images.unsplash.com/photo-1531466877279-9c0d35b7b8c0",
            "translations": {
                "ru": {
                    "name": "Рептилии",
                    "description": "Экзотические и захватывающие существа. Рептилии предлагают уникальный опыт владения питомцами для энтузиастов."
                },
                "hy": {
                    "name": "Սողուններ",
                    "description": "Էկզոտիկ և հետաքրքիր արարածներ: Սողունները եզակի փորձ են տալիս կենդանիների սիրահարների համար:"
                }
            }
        },
        {
            "name": "Guinea Pigs",
            "description": "Social and friendly rodents. Guinea pigs are vocal, interactive pets that thrive on companionship.",
            "image_url": "https://images.unsplash.com/photo-1548681528-6a5c45b66b42",
            "translations": {
                "ru": {
                    "name": "Морские свинки",
                    "description": "Социальные и дружелюбные грызуны. Морские свинки - голосистые, интерактивные питомцы, которые процветают в компании."
                },
                "hy": {
                    "name": "Ծովախոզուկներ",
                    "description": "Սոցիալական և բարեկամական կրծողներ: Ծովախոզուկները ձայնային, ինտերակտիվ կենդանիներ են, որոնք հաջողվում են ընկերակցության մեջ:"
                }
            }
        }
    ]
    
    types_objects = []
    for types_data in types_list:
        translations = types_data.pop("translations")
        # AnimalTypes model only accepts name and image_url; description goes into translations
        types_name = types_data.get("name")
        types_image = types_data.get("image_url")
        types = AnimalTypes(name=types_name, image_url=types_image)
        db.add(types)
        db.flush()  # Get the ID
        
        # Add translations
        for lang, trans_data in translations.items():
            translation = AnimalTypesTranslation(
                types_id=types.id,
                language=LanguageEnum(lang),
                name=trans_data.get("name"),
                description=trans_data.get("description")
            )
            db.add(translation)
        
        types_objects.append(types)
    
    db.commit()
    print(f"✅ Created {len(types_list)} animal types with translations")
    return types_objects

def seed_categories(db):
    """Create product categories with subcategories and translations"""
    print("📦 Creating product categories with subcategories and translations...")
    
    categories_list = [
        {
            "name": "Food",
            "translations": {
                "ru": {"name": "Корм"},
                "hy": {"name": "Կեր"},
                "en": {"name": "Food"}
            },
            "subcategories": [
                {"name": "Dry Food", "translations": {"ru": {"name": "Сухой корм"}, "hy": {"name": "Չոր կեր"}, "en": {"name": "Dry Food"}}},
                {"name": "Wet Food", "translations": {"ru": {"name": "Влажный корм"}, "hy": {"name": "Խոնավ կեր"}, "en": {"name": "Wet Food"}}},
                {"name": "Treats", "translations": {"ru": {"name": "Лакомства"}, "hy": {"name": "Մրցանակներ"}, "en": {"name": "Treats"}}}
            ]
        },
        {
            "name": "Toys",
            "translations": {
                "ru": {"name": "Игрушки"},
                "hy": {"name": "Խաղալիքներ"},
                "en": {"name": "Toys"}
            },
            "subcategories": [
                {"name": "Rubber Toys", "translations": {"ru": {"name": "Резиновые игрушки"}, "hy": {"name": "Ռետինե խաղալիքներ"}, "en": {"name": "Rubber Toys"}}},
                {"name": "Interactive Toys", "translations": {"ru": {"name": "Интерактивные игрушки"}, "hy": {"name": "Ինտերակտիվ խաղալիքներ"}, "en": {"name": "Interactive Toys"}}},
                {"name": "Fetch Toys", "translations": {"ru": {"name": "Игрушки для апорта"}, "hy": {"name": "Բերման խաղալիքներ"}, "en": {"name": "Fetch Toys"}}}
            ]
        },
        {
            "name": "Accessories",
            "translations": {
                "ru": {"name": "Аксессуары"},
                "hy": {"name": "Աքսեսուարներ"},
                "en": {"name": "Accessories"}
            },
            "subcategories": [
                {"name": "Collars & Leashes", "translations": {"ru": {"name": "Ошейники и поводки"}, "hy": {"name": "Կոլարներ և վարիչներ"}, "en": {"name": "Collars & Leashes"}}},
                {"name": "Bowls & Feeders", "translations": {"ru": {"name": "Миски и кормушки"}, "hy": {"name": "Սկուտեղներ և կերատարներ"}, "en": {"name": "Bowls & Feeders"}}},
                {"name": "ID Tags", "translations": {"ru": {"name": "Бирки идентификации"}, "hy": {"name": "Նույնականացման պիտակներ"}, "en": {"name": "ID Tags"}}}
            ]
        },
        {
            "name": "Healthcare",
            "translations": {
                "ru": {"name": "Здравоохранение"},
                "hy": {"name": "Առողջապահություն"},
                "en": {"name": "Healthcare"}
            },
            "subcategories": [
                {"name": "Supplements", "translations": {"ru": {"name": "Добавки"}, "hy": {"name": "Հավելումներ"}, "en": {"name": "Supplements"}}},
                {"name": "Vitamins", "translations": {"ru": {"name": "Витамины"}, "hy": {"name": "Վիտամիններ"}, "en": {"name": "Vitamins"}}},
                {"name": "Medications", "translations": {"ru": {"name": "Лекарства"}, "hy": {"name": "Դեղամիջոցներ"}, "en": {"name": "Medications"}}}
            ]
        },
        {
            "name": "Grooming",
            "translations": {
                "ru": {"name": "Груминг"},
                "hy": {"name": "Խնամք"},
                "en": {"name": "Grooming"}
            },
            "subcategories": [
                {"name": "Shampoo & Conditioner", "translations": {"ru": {"name": "Шампунь и кондиционер"}, "hy": {"name": "Շամպուն և կոնդիցիոներ"}, "en": {"name": "Shampoo & Conditioner"}}},
                {"name": "Brushes & Combs", "translations": {"ru": {"name": "Щетки и расчески"}, "hy": {"name": "Խոզանակներ և մազակտաններ"}, "en": {"name": "Brushes & Combs"}}},
                {"name": "Nail Care", "translations": {"ru": {"name": "Уход за когтями"}, "hy": {"name": "Ցուպ խնամք"}, "en": {"name": "Nail Care"}}}
            ]
        },
        {
            "name": "Housing",
            "translations": {
                "ru": {"name": "Жилье"},
                "hy": {"name": "Բնակարան"},
                "en": {"name": "Housing"}
            },
            "subcategories": [
                {"name": "Cages", "translations": {"ru": {"name": "Клетки"}, "hy": {"name": "Վանդակներ"}, "en": {"name": "Cages"}}},
                {"name": "Beds", "translations": {"ru": {"name": "Кровати"}, "hy": {"name": "Անկողիններ"}, "en": {"name": "Beds"}}},
                {"name": "Tanks", "translations": {"ru": {"name": "Аквариумы"}, "hy": {"name": "Ակվարիումներ"}, "en": {"name": "Tanks"}}}
            ]
        },
        {
            "name": "Training",
            "translations": {
                "ru": {"name": "Дрессировка"},
                "hy": {"name": "Վարժեցում"},
                "en": {"name": "Training"}
            },
            "subcategories": [
                {"name": "Training Pads", "translations": {"ru": {"name": "Пеленки для тренировки"}, "hy": {"name": "Վարժեցման փաթ"}, "en": {"name": "Training Pads"}}},
                {"name": "Training Treats", "translations": {"ru": {"name": "Угощения для тренировки"}, "hy": {"name": "Վարժեցման համեղ վտանգ"}, "en": {"name": "Training Treats"}}},
                {"name": "Clickers & Whistles", "translations": {"ru": {"name": "Кликеры и свистки"}, "hy": {"name": "Կլիկերներ և սուլիչներ"}, "en": {"name": "Clickers & Whistles"}}}
            ]
        }
    ]
    
    category_objects = []
    for category_data in categories_list:
        translations = category_data.pop("translations")
        subcats_data = category_data.pop("subcategories", [])
        
        # Create category
        category = ProductCategory(name=category_data.get("name"))
        db.add(category)
        db.flush()
        
        # Add category translations
        for lang, trans_data in translations.items():
            translation = ProductCategoryTranslation(
                category_id=category.id,
                language=LanguageEnum(lang),
                name=trans_data.get("name")
            )
            db.add(translation)
        
        # Add subcategories
        for subcat_data in subcats_data:
            subcat_trans = subcat_data.pop("translations", {})
            subcat = ProductSubcategory(category_id=category.id, name=subcat_data.get("name"))
            db.add(subcat)
            db.flush()
            
            # Add subcategory translations
            for lang, trans_data in subcat_trans.items():
                trans = ProductSubcategoryTranslation(
                    subcategory_id=subcat.id,
                    language=LanguageEnum(lang),
                    name=trans_data.get("name")
                )
                db.add(trans)
        
        category_objects.append(category)
    
    db.commit()
    print(f"✅ Created {len(categories_list)} categories with subcategories")
    return category_objects

def seed_authors(db):
    """Create sample news authors with translations"""
    print("✍️  Creating news authors with translations...")
    
    authors_data = [
        {
            "name": "Dr. Michael Roberts",
            "position": "Veterinary Scientist",
            "bio": "Dr. Roberts has been a veterinary scientist for over 15 years, specializing in canine cognition and behavior. He regularly publishes research on animal intelligence.",
            "image_url": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d",
            "translations": {
                "ru": {
                    "name": "Доктор Майкл Робертс",
                    "position": "Ветеринарный ученый",
                    "bio": "Доктор Робертс работает ветеринарным ученым более 15 лет, специализируясь на когнитивных способностях и поведении собак. Он регулярно публикует исследования по интеллекту животных."
                },
                "hy": {
                    "name": "Դոկտոր Մայքլ Ռոբերտս",
                    "position": "Վետերինար գիտնական",
                    "bio": "Դոկտոր Ռոբերտս ավելի քան 15 տարի է, ինչ վետերինար գիտնական է, մասնագիտանալով շների ճանաչողականությունում և վարքագծում: Նա կանոնավոր կերպով հրապարակում է հետազոտություններ կենդանիների ինտելեկտի վերաբերյալ:"
                }
            }
        },
        {
            "name": "Emily Chen",
            "position": "Feline Behavior Specialist",
            "bio": "Emily has worked with cats for over a decade, helping owners understand and resolve behavioral issues. She runs a popular cat behavior consultation service.",
            "image_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956",
            "translations": {
                "ru": {
                    "name": "Эмили Чен",
                    "position": "Специалист по поведению кошек",
                    "bio": "Эмили работает с кошками более десяти лет, помогая владельцам понимать и решать поведенческие проблемы. Она ведет популярную службу консультаций по поведению кошек."
                },
                "hy": {
                    "name": "Էմիլի Չեն",
                    "position": "Կատուների վարքագծի մասնագետ",
                    "bio": "Էմիլին ավելի քան տասը տարի է աշխատում կատուների հետ՝ օգնելով տերերին հասկանալ և լուծել վարքագծային խնդիրները: Նա վարում է հայտնի կատուների վարքագծի խորհրդատվական ծառայություն:"
                }
            }
        },
        {
            "name": "Dr. James Martinez",
            "position": "Aquatic Life Expert",
            "bio": "With a PhD in Marine Biology, Dr. Martinez has spent 20 years studying aquatic ecosystems and the therapeutic benefits of aquarium keeping.",
            "image_url": "https://images.unsplash.com/photo-1560250097-0b93528c311a",
            "translations": {
                "ru": {
                    "name": "Доктор Джеймс Мартинес",
                    "position": "Эксперт по водной жизни",
                    "bio": "Имея докторскую степень в области морской биологии, доктор Мартинес провел 20 лет, изучая водные экосистемы и терапевтические преимущества содержания аквариумов."
                },
                "hy": {
                    "name": "Դոկտոր Ջեյմս Մարտինես",
                    "position": "Ջրային կյանքի փորձագետ",
                    "bio": "Ծովային կենսաբանության դոկտորի աստիճան ունենալով՝ Դոկտոր Մարտինեսը 20 տարի է ուսումնասիրում է ջրային էկոհամակարգերը և ակվարիումների պահպանության թերապևտիկ առավելությունները:"
                }
            }
        },
        {
            "name": "Rebecca Foster",
            "position": "Avian Specialist",
            "bio": "Rebecca has been working with exotic birds for 12 years. She specializes in avian nutrition and behavioral enrichment for captive birds.",
            "image_url": "https://images.unsplash.com/photo-1494790108755-2616b612b786",
            "translations": {
                "ru": {
                    "name": "Ребекка Фостер",
                    "position": "Специалист по птицам",
                    "bio": "Ребекка работает с экзотическими птицами 12 лет. Она специализируется на питании птиц и поведенческом обогащении для птиц в неволе."
                },
                "hy": {
                    "name": "Ռեբեկա Ֆոսթեր",
                    "position": "Թռչունների մասնագետ",
                    "bio": "Ռեբեկան 12 տարի է աշխատում է էկզոտիկ թռչունների հետ: Նա մասնագիտանում է թռչունների սնուցման և գերության մեջ գտնվող թռչունների վարքագծային հարստացման մեջ:"
                }
            }
        },
        {
            "name": "Amanda Sullivan",
            "position": "Rabbit Behavior Consultant",
            "bio": "Amanda has dedicated her career to understanding rabbit behavior. She helps rescue centers and owners create optimal environments for rabbits.",
            "image_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2",
            "translations": {
                "ru": {
                    "name": "Аманда Салливан",
                    "position": "Консультант по поведению кроликов",
                    "bio": "Аманда посвятила свою карьеру пониманию поведения кроликов. Она помогает приютам и владельцам создавать оптимальные условия для кроликов."
                },
                "hy": {
                    "name": "Ամանդա Սալլիվան",
                    "position": "Ճագարների վարքագծի խորհրդատու",
                    "bio": "Ամանդան նվիրել է իր կարիերան ճագարների վարքագիծը հասկանալուն: Նա օգնում է փրկարարական կենտրոններին և տերերին ստեղծել օպտիմալ միջավայրեր ճագարների համար:"
                }
            }
        },
        {
            "name": "Dr. Nathan Brooks",
            "position": "Herpetologist",
            "bio": "Dr. Brooks is a leading herpetologist with extensive experience in reptile care, conservation, and captive breeding programs.",
            "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
            "translations": {
                "ru": {
                    "name": "Доктор Натан Брукс",
                    "position": "Герпетолог",
                    "bio": "Доктор Брукс - ведущий герпетолог с обширным опытом в уходе за рептилиями, сохранении и программах разведения в неволе."
                },
                "hy": {
                    "name": "Դոկտոր Նեթան Բրուկս",
                    "position": "Հերպետոլոգ",
                    "bio": "Դոկտոր Բրուկսը առաջատար հերպետոլոգ է՝ սողունների խնամքի, պահպանման և գերության մեջ բուծման ծրագրերում լայն փորձառությամբ:"
                }
            }
        },
        {
            "name": "Animal Store Team",
            "position": "Editorial Team",
            "bio": "Our team of pet experts and enthusiasts brings you the latest news, tips, and product information from the world of pet care.",
            "image_url": "https://images.unsplash.com/photo-1551836026-d5c2c7d4b6ac",
            "translations": {
                "ru": {
                    "name": "Команда Animal Store",
                    "position": "Редакционная команда",
                    "bio": "Наша команда экспертов и энтузиастов по домашним животным приносит вам последние новости, советы и информацию о продуктах из мира ухода за домашними животными."
                },
                "hy": {
                    "name": "Animal Store թիմ",
                    "position": "Խմբագրական թիմ",
                    "bio": "Մեր ընտանի կենդանիների փորձագետների և սիրահարների թիմը բերում է ձեզ վերջին նորությունները, խորհուրդները և արտադրանքի տեղեկատվությունը ընտանի կենդանիների խնամքի աշխարհից:"
                }
            }
        }
    ]
    
    author_objects = []
    for author_data in authors_data:
        translations = author_data.pop("translations")
        # NewsAuthor only accepts name and image_url in model
        author = NewsAuthor(name=author_data.get("name"), image_url=author_data.get("image_url"))
        db.add(author)
        db.flush()
        
        # Add translations
        for lang, trans_data in translations.items():
            translation = NewsAuthorTranslation(
                author_id=author.id,
                language=LanguageEnum(lang),
                name=trans_data.get("name"),
                position=trans_data.get("position"),
                bio=trans_data.get("bio")
            )
            db.add(translation)
        
    author_objects.append(author)
    
    db.commit()
    print(f"✅ Created {len(authors_data)} news authors with translations")
    return author_objects

def seed_sample_categories_with_subcategories(db):
    """Insert 3 seed categories and 3 subcategories for each."""
    print("🌱 Seeding 3 categories each with 3 subcategories...")

    seed = [
        {
            "name": "Biopreparations",
            "translations": {
                "hy": {"name": "Բիոպրեպարատներ", "description": "Բիոպրեպարատների նկարագրություն"},
                "ru": {"name": "Биопрепараты", "description": "Описание биопрепаратов"},
                "en": {"name": "Biopreparations", "description": "Biopreparations description"}
            },
            "subcategories": [
                {"name": "Vaccines", "translations": {"hy": {"name": "Պատվաստանյութեր"}, "ru": {"name": "Вакцины"}, "en": {"name": "Vaccines"}}},
                {"name": "Antibiotics", "translations": {"hy": {"name": "Անտիբիոտիկներ"}, "ru": {"name": "Антибиотики"}, "en": {"name": "Antibiotics"}}},
                {"name": "Supplements", "translations": {"hy": {"name": "Ավելացուցիչներ"}, "ru": {"name": "Добавки"}, "en": {"name": "Supplements"}}}
            ]
        },
        {
            "name": "Hygiene",
            "translations": {
                "hy": {"name": "Հիգիենա", "description": "Հիգիենայի նկարագրություն"},
                "ru": {"name": "Гигиена", "description": "Описание гигиены"},
                "en": {"name": "Hygiene", "description": "Hygiene description"}
            },
            "subcategories": [
                {"name": "Shampoos", "translations": {"hy": {"name": "Շամպուններ"}, "ru": {"name": "Шампуни"}, "en": {"name": "Shampoos"}}},
                {"name": "Wipes", "translations": {"hy": {"name": "Ձեռոցիկներ"}, "ru": {"name": "Салфетки"}, "en": {"name": "Wipes"}}},
                {"name": "Sanitizers", "translations": {"hy": {"name": "Անտիսեպտիկներ"}, "ru": {"name": "Антисептики"}, "en": {"name": "Sanitizers"}}}
            ]
        },
        {
            "name": "Feeds",
            "translations": {
                "hy": {"name": "Կերեր", "description": "Կերերի նկարագրություն"},
                "ru": {"name": "Корма", "description": "Описание кормов"},
                "en": {"name": "Feeds", "description": "Feeds description"}
            },
            "subcategories": [
                {"name": "Dry Food", "translations": {"hy": {"name": "Ոչ թաց կեր"}, "ru": {"name": "Сухой корм"}, "en": {"name": "Dry Food"}}},
                {"name": "Wet Food", "translations": {"hy": {"name": "Խոնավ կեր"}, "ru": {"name": "Влажный корм"}, "en": {"name": "Wet Food"}}},
                {"name": "Treats", "translations": {"hy": {"name": "Մրցանակներ"}, "ru": {"name": "Лакомства"}, "en": {"name": "Treats"}}}
            ]
        }
    ]

    created = []
    for c in seed:
        translations = c.get("translations", {})
        subcats = c.get("subcategories", [])
        cat = ProductCategory(name=c["name"]) 
        db.add(cat)
        db.flush()

        # create translations (ProductCategoryTranslation only has 'name')
        for lang, t in translations.items():
            tr = ProductCategoryTranslation(category_id=cat.id, language=LanguageEnum(lang), name=t.get("name"))
            db.add(tr)

        # create subcategories
        for sc in subcats:
            sc_trans = sc.get("translations", {})
            sub = ProductSubcategory(category_id=cat.id, name=sc["name"]) 
            db.add(sub)
            db.flush()
            for lang, st in sc_trans.items():
                s_tr = ProductSubcategoryTranslation(subcategory_id=sub.id, language=LanguageEnum(lang), name=st.get("name"))
                db.add(s_tr)

        created.append(cat)

    db.commit()
    print(f"✅ Seeded {len(created)} categories with subcategories")
    return created

def seed_products(db, types_list, categories):
    """Create sample products with translations and features"""
    print("🛍️  Creating products with translations and features...")
    
    products_data = [
        # Dog Products
        {"name": "Premium Dog Food - Chicken & Rice", "description": "High-quality dry dog food with real chicken and brown rice. Perfect for adult dogs of all breeds.", "price": 45.99, "stock": 150, "types": "Dogs", "category": "Food", "is_new": True, "manufacturer": "PremiumPet Nutrition",
         "translations": {
             "ru": {
                 "name": "Премиум корм для собак - Курица и рис",
                 "description": "Высококачественный сухой корм для собак с настоящей курицей и коричневым рисом. Идеален для взрослых собак всех пород."
             },
             "hy": {
                 "name": "Պրեմիում շների կեր - Հավ և բրինձ",
                 "description": "Բարձրորակ չոր կեր շների համար իրական հավով և շագանակագույն բրինձով: Կատարյալ է բոլոր ցեղատեսակների չափահաս շների համար:"
             }
         },
         "features": [
             {
                 "title": "Complete Nutrition",
                 "description": "Formulated with essential vitamins, minerals, and antioxidants for overall health",
                 "translations": {
                     "ru": {
                         "title": "Полноценное питание",
                         "description": "Формула с необходимыми витаминами, минералами и антиоксидантами для общего здоровья"
                     },
                     "hy": {
                         "title": "Լրիվ սնուցում",
                         "description": "Կազմված է անհրաժեշտ վիտամիններով, հանքանյութերով և հակաօքսիդանտներով ընդհանուր առողջության համար"
                     }
                 }
             },
             {
                 "title": "Digestive Health",
                 "description": "Contains prebiotic fibers and probiotics for optimal digestion",
                 "translations": {
                     "ru": {
                         "title": "Здоровье пищеварения",
                         "description": "Содержит пребиотические волокна и пробиотики для оптимального пищеварения"
                     },
                     "hy": {
                         "title": "Մարսողական առողջություն",
                         "description": "Պարունակում է պրեբիոտիկ մանրաթելեր և պրոբիոտիկներ օպտիմալ մարսողության համար"
                     }
                 }
             },
             {
                 "title": "Coat Health",
                 "description": "Omega-3 fatty acids promote shiny coat and healthy skin",
                 "translations": {
                     "ru": {
                         "title": "Здоровье шерсти",
                         "description": "Омега-3 жирные кислоты способствуют блестящей шерсти и здоровой коже"
                     },
                     "hy": {
                         "title": "Դիմակի առողջություն",
                         "description": "Օմեգա-3 ճարպաթթուներն խթանում են փայլուն դիմակ և առողջ մաշկ"
                     }
                 }
             }
         ]},
        {"name": "Interactive Dog Toy Ball", "description": "Durable rubber ball that bounces unpredictably to keep your dog entertained for hours.", "price": 12.99, "stock": 200, "types": "Dogs", "category": "Toys", "is_new": False, "manufacturer": "PlaySafe Toys",
         "translations": {
             "ru": {
                 "name": "Интерактивный мяч для собак",
                 "description": "Прочный резиновый мяч, который непредсказуемо подпрыгивает, развлекая вашу собаку часами."
             },
             "hy": {
                 "name": "Ինտերակտիվ գնդակ շների համար",
                 "description": "Ամուր ռետինե գնդակ, որը անկանխատեսելի է ցատկում՝ ձեր շանը ժամերով զվարճացնելու համար:"
             }
         },
         "features": [
             {
                 "title": "Durable Construction",
                 "description": "Made from high-grade, non-toxic rubber that withstands heavy chewing",
                 "translations": {
                     "ru": {
                         "title": "Прочная конструкция",
                         "description": "Изготовлен из высококачественной нетоксичной резины, выдерживающей сильное жевание"
                     },
                     "hy": {
                         "title": "Դիմացկուն կառուցվածք",
                         "description": "Պատրաստված է բարձրորակ, ոչ թունավոր ռետինից, որն դիմակայում է ծանր ծամելուն"
                     }
                 }
             },
             {
                 "title": "Unpredictable Bounce",
                 "description": "Erratic movement pattern keeps dogs engaged and interested",
                 "translations": {
                     "ru": {
                         "title": "Непредсказуемый отскок",
                         "description": "Непостоянный характер движения удерживает собак вовлеченными и заинтересованными"
                     },
                     "hy": {
                         "title": "Անկանխատեսելի ցատկ",
                         "description": "Անկանխատեսելի շարժման օրինաչափությունը շներին պահում է ներգրավված և հետաքրքրված"
                     }
                 }
             }
         ]},
        
        # Cat Products
        {"name": "Gourmet Cat Food - Salmon Feast", "description": "Premium wet cat food made with real salmon. Rich in protein and omega-3.", "price": 29.99, "stock": 120, "types": "Cats", "category": "Food", "is_new": False, "manufacturer": "Feline Gourmet",
         "translations": {
             "ru": {
                 "name": "Гурман корм для кошек - Лосось",
                 "description": "Премиум влажный корм для кошек из настоящего лосося. Богат белком и омега-3."
             },
             "hy": {
                 "name": "Գուրման կատուների կեր - Սաղմոն",
                 "description": "Պրեմիում թաց կեր կատուների համար իրական սաղմոնով: Հարուստ է սպիտակուցով և օմեգա-3-ով:"
             }
         },
         "features": [
             {
                 "title": "Real Salmon",
                 "description": "Made with 100% real salmon as the primary ingredient",
                 "translations": {
                     "ru": {
                         "title": "Настоящий лосось",
                         "description": "Изготовлен из 100% настоящего лосося в качестве основного ингредиента"
                     },
                     "hy": {
                         "title": "Իրական սաղմոն",
                         "description": "Պատրաստված է 100% իրական սաղմոնով որպես հիմնական բաղադրիչ"
                     }
                 }
             },
             {
                 "title": "Grain-Free",
                 "description": "No wheat, corn, or soy for cats with sensitive stomachs",
                 "translations": {
                     "ru": {
                         "title": "Без зерна",
                         "description": "Без пшеницы, кукурузы или сои для кошек с чувствительным желудком"
                     },
                     "hy": {
                         "title": "Հացահատիկազերծ",
                         "description": "Ոչ մի ցորեն, եգիպտացորեն կամ սոյա զգայուն ստամոքս ունեցող կատուների համար"
                     }
                 }
             }
         ]},
        
        # Bird Products
        {"name": "Premium Bird Seed Mix", "description": "Nutritious blend of seeds, nuts, and dried fruits for all bird types.", "price": 18.99, "stock": 100, "types": "Birds", "category": "Food", "is_new": False, "manufacturer": "Avian Delight",
         "translations": {
             "ru": {
                 "name": "Премиум смесь семян для птиц",
                 "description": "Питательная смесь семян, орехов и сушеных фруктов для всех видов птиц."
             },
             "hy": {
                 "name": "Պրեմիում սերմերի խառնուրդ թռչունների համար",
                 "description": "Սննդարար սերմերի, ընկույզների և չորացրած մրգերի խառնուրդ բոլոր տեսակի թռչունների համար:"
             }
         },
         "features": [
             {
                 "title": "Balanced Nutrition",
                 "description": "Carefully balanced for optimal health and vibrant plumage",
                 "translations": {
                     "ru": {
                         "title": "Сбалансированное питание",
                         "description": "Тщательно сбалансировано для оптимального здоровья и яркого оперения"
                     },
                     "hy": {
                         "title": "Հավասարակշռված սնուցում",
                         "description": "Ուշադրությամբ հավասարակշռված է օպտիմալ առողջության և վառ փետուրների համար"
                     }
                 }
             }
         ]},
        
        # Fish Products
        {"name": "Tropical Fish Flakes", "description": "Complete nutrition for all tropical fish. Enhances colors naturally.", "price": 13.99, "stock": 200, "types": "Fish", "category": "Food", "is_new": False, "manufacturer": "Aqua Life",
         "translations": {
             "ru": {
                 "name": "Хлопья для тропических рыб",
                 "description": "Полноценное питание для всех тропических рыб. Естественно улучшает цвета."
             },
             "hy": {
                 "name": "Թաթիկներ արևադարձային ձկների համար",
                 "description": "Ամբողջական սնուցում բոլոր արևադարձային ձկների համար: Բնականորեն բարելավում է գույները:"
             }
         },
         "features": [
             {
                 "title": "Color Enhancement",
                 "description": "Natural carotenoids enhance red, orange, and yellow pigments",
                 "translations": {
                     "ru": {
                         "title": "Улучшение цвета",
                         "description": "Натуральные каротиноиды усиливают красные, оранжевые и желтые пигменты"
                     },
                     "hy": {
                         "title": "Գույնի բարելավում",
                         "description": "Բնական կարոտինոիդներն ուժեղացնում են կարմիր, նարնջագույն և դեղին գունանյութերը"
                     }
                 }
             }
         ]}
    ]
    
    # Create types and category lookup dictionaries
    types_dict = {s.name: s for s in types_list}
    category_dict = {c.name: c for c in categories}
    
    product_objects = []
    for product_data in products_data:
        translations = product_data.pop("translations", {})
        features = product_data.pop("features", [])
        types_name = product_data.pop("types")
        category_name = product_data.pop("category")
        
        # Only keep valid Product fields here
        product = Product(
            name=product_data.get("name"),
            price=product_data.get("price"),
            stock=product_data.get("stock", 0),
            manufacturer=product_data.get("manufacturer"),
            image_url=product_data.get("image_url") or f"https://images.unsplash.com/photo-{random.randint(1500000000000, 1700000000000)}",
            is_new=product_data.get("is_new", False),
            types_id=types_dict[types_name].id,
            category_id=category_dict[category_name].id
        )
        db.add(product)
        db.flush()
        
        # Add translations
        for lang, trans_data in translations.items():
            translation = ProductTranslation(
                product_id=product.id,
                language=LanguageEnum(lang),
                name=trans_data.get("name"),
                description=trans_data.get("description")
            )
            db.add(translation)
        
        # Add features
        for feature_data in features:
            feature_translations = feature_data.pop("translations", {})
            feature = ProductFeature(
                product_id=product.id,
                title=feature_data.get("title")
            )
            db.add(feature)
            db.flush()
            
            # Add feature translations
            for lang, trans_data in feature_translations.items():
                feature_translation = ProductFeatureTranslation(
                    feature_id=feature.id,
                    language=LanguageEnum(lang),
                    title=trans_data.get("title"),
                    description=trans_data.get("description")
                )
                db.add(feature_translation)
        
        product_objects.append(product)
    
    db.commit()
    print(f"✅ Created {len(products_data)} products with translations and features")
    return product_objects

def seed_news(db, authors):
    """Create sample news articles with translations and features"""
    print("📰 Creating news articles with translations and features...")
    
    # Create author lookup dictionary
    author_dict = {}
    for author in authors:
        author_dict[author.name] = author.id
    
    news_data = [
        {
            "title": "New Study Reveals Dogs Can Understand Up to 250 Words",
            "summary": "Recent research shows that dogs have impressive cognitive abilities and can learn vocabulary comparable to a 2-year-old child.",
            "content": """A groundbreaking study published in the Journal of Animal Cognition has revealed that dogs possess remarkable language comprehension abilities. Researchers at the Canine Cognition Center found that the average dog can understand up to 250 words and gestures, with some highly intelligent breeds capable of learning even more.

The study, which spanned three years and involved over 500 dogs of various breeds, utilized advanced behavioral testing and cognitive assessments. Border Collies, Poodles, and German Shepherds demonstrated the highest levels of word comprehension.

Dr. Sarah Johnson, lead researcher, stated: "We've long known that dogs are intelligent, but this study quantifies just how sophisticated their understanding of human language can be. It's comparable to the vocabulary of a two-year-old child."

The research also explored how dogs process commands and emotional tones, finding that they respond not just to words but to the emotional context in which they're spoken. This has significant implications for dog training and human-animal communication.""",
            "author": "Dr. Michael Roberts",
            "image_url": "https://images.unsplash.com/photo-1560807707-8cc77767d783",
            "published_at": datetime.now() - timedelta(days=2),
            "translations": {
                "ru": {
                    "title": "Новое исследование показывает, что собаки могут понимать до 250 слов",
                    "summary": "Недавние исследования показывают, что собаки обладают впечатляющими когнитивными способностями и могут выучить словарный запас, сравнимый с 2-летним ребенком.",
                    "content": """Новаторское исследование, опубликованное в журнале Journal of Animal Cognition, показало, что собаки обладают замечательными способностями к пониманию языка. Исследователи из Canine Cognition Center обнаружили, что средняя собака может понимать до 250 слов и жестов, а некоторые высокоинтеллектуальные породы способны выучить еще больше.

Исследование, которое длилось три года и охватило более 500 собак различных пород, использовало передовое поведенческое тестирование и когнитивные оценки. Бордер-колли, пудели и немецкие овчарки продемонстрировали самые высокие уровни понимания слов.

Доктор Сара Джонсон, ведущий исследователь, заявила: "Мы давно знали, что собаки умны, но это исследование количественно оценивает, насколько сложным может быть их понимание человеческого языка. Это сопоставимо со словарным запасом двухлетнего ребенка".

Исследование также изучило, как собаки обрабатывают команды и эмоциональные тона, обнаружив, что они реагируют не только на слова, но и на эмоциональный контекст, в котором они произносятся. Это имеет значительные последствия для дрессировки собак и общения человека с животными."""
                },
                "hy": {
                    "title": "Նոր ուսումնասիրությունը բացահայտում է, որ շները կարող են հասկանալ մինչև 250 բառ",
                    "summary": "Վերջին հետազոտությունը ցույց է տալիս, որ շները ունեն տպավորիչ ճանաչողական ունակություններ և կարող են սովորել բառապաշար, որը համեմատելի է 2 տարեկան երեխայի հետ:",
                    "content": """Journal of Animal Cognition ամսագրում հրապարակված հեղափոխական ուսումնասիրությունը բացահայտել է, որ շները ունեն ուշագրավ լեզվի հասկացողության ունակություններ: Canine Cognition Center-ի հետազոտողները հայտնաբերել են, որ միջին շունը կարող է հասկանալ մինչև 250 բառ և ժեստ, իսկ որոշ բարձր ինտելեկտով ցեղատեսակներ կարող են սովորել նույնիսկ ավելի շատ:

Երեք տարի տևած և տարբեր ցեղատեսակների ավելի քան 500 շներ ներառող ուսումնասիրությունը օգտագործել է առաջադեմ վարքագծային թեստավորում և ճանաչողական գնահատում: Բորդեր կոլիները, պուդելները և գերմանական հովիվները ցուցադրել են բառերի հասկացողության ամենաբարձր մակարդակները:

Առաջատար հետազոտող Դոկտոր Սառա Ջոնսոնը հայտարարել է. «Մենք վաղուց գիտենք, որ շները խելացի են, բայց այս ուսումնասիրությունը քանակապես գնահատում է, թե որքան բարդ կարող է լինել նրանց մարդկային լեզվի հասկացողությունը: Դա համեմատելի է երկու տարեկան երեխայի բառապաշարի հետ»:

Հետազոտությունը նաև ուսումնասիրել է, թե ինչպես են շները մշակում հրամաններն ու զգացմունքային երանգները, և հայտնաբերել, որ նրանք արձագանքում են ոչ միայն բառերին, այլ նաև այն զգացմունքային համատեքստին, որում դրանք արտասանվում են: Սա կարևոր հետևանքներ ունի շների վարժեցման և մարդկանց ու կենդանիների հաղորդակցության համար:"""
                }
            },
            "features": [
                {
                    "title": "Study Duration",
                    "description": "Three-year comprehensive study involving multiple research institutions",
                    "translations": {
                        "ru": {
                            "title": "Продолжительность исследования",
                            "description": "Трехлетнее комплексное исследование с участием нескольких научных учреждений"
                        },
                        "hy": {
                            "title": "Ուսումնասիրության տևողությունը",
                            "description": "Երեք տարվա համապարփակ ուսումնասիրություն՝ ներառելով բազմաթիվ հետազոտական հաստատություններ"
                        }
                    }
                },
                {
                    "title": "Key Findings",
                    "description": "Border Collies demonstrated highest vocabulary retention at 300+ words",
                    "translations": {
                        "ru": {
                            "title": "Ключевые выводы",
                            "description": "Бордер-колли продемонстрировали наивысшее сохранение словарного запаса - более 300 слов"
                        },
                        "hy": {
                            "title": "Հիմնական հայտնաբերումները",
                            "description": "Բորդեր կոլիները ցուցադրել են ամենաբարձր բառապաշարի պահպանում՝ 300+ բառ"
                        }
                    }
                }
            ]
        },
        {
            "title": "Top 10 Tips for First-Time Cat Owners",
            "summary": "Bringing home your first cat? Here's everything you need to know to ensure a smooth transition for both you and your new feline friend.",
            "content": """Adopting your first cat is an exciting journey, but it can also be overwhelming. Here are ten essential tips to help you and your new feline companion start off on the right paw:

1. Create a Safe Space: Set up a quiet room where your cat can adjust to their new environment without feeling overwhelmed.

2. Litter Box Basics: Place the litter box in a quiet, accessible location and scoop daily.

3. Proper Nutrition: Choose high-quality cat food appropriate for your cat's age and health needs.

4. Regular Vet Visits: Schedule a check-up within the first week and keep up with vaccinations.

5. Interactive Play: Dedicate time each day for play to build bonds and provide exercise.

6. Scratching Solutions: Provide multiple scratching posts to save your furniture.

7. Patience is Key: Give your cat time to adjust - it may take weeks or months for them to fully settle in.

8. Cat-Proof Your Home: Remove toxic plants and secure dangerous items before your cat arrives.

9. Grooming Routine: Start brushing early to make it a positive experience.

10. Love and Respect: Learn to read your cat's body language and respect their boundaries.

Remember, every cat is unique, and what works for one may not work for another. The key is patience, observation, and lots of love.""",
            "author": "Emily Chen",
            "image_url": "https://images.unsplash.com/photo-1573865526739-10c1d3a55e86",
            "published_at": datetime.now() - timedelta(days=5),
            "translations": {
                "ru": {
                    "title": "Топ-10 советов для новых владельцев кошек",
                    "summary": "Приводите домой свою первую кошку? Вот все, что вам нужно знать, чтобы обеспечить плавный переход как для вас, так и для вашего нового кошачьего друга.",
                    "content": """Усыновление вашей первой кошки - это захватывающее путешествие, но оно также может быть ошеломляющим. Вот десять важных советов, которые помогут вам и вашему новому кошачьему компаньону начать с правильной лапы:

1. Создайте безопасное пространство: организуйте тихую комнату, где ваша кошка сможет привыкнуть к новой обстановке, не чувствуя себя перегруженной.

2. Основы лотка: поместите лоток в тихом, доступном месте и убирайте его ежедневно.

3. Правильное питание: выберите высококачественный корм для кошек, соответствующий возрасту и потребностям вашей кошки в здоровье.

4. Регулярные визиты к ветеринару: назначьте проверку в течение первой недели и соблюдайте график вакцинации.

5. Интерактивная игра: посвящайте время каждый день игре, чтобы строить связи и обеспечивать физические нагрузки.

6. Решения для царапания: предоставьте несколько когтеточек, чтобы спасти вашу мебель.

7. Терпение - ключ: дайте кошке время адаптироваться - может потребоваться недели или месяцы, чтобы она полностью освоилась.

8. Защитите дом от кошки: удалите токсичные растения и закрепите опасные предметы до прибытия кошки.

9. Режим груминга: начните расчесывать рано, чтобы сделать это позитивным опытом.

10. Любовь и уважение: научитесь читать язык тела вашей кошки и уважайте ее границы.

Помните, каждая кошка уникальна, и то, что работает для одной, может не работать для другой. Ключ - терпение, наблюдение и много любви."""
                },
                "hy": {
                    "title": "Լավագույն 10 խորհուրդներ առաջին անգամ կատու ունեցողների համար",
                    "summary": "Տուն եք բերում ձեր առաջին կատուն: Ահա այն ամենը, ինչ դուք պետք է իմանաք, որպեսզի ապահովեք հարթ անցում և՛ ձեզ, և՛ ձեր նոր կատվի ընկերոջ համար:",
                    "content": """Ձեր առաջին կատվին որդեգրելը հետաքրքիր ճանապարհորդություն է, բայց այն կարող է նաև ճնշող լինել: Ահա տասը էական խորհուրդներ, որոնք կօգնեն ձեզ և ձեր նոր կատվի ընկերոջը սկսել ճիշտ թաթով.

1. Ստեղծեք անվտանգ տարածք. կազմակերպեք հանգիստ սենյակ, որտեղ ձեր կատուն կկարողանա հարմարվել նոր միջավայրին՝ առանց զգալու գերբեռնվածություն:

2. Ծղոտի տուփի հիմունքները. տեղադրեք ծղոտի տուփը հանգիստ, հասանելի վայրում և մաքրեք այն ամեն օր:

3. Ճիշտ սնուցում. ընտրեք բարձրորակ կատվի կեր, որը համապատասխանում է ձեր կատվի տարիքին և առողջության կարիքներին:

4. Կանոնավոր այցեր անասնաբույժի մոտ. նշանակեք ստուգում առաջին շաբաթվա ընթացքում և պահպանեք պատվաստման գրաֆիկը:

5. Ինտերակտիվ խաղ. ամեն օր ժամանակ հատկացրեք խաղի համար՝ կապեր ստեղծելու և ֆիզիկական վարժություններ ապահովելու համար:

6. Քերծման լուծումներ. տրամադրեք մի քանի քերծման սյուներ՝ ձեր կահույքը փրկելու համար:

7. Համբերությունը բանալին է. տվեք կատվին ժամանակ հարմարվելու - կարող է պահանջվել շաբաթներ կամ ամիսներ, որպեսզի այն լիովին հարմարվի:

8. Կատվի համար ապահովեք ձեր տունը. հեռացրեք թունավոր բույսերը և ապահովեք վտանգավոր իրերը մինչև կատվի ժամանումը:

9. Խնամքի ռեժիմ. սկսեք շուտ սանրել՝ դա դարձնելու դրական փորձ:

10. Սեր և հարգանք. սովորեք կարդալ ձեր կատվի մարմնի լեզուն և հարգեք նրա սահմանները:

Հիշեք, որ յուրաքանչյուր կատու եզակի է, և այն, ինչ աշխատում է մեկի համար, կարող է չաշխատել մյուսի համար: Բանալին հանդուրժողականությունն է, դիտարկումը և շատ սերը:"""
                }
            },
            "features": [
                {
                    "title": "Essential Supplies",
                    "description": "Litter box, scratching post, carrier, food/water bowls, toys",
                    "translations": {
                        "ru": {
                            "title": "Необходимые принадлежности",
                            "description": "Лоток, когтеточка, переноска, миски для еды/воды, игрушки"
                        },
                        "hy": {
                            "title": "Անհրաժեշտ պարագաներ",
                            "description": "Ծղոտի տուփ, քերծման սյուն, փոխադրիչ, կերակրի/ջրի ամաններ, խաղալիքներ"
                        }
                    }
                },
                {
                    "title": "Emergency Preparedness",
                    "description": "Keep emergency vet contact and know signs of common feline illnesses",
                    "translations": {
                        "ru": {
                            "title": "Готовность к чрезвычайным ситуациям",
                            "description": "Храните контакт ветеринара для экстренных случаев и знайте признаки распространенных кошачьих заболеваний"
                        },
                        "hy": {
                            "title": "Վթարային պատրաստվածություն",
                            "description": "Պահպանեք արտակարգ դեպքերի համար անասնաբույժի կոնտակտը և իմացեք սովորական կատվային հիվանդությունների նշանները"
                        }
                    }
                }
            ]
        }
    ]
    
    news_objects = []
    for news_item in news_data:
        translations = news_item.pop("translations", {})
        features = news_item.pop("features", [])
        author_name = news_item.pop("author")
        # News model accepts title, image_url, author_id, published_at
        _summary = news_item.pop("summary", None)
        _content = news_item.pop("content", None)
        news = News(
            title=news_item.get("title"),
            image_url=news_item.get("image_url"),
            published_at=news_item.get("published_at"),
            author_id=author_dict.get(author_name)
        )
        db.add(news)
        db.flush()
        
        # Add translations
        for lang, trans_data in translations.items():
            translation = NewsTranslation(
                news_id=news.id,
                language=LanguageEnum(lang),
                title=trans_data.get("title"),
                description=trans_data.get("summary") or trans_data.get("content")
            )
            db.add(translation)
        
        # Add features
        for feature_data in features:
            feature_translations = feature_data.pop("translations", {})
            feature = NewsFeatures(
                news_id=news.id,
                title=feature_data.get("title")
            )
            db.add(feature)
            db.flush()
            
            # Add feature translations
            for lang, trans_data in feature_translations.items():
                feature_translation = NewsFeaturesTranslation(
                    feature_id=feature.id,
                    language=LanguageEnum(lang),
                    title=trans_data.get("title"),
                    description=trans_data.get("description")
                )
                db.add(feature_translation)
        
        news_objects.append(news)
    
    db.commit()
    print(f"✅ Created {len(news_data)} news articles with translations and features")
    return news_objects

def main():
    """Main function to seed the database"""
    print("\n" + "="*60)
    print("🌱 ANIMAL STORE DATABASE SEEDER")
    print("="*60 + "\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Clear existing data
        clear_database(db)
        
        # Seed data in order
        seed_users(db)
        print("✅ Users created")

        types = seed_animal_types(db)
        print()

        categories = seed_categories(db)
        print()

        authors = seed_authors(db)
        print()

        products = seed_products(db, types, categories)
        print()

        news = seed_news(db, authors)
        print()
        
        # print("="*60)
        # print("✨ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        # print("="*60)
        # print("\n📊 Summary:")
        # print(f"   • Users: {db.query(User).count()}")
        # print(f"   • Animal Species: {db.query(AnimalTypes).count()}")
        # print(f"   • Categories: {db.query(ProductCategory).count()}")
        # print(f"   • Authors: {db.query(NewsAuthor).count()}")
        # print(f"   • Products: {db.query(Product).count()}")
        # print(f"   • Product Features: {db.query(ProductFeatures).count()}")
        # print(f"   • News Articles: {db.query(News).count()}")
        # print(f"   • News Features: {db.query(NewsFeatures).count()}")
        # print("\n🔐 Login Credentials:")
        # print("   Admin: admin / admin123")
        # print("   User: john_doe / password123")
        # print("\n🚀 You can now start the server with: python main.py")
        # print("   API Documentation: http://localhost:8000/docs\n")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()