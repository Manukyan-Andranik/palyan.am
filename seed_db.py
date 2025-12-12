import random
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Import models from main.py
from db import engine, SessionLocal
from db import (
    Base, User, AnimalSpecies, ProductCategory, Product, News,
    AnimalSpeciesTranslation, ProductCategoryTranslation, ProductTranslation, NewsTranslation,
    LanguageEnum
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base.metadata.create_all(bind=engine)

def get_password_hash(password):
    return pwd_context.hash(password)

def clear_database(db):
    """Clear all existing data"""
    print("🗑️  Clearing existing data...")
    db.query(ProductTranslation).delete()
    db.query(Product).delete()
    db.query(NewsTranslation).delete()
    db.query(News).delete()
    db.query(AnimalSpeciesTranslation).delete()
    db.query(AnimalSpecies).delete()
    db.query(ProductCategoryTranslation).delete()
    db.query(ProductCategory).delete()
    db.query(User).delete()
    db.commit()
    print("✅ Database cleared!")

def seed_users(db):
    """Create sample users"""
    print("👥 Creating users...")
    
    users = [
        User(
            username="admin",
            email="admin@animalstore.com",
            hashed_password=get_password_hash("admin123"),
            is_admin=True
        ),
        User(
            username="john_doe",
            email="john@example.com",
            hashed_password=get_password_hash("password123"),
            is_admin=False
        ),
        User(
            username="jane_smith",
            email="jane@example.com",
            hashed_password=get_password_hash("password123"),
            is_admin=False
        )
    ]
    
    for user in users:
        db.add(user)
    
    db.commit()
    print(f"✅ Created {len(users)} users")
    print("   - admin / admin123 (Admin)")
    print("   - john_doe / password123")
    print("   - jane_smith / password123")

def seed_animal_species(db):
    """Create sample animal species with translations"""
    print("🐾 Creating animal species with translations...")
    
    species_list = [
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
    
    species_objects = []
    for species_data in species_list:
        translations = species_data.pop("translations")
        species = AnimalSpecies(**species_data)
        db.add(species)
        db.flush()  # Get the ID
        
        # Add translations
        for lang, trans_data in translations.items():
            translation = AnimalSpeciesTranslation(
                species_id=species.id,
                language=LanguageEnum(lang),
                **trans_data
            )
            db.add(translation)
        
        species_objects.append(species)
    
    db.commit()
    print(f"✅ Created {len(species_list)} animal species with translations")
    return species_objects

def seed_categories(db):
    """Create sample product categories with translations"""
    print("📦 Creating product categories with translations...")
    
    categories_list = [
        {
            "name": "Food",
            "description": "Nutritious and delicious food for all types of pets",
            "translations": {
                "ru": {
                    "name": "Корм",
                    "description": "Питательная и вкусная еда для всех видов домашних животных"
                },
                "hy": {
                    "name": "Կեր",
                    "description": "Սննդային և համեղ կեր բոլոր տեսակի ընտանի կենդանիների համար"
                }
            }
        },
        {
            "name": "Toys",
            "description": "Fun and engaging toys to keep your pets entertained",
            "translations": {
                "ru": {
                    "name": "Игрушки",
                    "description": "Веселые и увлекательные игрушки для развлечения ваших питомцев"
                },
                "hy": {
                    "name": "Խաղալիքներ",
                    "description": "Զվարճալի և հետաքրքիր խաղալիքներ ձեր կենդանիների զվարճացման համար"
                }
            }
        },
        {
            "name": "Accessories",
            "description": "Essential accessories for pet care and comfort",
            "translations": {
                "ru": {
                    "name": "Аксессуары",
                    "description": "Необходимые аксессуары для ухода и комфорта питомцев"
                },
                "hy": {
                    "name": "Աքսեսուարներ",
                    "description": "Անհրաժեշտ աքսեսուարներ կենդանիների խնամքի և հարմարավետության համար"
                }
            }
        },
        {
            "name": "Healthcare",
            "description": "Vitamins, supplements, and healthcare products for pet wellness",
            "translations": {
                "ru": {
                    "name": "Здравоохранение",
                    "description": "Витамины, добавки и продукты для здоровья питомцев"
                },
                "hy": {
                    "name": "Առողջապահություն",
                    "description": "Վիտամիններ, հավելումներ և առողջապահական արտադրանք կենդանիների բարեկեցության համար"
                }
            }
        },
        {
            "name": "Grooming",
            "description": "Grooming tools and products to keep your pet looking their best",
            "translations": {
                "ru": {
                    "name": "Груминг",
                    "description": "Инструменты и средства для ухода, чтобы ваш питомец выглядел наилучшим образом"
                },
                "hy": {
                    "name": "Խնամք",
                    "description": "Խնամքի գործիքներ և արտադրանք՝ ձեր կենդանուն լավագույն տեսքով պահելու համար"
                }
            }
        },
        {
            "name": "Housing",
            "description": "Cages, tanks, beds, and housing solutions for pets",
            "translations": {
                "ru": {
                    "name": "Жилье",
                    "description": "Клетки, аквариумы, кровати и жилищные решения для питомцев"
                },
                "hy": {
                    "name": "Բնակարան",
                    "description": "Վանդակներ, ակվարիումներ, անկողիններ և բնակարան լուծումներ կենդանիների համար"
                }
            }
        },
        {
            "name": "Training",
            "description": "Training aids and tools for pet behavior and obedience",
            "translations": {
                "ru": {
                    "name": "Дрессировка",
                    "description": "Средства и инструменты для дрессировки и послушания питомцев"
                },
                "hy": {
                    "name": "Վարժեցում",
                    "description": "Վարժեցման օգնական միջոցներ և գործիքներ կենդանիների վարքագծի և հնազանդության համար"
                }
            }
        }
    ]
    
    category_objects = []
    for category_data in categories_list:
        translations = category_data.pop("translations")
        category = ProductCategory(**category_data)
        db.add(category)
        db.flush()
        
        # Add translations
        for lang, trans_data in translations.items():
            translation = ProductCategoryTranslation(
                category_id=category.id,
                language=LanguageEnum(lang),
                **trans_data
            )
            db.add(translation)
        
        category_objects.append(category)
    
    db.commit()
    print(f"✅ Created {len(categories_list)} categories with translations")
    return category_objects

def seed_products(db, species_list, categories):
    """Create sample products with translations"""
    print("🛍️  Creating products with translations...")
    
    products_data = [
        # Dog Products
        {"name": "Premium Dog Food - Chicken & Rice", "description": "High-quality dry dog food with real chicken and brown rice. Perfect for adult dogs of all breeds.", "price": 45.99, "stock": 150, "species": "Dogs", "category": "Food", "is_new": True,
         "translations": {
             "ru": {
                 "name": "Премиум корм для собак - Курица и рис",
                 "description": "Высококачественный сухой корм для собак с настоящей курицей и коричневым рисом. Идеален для взрослых собак всех пород."
             },
             "hy": {
                 "name": "Պրեմիում շների կեր - Հավ և բրինձ",
                 "description": "Բարձրորակ չոր կեր շների համար իրական հավով և շագանակագույն բրինձով: Կատարյալ է բոլոր ցեղատեսակների չափահաս շների համար:"
             }
         }},
        {"name": "Interactive Dog Toy Ball", "description": "Durable rubber ball that bounces unpredictably to keep your dog entertained for hours.", "price": 12.99, "stock": 200, "species": "Dogs", "category": "Toys", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Интерактивный мяч для собак",
                 "description": "Прочный резиновый мяч, который непредсказуемо подпрыгивает, развлекая вашу собаку часами."
             },
             "hy": {
                 "name": "Ինտերակտիվ գնդակ շների համար",
                 "description": "Ամուր ռետինե գնդակ, որը անկանխատեսելի է ցատկում՝ ձեր շանը ժամերով զվարճացնելու համար:"
             }
         }},
        {"name": "Adjustable Dog Collar - Large", "description": "Comfortable nylon collar with quick-release buckle. Available in multiple colors.", "price": 15.99, "stock": 100, "species": "Dogs", "category": "Accessories", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Регулируемый ошейник для собак - Большой",
                 "description": "Удобный нейлоновый ошейник с быстросъемной пряжкой. Доступен в различных цветах."
             },
             "hy": {
                 "name": "Կարգավորվող օձիք շների համար - Մեծ",
                 "description": "Հարմարավետ նեյլոնե օձիք արագ բացվող կոճակով: Հասանելի է բազմաթիվ գույներով:"
             }
         }},
        {"name": "Dog Multivitamin Supplements", "description": "Daily vitamins to support your dog's immune system and overall health.", "price": 24.99, "stock": 80, "species": "Dogs", "category": "Healthcare", "is_new": True,
         "translations": {
             "ru": {
                 "name": "Мультивитамины для собак",
                 "description": "Ежедневные витамины для поддержки иммунной системы и общего здоровья вашей собаки."
             },
             "hy": {
                 "name": "Շների համար մուլտիվիտամիններ",
                 "description": "Օրական վիտամիններ ձեր շան իմունային համակարգի և ընդհանուր առողջության աջակցման համար:"
             }
         }},
        {"name": "Professional Dog Grooming Kit", "description": "Complete grooming set with brush, comb, nail clippers, and scissors.", "price": 39.99, "stock": 60, "species": "Dogs", "category": "Grooming", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Профессиональный набор для груминга собак",
                 "description": "Полный набор для груминга с щеткой, расческой, кусачками для ногтей и ножницами."
             },
             "hy": {
                 "name": "Շների պրոֆեսիոնալ խնամքի հավաքածու",
                 "description": "Ամբողջական խնամքի հավաքածու՝ խոզանակ, սանր, եղունջների մկրատ և մկրատ:"
             }
         }},
        
        # Cat Products
        {"name": "Gourmet Cat Food - Salmon Feast", "description": "Premium wet cat food made with real salmon. Rich in protein and omega-3.", "price": 29.99, "stock": 120, "species": "Cats", "category": "Food", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Гурман корм для кошек - Лосось",
                 "description": "Премиум влажный корм для кошек из настоящего лосося. Богат белком и омега-3."
             },
             "hy": {
                 "name": "Գուրման կատուների կեր - Սաղմոն",
                 "description": "Պրեմիում թաց կեր կատուների համար իրական սաղմոնով: Հարուստ է սպիտակուցով և օմեգա-3-ով:"
             }
         }},
        {"name": "Catnip Mouse Toy Set", "description": "Set of 5 colorful mice filled with organic catnip to drive your cat wild.", "price": 9.99, "stock": 180, "species": "Cats", "category": "Toys", "is_new": True,
         "translations": {
             "ru": {
                 "name": "Набор игрушек-мышек с кошачьей мятой",
                 "description": "Набор из 5 разноцветных мышек, наполненных органической кошачьей мятой, чтобы свести вашу кошку с ума."
             },
             "hy": {
                 "name": "Կատվի անանուխի մկնիկների հավաքածու",
                 "description": "5 գունագեղ մկնիկների հավաքածու՝ լցված օրգանական կատվի անանուխով՝ ձեր կատուն խելագարելու համար:"
             }
         }},
        {"name": "Automatic Cat Water Fountain", "description": "Circulating water fountain encourages cats to drink more water. Ultra-quiet pump.", "price": 34.99, "stock": 70, "species": "Cats", "category": "Accessories", "is_new": True,
         "translations": {
             "ru": {
                 "name": "Автоматический фонтан для кошек",
                 "description": "Циркулирующий фонтан побуждает кошек пить больше воды. Ультра-тихий насос."
             },
             "hy": {
                 "name": "Ավտոմատ ջրային շատրվան կատուների համար",
                 "description": "Շրջանառվող ջրի շատրվանը խրախուսում է կատուներին ավելի շատ ջուր խմել: Գերանձ պոմպ:"
             }
         }},
        {"name": "Cat Dental Care Treats", "description": "Crunchy treats that help reduce tartar and freshen breath.", "price": 11.99, "stock": 150, "species": "Cats", "category": "Healthcare", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Лакомства для ухода за зубами кошек",
                 "description": "Хрустящие лакомства, которые помогают уменьшить зубной камень и освежить дыхание."
             },
             "hy": {
                 "name": "Կատուների ատամների խնամքի համար նախատեսված համեղություններ",
                 "description": "Խռչող համեղություններ, որոնք օգնում են կրճատել ատամների քարը և թարմացնել շնչառությունը:"
             }
         }},
        {"name": "Cat Self-Grooming Arch", "description": "Bristle arch allows cats to groom themselves while you watch them enjoy.", "price": 19.99, "stock": 90, "species": "Cats", "category": "Grooming", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Арка для самостоятельного груминга кошек",
                 "description": "Арка со щетинками позволяет кошкам ухаживать за собой, пока вы наблюдаете, как они наслаждаются."
             },
             "hy": {
                 "name": "Կատվի ինքնախնամքի կամար",
                 "description": "Կամարը խոզանակներով թույլ է տալիս կատուներին խնամել իրենց, մինչ դուք նայում եք, թե ինչպես են վայելում:"
             }
         }},
        
        # Bird Products
        {"name": "Premium Bird Seed Mix", "description": "Nutritious blend of seeds, nuts, and dried fruits for all bird species.", "price": 18.99, "stock": 100, "species": "Birds", "category": "Food", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Премиум смесь семян для птиц",
                 "description": "Питательная смесь семян, орехов и сушеных фруктов для всех видов птиц."
             },
             "hy": {
                 "name": "Պրեմիում սերմերի խառնուրդ թռչունների համար",
                 "description": "Սննդարար սերմերի, ընկույզների և չորացրած մրգերի խառնուրդ բոլոր տեսակի թռչունների համար:"
             }
         }},
        {"name": "Bird Swing Perch with Bell", "description": "Natural wood swing with entertaining bell. Perfect for parakeets and small birds.", "price": 8.99, "stock": 140, "species": "Birds", "category": "Toys", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Качели для птиц с колокольчиком",
                 "description": "Качели из натурального дерева с развлекательным колокольчиком. Идеально для попугайчиков и маленьких птиц."
             },
             "hy": {
                 "name": "Թռչունների ճոճանակ զանգակով",
                 "description": "Բնական փայտից ճոճանակ զվարճալի զանգակով: Կատարյալ է թութակների և փոքր թռչունների համար:"
             }
         }},
        {"name": "Stainless Steel Bird Cage", "description": "Spacious cage with multiple perches and feeding stations. Easy to clean.", "price": 89.99, "stock": 35, "species": "Birds", "category": "Housing", "is_new": True,
         "translations": {
             "ru": {
                 "name": "Клетка из нержавеющей стали для птиц",
                 "description": "Просторная клетка с несколькими жердочками и кормушками. Легко чистится."
             },
             "hy": {
                 "name": "Անժանգ պողպատից վանդակ թռչունների համար",
                 "description": "Ընդարձակ վանդակ բազմաթիվ նստատեղերով և կերակրման կայաններով: Հեշտ է մաքրել:"
             }
         }},
        
        # Fish Products
        {"name": "Tropical Fish Flakes", "description": "Complete nutrition for all tropical fish. Enhances colors naturally.", "price": 13.99, "stock": 200, "species": "Fish", "category": "Food", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Хлопья для тропических рыб",
                 "description": "Полноценное питание для всех тропических рыб. Естественно улучшает цвета."
             },
             "hy": {
                 "name": "Թաթիկներ արևադարձային ձկների համար",
                 "description": "Ամբողջական սնուցում բոլոր արևադարձային ձկների համար: Բնականորեն բարելավում է գույները:"
             }
         }},
        {"name": "Aquarium Decoration Castle", "description": "Detailed resin castle provides hiding spots and enhances aquarium aesthetics.", "price": 22.99, "stock": 85, "species": "Fish", "category": "Accessories", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Декоративный замок для аквариума",
                 "description": "Детализированный смоляной замок обеспечивает укрытия и улучшает эстетику аквариума."
             },
             "hy": {
                 "name": "Ակվարիումի զարդարանքի դղյակ",
                 "description": "Մանրամասն սմոլային դղյակը թաքստոցներ է տալիս և բարելավում է ակվարիումի գեղագիտությունը:"
             }
         }},
        {"name": "LED Aquarium Light", "description": "Energy-efficient LED lighting with adjustable color spectrum for plant growth.", "price": 44.99, "stock": 50, "species": "Fish", "category": "Housing", "is_new": True,
         "translations": {
             "ru": {
                 "name": "LED освещение для аквариума",
                 "description": "Энергоэффективное LED освещение с регулируемым цветовым спектром для роста растений."
             },
             "hy": {
                 "name": "LED լուսավորություն ակվարիումի համար",
                 "description": "Էներգաարդյունավետ LED լուսավորություն կարգավորվող գունային սպեկտրով բույսերի աճի համար:"
             }
         }},
        
        # Rabbit Products
        {"name": "Timothy Hay for Rabbits - 5lb", "description": "Fresh, high-fiber timothy hay essential for rabbit dental and digestive health.", "price": 16.99, "stock": 110, "species": "Rabbits", "category": "Food", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Сено тимофеевка для кроликов - 5 фунтов",
                 "description": "Свежее сено тимофеевки с высоким содержанием клетчатки, необходимое для здоровья зубов и пищеварения кроликов."
             },
             "hy": {
                 "name": "Տիմոթի խոտ ճագարների համար - 5 ֆունտ",
                 "description": "Թարմ, բարձր մանրաթելային տիմոթի խոտ՝ անհրաժեշտ ճագարների ատամների և մարսողության առողջության համար:"
             }
         }},
        {"name": "Rabbit Chew Toy Bundle", "description": "Set of natural wood chews to keep rabbit teeth healthy and trim.", "price": 14.99, "stock": 95, "species": "Rabbits", "category": "Toys", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Набор игрушек-погрызушек для кроликов",
                 "description": "Набор жевательных игрушек из натурального дерева для поддержания здоровья и подстригания зубов кроликов."
             },
             "hy": {
                 "name": "Ճագարների ծամոն խաղալիքների հավաքածու",
                 "description": "Բնական փայտից ծամոն խաղալիքների հավաքածու՝ ճագարների ատամների առողջությունը և հարդարումը պահպանելու համար:"
             }
         }},
        {"name": "Large Rabbit Hutch", "description": "Spacious indoor/outdoor hutch with separate sleeping and play areas.", "price": 149.99, "stock": 25, "species": "Rabbits", "category": "Housing", "is_new": True,
         "translations": {
             "ru": {
                 "name": "Большая клетка для кроликов",
                 "description": "Просторная клетка для помещений/улицы с отдельными зонами для сна и игр."
             },
             "hy": {
                 "name": "Մեծ վանդակ ճագարների համար",
                 "description": "Ընդարձակ ներքին/արտաքին վանդակ առանձին քնի և խաղի տարածքներով:"
             }
         }},
        
        # Hamster Products
        {"name": "Hamster Food Pellets", "description": "Balanced nutrition pellets fortified with vitamins and minerals.", "price": 9.99, "stock": 160, "species": "Hamsters", "category": "Food", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Гранулы корма для хомяков",
                 "description": "Сбалансированные питательные гранулы, обогащенные витаминами и минералами."
             },
             "hy": {
                 "name": "Համստերների կերի գրանուլաներ",
                 "description": "Հավասարակշռված սննդարար գրանուլաներ՝ հարստացված վիտամիններով և հանքանյութերով:"
             }
         }},
        {"name": "Hamster Exercise Wheel", "description": "Silent spinner wheel for safe and quiet exercise. Multiple sizes available.", "price": 12.99, "stock": 130, "species": "Hamsters", "category": "Toys", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Беговое колесо для хомяков",
                 "description": "Бесшумное вращающееся колесо для безопасных и тихих упражнений. Доступно несколько размеров."
             },
             "hy": {
                 "name": "Համստերների մարզման անիվ",
                 "description": "Անլսելի պտտվող անիվ անվտանգ և հանգիստ մարզման համար: Հասանելի է բազմաթիվ չափսեր:"
             }
         }},
        {"name": "Deluxe Hamster Cage with Tubes", "description": "Multi-level habitat with colorful tubes and hideouts for exploration.", "price": 59.99, "stock": 40, "species": "Hamsters", "category": "Housing", "is_new": True,
         "translations": {
             "ru": {
                 "name": "Делюкс клетка для хомяков с трубками",
                 "description": "Многоуровневая среда обитания с красочными трубками и укрытиями для исследования."
             },
             "hy": {
                 "name": "Դելյուքս վանդակ համստերների համար խողովակներով",
                 "description": "Բազմամակարդակ բնակարան գունագեղ խողովակներով և թաքստոցներով ուսումնասիրության համար:"
             }
         }},
        
        # Reptile Products
        {"name": "Live Crickets (50 count)", "description": "Fresh live crickets, gut-loaded for maximum nutrition. Perfect for reptiles.", "price": 11.99, "stock": 75, "species": "Reptiles", "category": "Food", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Живые сверчки (50 штук)",
                 "description": "Свежие живые сверчки, насыщенные питательными веществами. Идеально для рептилий."
             },
             "hy": {
                 "name": "Ողջ ճռիկներ (50 հատ)",
                 "description": "Թարմ կենդանի ճռիկներ՝ լցված սննդանյութերով առավելագույն սնուցման համար: Կատարյալ է սողունների համար:"
             }
         }},
        {"name": "Reptile Heating Lamp", "description": "UVB heating lamp essential for reptile health and metabolism.", "price": 32.99, "stock": 65, "species": "Reptiles", "category": "Accessories", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Нагревательная лампа для рептилий",
                 "description": "UVB нагревательная лампа, необходимая для здоровья и метаболизма рептилий."
             },
             "hy": {
                 "name": "Սողունների տաքացման լամպ",
                 "description": "UVB տաքացման լամպ՝ անհրաժեշտ սողունների առողջության և նյութափոխանակության համար:"
             }
         }},
        {"name": "Glass Terrarium 20-Gallon", "description": "Front-opening terrarium with screen top. Ideal for most reptile species.", "price": 119.99, "stock": 30, "species": "Reptiles", "category": "Housing", "is_new": True,
         "translations": {
             "ru": {
                 "name": "Стеклянный террариум 20 галлонов",
                 "description": "Террариум с передним открыванием и сетчатой крышкой. Идеален для большинства видов рептилий."
             },
             "hy": {
                 "name": "Ապակե տերարիում 20 գալոն",
                 "description": "Տերարիում առջևի բացվող դռնով և ցանցի կափարիչով: Կատարյալ է սողունների մեծ մասի համար:"
             }
         }},
        
        # Guinea Pig Products
        {"name": "Guinea Pig Pellet Food", "description": "Vitamin C fortified pellets specially formulated for guinea pigs.", "price": 14.99, "stock": 125, "species": "Guinea Pigs", "category": "Food", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Гранулированный корм для морских свинок",
                 "description": "Гранулы, обогащенные витамином С, специально разработанные для морских свинок."
             },
             "hy": {
                 "name": "Ծովախոզուկների գրանուլյար կեր",
                 "description": "Վիտամին C-ով հարստացված գրանուլաներ՝ հատուկ ձևակերպված ծովախոզուկների համար:"
             }
         }},
        {"name": "Guinea Pig Hideout House", "description": "Wooden hideout provides security and privacy for nervous guinea pigs.", "price": 18.99, "stock": 80, "species": "Guinea Pigs", "category": "Accessories", "is_new": False,
         "translations": {
             "ru": {
                 "name": "Домик-укрытие для морских свинок",
                 "description": "Деревянное укрытие обеспечивает безопасность и уединение для нервных морских свинок."
             },
             "hy": {
                 "name": "Ծովախոզուկների թաքստոց տուն",
                 "description": "Փայտե թաքստոցն ապահովում է անվտանգություն և գաղտնիություն նյարդային ծովախոզուկների համար:"
             }
         }},
        {"name": "Guinea Pig Vitamin C Drops", "description": "Essential vitamin C supplement to prevent scurvy and boost immunity.", "price": 13.99, "stock": 90, "species": "Guinea Pigs", "category": "Healthcare", "is_new": True,
         "translations": {
             "ru": {
                 "name": "Капли витамина С для морских свинок",
                 "description": "Необходимая добавка витамина С для предотвращения цинги и укрепления иммунитета."
             },
             "hy": {
                 "name": "Ծովախոզուկների վիտամին C կաթիլներ",
                 "description": "Անհրաժեշտ վիտամին C հավելում՝ ցինգան կանխելու և իմունիտետը բարձրացնելու համար:"
             }
         }}
    ]
    
    # Create species and category lookup dictionaries
    species_dict = {s.name: s for s in species_list}
    category_dict = {c.name: c for c in categories}
    
    product_objects = []
    for product_data in products_data:
        translations = product_data.pop("translations")
        species_name = product_data.pop("species")
        category_name = product_data.pop("category")
        
        product = Product(
            **product_data,
            species_id=species_dict[species_name].id,
            category_id=category_dict[category_name].id,
            image_url=f"https://images.unsplash.com/photo-{random.randint(1500000000000, 1700000000000)}"
        )
        db.add(product)
        db.flush()
        
        # Add translations
        for lang, trans_data in translations.items():
            translation = ProductTranslation(
                product_id=product.id,
                language=LanguageEnum(lang),
                **trans_data
            )
            db.add(translation)
        
        product_objects.append(product)
    
    db.commit()
    print(f"✅ Created {len(products_data)} products with translations")
    return product_objects

def seed_news(db):
    """Create sample news articles with translations"""
    print("📰 Creating news articles with translations...")
    
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
            }
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
            }
        },
        {
            "title": "The Benefits of Aquarium Keeping for Mental Health",
            "summary": "Studies show that watching fish in an aquarium can reduce stress and anxiety, making fishkeeping a therapeutic hobby.",
            "content": """In our fast-paced, stress-filled world, people are constantly seeking ways to improve their mental health and well-being. One surprisingly effective method that's gaining recognition is aquarium keeping.

Recent studies from the National Marine Aquarium in Plymouth, UK, have demonstrated that watching fish swim can significantly reduce stress levels and lower blood pressure. The gentle movements, the sound of flowing water, and the peaceful environment created by an aquarium produce a calming effect similar to meditation.

Dr. Lisa Peterson, a clinical psychologist, explains: "The rhythmic movement of fish and the serene aquatic environment engage our attention in a way that's both calming and restorative. It's a form of mindfulness that happens naturally."

Benefits include:
- Reduced heart rate and blood pressure
- Decreased anxiety and stress levels
- Improved mood and emotional well-being
- Better focus and concentration
- Enhanced sleep quality

The study also noted that participants with larger, more diverse aquariums reported greater benefits, though even small desktop aquariums provided positive effects.

For those considering starting this therapeutic hobby, experts recommend beginning with hardy fish species and simple setups, gradually expanding as confidence grows.""",
            "author": "Dr. James Martinez",
            "image_url": "https://images.unsplash.com/photo-1524704654690-b56c05c78a00",
            "published_at": datetime.now() - timedelta(days=7),
            "translations": {
                "ru": {
                    "title": "Польза содержания аквариума для психического здоровья",
                    "summary": "Исследования показывают, что наблюдение за рыбами в аквариуме может снизить стресс и тревогу, делая рыбоводство терапевтическим хобби.",
                    "content": """В нашем быстром, наполненном стрессом мире люди постоянно ищут способы улучшить свое психическое здоровье и благополучие. Одним из удивительно эффективных методов, который получает признание, является содержание аквариума.

Недавние исследования Национального морского аквариума в Плимуте, Великобритания, показали, что наблюдение за плавающими рыбами может значительно снизить уровень стресса и понизить кровяное давление. Нежные движения, звук текущей воды и мирная обстановка, создаваемая аквариумом, производят успокаивающий эффект, подобный медитации.

Доктор Лиза Петерсон, клинический психолог, объясняет: "Ритмичное движение рыб и спокойная водная среда привлекают наше внимание таким образом, который одновременно успокаивает и восстанавливает. Это форма осознанности, которая происходит естественно".

Преимущества включают:
- Снижение частоты сердечных сокращений и кровяного давления
- Снижение уровня тревоги и стресса
- Улучшение настроения и эмоционального благополучия
- Лучшая концентрация и фокусировка
- Улучшенное качество сна

Исследование также отметило, что участники с более крупными, более разнообразными аквариумами сообщали о больших преимуществах, хотя даже маленькие настольные аквариумы обеспечивали положительные эффекты.

Для тех, кто рассматривает начало этого терапевтического хобби, эксперты рекомендуют начинать с выносливых видов рыб и простых установок, постепенно расширяясь по мере роста уверенности."""
                },
                "hy": {
                    "title": "Ակվարիում պահելու առավելությունները հոգեկան առողջության համար",
                    "summary": "Ուսումնասիրությունները ցույց են տալիս, որ ակվարիումում ձկներին դիտելը կարող է նվազեցնել սթրեսը և անհանգստությունը՝ ձկնաբուծությունը դարձնելով թերապևտիկ հոբբի:",
                    "content": """Մեր արագընթաց, սթրեսով լցված աշխարհում մարդիկ անընդհատ ձգտում են բարելավել իրենց հոգեկան առողջությունը և բարեկեցությունը: Մեկ անսպասելիորեն արդյունավետ մեթոդ, որը ստանում է ճանաչում, ակվարիումի պահպանումն է:

Մեծ Բրիտանիայի Պլիմուտի ազգային ծովային ակվարիումի վերջին ուսումնասիրությունները ցույց են տվել, որ լողացող ձկներին դիտելը կարող է զգալիորեն նվազեցնել սթրեսի մակարդակը և իջեցնել արյան ճնշումը: Նուրբ շարժումները, հոսող ջրի ձայնը և ակվարիումի ստեղծած խաղաղ միջավայրը առաջացնում են հանգստացնող ազդեցություն, որը նման է մեդիտացիայի:

Կլինիկական հոգեբան Դոկտոր Լիզա Փիթերսոնը բացատրում է. «Ձկների ռիթմիկ շարժումը և հանգիստ ջրային միջավայրը մեր ուշադրությունը գրավում են այնպիսի ձևով, որը միաժամանակ հանգստացնում և վերականգնում է: Դա գիտակցվածության ձև է, որը տեղի է ունենում բնականաբար»:

Առավելությունները ներառում են.
- Սրտի զարկերի և արյան ճնշման նվազում
- Անհանգստության և սթրեսի մակարդակների նվազում
- Տրամադրության և հուզական բարեկեցության բարելավում
- Լավ կենտրոնացում և ֆոկուս
- Բարելավված քնի որակ

Ուսումնասիրությունը նաև նշել է, որ ավելի մեծ, ավելի բազմազան ակվարիումներ ունեցող մասնակիցները զեկուցել են ավելի մեծ օգուտների մասին, թեև նույնիսկ փոքր սեղանի ակվարիումները տվել են դրական ազդեցություններ:

Նրանց համար, ովքեր դիտարկում են այս թերապևտիկ հոբբին սկսելը, փորձագետները խորհուրդ են տալիս սկսել ամուր ձկների տեսակներից և պարզ կազմավորումներից, աստիճանաբար ընդլայնվելով, երբ վստահությունը մեծանում է:"""
                }
            }
        },
        {
            "title": "Exotic Birds as Pets: What You Need to Know",
            "summary": "Considering a parrot or other exotic bird? Learn about the commitment, care requirements, and joys of bird ownership.",
            "content": """Exotic birds, particularly parrots, make fascinating and rewarding pets, but they require significant commitment and specialized care. Before bringing home a feathered friend, it's crucial to understand what bird ownership entails.

Lifespan Considerations:
Many exotic birds live for decades. Large parrots like Macaws and Cockatoos can live 50-80 years, meaning they may outlive their owners. This long-term commitment should not be taken lightly.

Social Needs:
Birds are highly social creatures that require daily interaction. They can become depressed, develop behavioral problems, or engage in self-destructive behaviors like feather plucking if neglected.

Space Requirements:
Despite their size, birds need large cages and several hours of supervised out-of-cage time daily. The cage should be spacious enough for the bird to fully spread its wings.

Diet and Nutrition:
A varied diet including pellets, fresh fruits, vegetables, and occasional nuts is essential. Avoid avocado, chocolate, caffeine, and salt, which are toxic to birds.

Noise Level:
Many exotic birds are loud, especially during dawn and dusk. Screaming is natural behavior but can be challenging in apartments or noise-sensitive environments.

Veterinary Care:
Avian veterinarians are specialized and may not be available in all areas. Regular check-ups are essential as birds hide illness well.

Despite these challenges, bird owners report incredible rewards. Birds are intelligent, affectionate, and can form deep bonds with their owners. They can learn tricks, mimic speech, and provide years of companionship. If you're prepared for the commitment, an exotic bird might be the perfect pet for you.""",
            "author": "Rebecca Foster, Avian Specialist",
            "image_url": "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7",
            "published_at": datetime.now() - timedelta(days=10),
            "translations": {
                "ru": {
                    "title": "Экзотические птицы как домашние животные: что вам нужно знать",
                    "summary": "Рассматриваете попугая или другую экзотическую птицу? Узнайте об обязательствах, требованиях по уходу и радостях владения птицей.",
                    "content": """Экзотические птицы, особенно попугаи, становятся увлекательными и вознаграждающими домашними животными, но они требуют значительных обязательств и специализированного ухода. Прежде чем привести домой пернатого друга, важно понять, что влечет за собой владение птицей.

Соображения по продолжительности жизни:
Многие экзотические птицы живут десятилетиями. Крупные попугаи, такие как ара и какаду, могут жить 50-80 лет, что означает, что они могут пережить своих владельцев. Это долгосрочное обязательство не следует воспринимать легкомысленно.

Социальные потребности:
Птицы - высоко социальные существа, требующие ежедневного взаимодействия. Они могут впасть в депрессию, развить поведенческие проблемы или заниматься саморазрушительным поведением, таким как выщипывание перьев, если их пренебрегать.

Требования к пространству:
Несмотря на свой размер, птицы нуждаются в больших клетках и нескольких часах контролируемого времени вне клетки ежедневно. Клетка должна быть достаточно просторной, чтобы птица могла полностью расправить крылья.

Диета и питание:
Разнообразная диета, включающая гранулы, свежие фрукты, овощи и орехи, является необходимой. Избегайте авокадо, шоколада, кофеина и соли, которые токсичны для птиц.

Уровень шума:
Многие экзотические птицы громкие, особенно на рассвете и в сумерках. Крики - естественное поведение, но могут быть проблематичными в квартирах или шумочувствительных средах.

Ветеринарная помощь:
Ветеринары по птицам специализированы и могут быть недоступны во всех регионах. Регулярные проверки необходимы, так как птицы хорошо скрывают болезни.

Несмотря на эти проблемы, владельцы птиц сообщают о невероятных наградах. Птицы умны, ласковы и могут формировать глубокие связи со своими владельцами. Они могут учить трюки, имитировать речь и обеспечивать годы общения. Если вы готовы к обязательствам, экзотическая птица может быть идеальным питомцем для вас."""
                },
                "hy": {
                    "title": "Էկզոտիկ թռչունները որպես ընտանի կենդանիներ. ինչ պետք է իմանաք",
                    "summary": "Դիտարկում եք թութակ կամ այլ էկզոտիկ թռչուն: Իմացեք պարտավորությունների, խնամքի պահանջների և թռչուն ունենալու ուրախությունների մասին:",
                    "content": """Էկզոտիկ թռչունները, հատկապես թութակները, դառնում են հետաքրքիր և մրցակցային ընտանի կենդանիներ, բայց դրանք պահանջում են զգալի պարտավորություններ և մասնագիտացված խնամք: Փետրավոր ընկերոջը տուն բերելուց առաջ կարևոր է հասկանալ, թե ինչ է ներառում թռչուն ունենալը:

Սպասվող կյանքի տևողության նկատառումներ.
Շատ էկզոտիկ թռչուններ ապրում են տասնամյակներ: Թութակների նման մեծ թռչունները, ինչպիսիք են մակաոն և կակատուն, կարող են ապրել 50-80 տարի, ինչը նշանակում է, որ դրանք կարող են գերազանցել իրենց տերերին: Այս երկարաժամկետ պարտավորությունը չպետք է թեթևամտորեն ընդունվի:

Սոցիալական կարիքներ.
Թռչունները բարձր սոցիալական արարածներ են, որոնք պահանջում են օրական փոխգործակցություն: Նրանք կարող են ընկնել դեպրեսիայի մեջ, զարգացնել վարքային խնդիրներ կամ զբաղվել ինքնավերացական վարքագծով, ինչպիսին է փետուրների քաշելը, եթե անտեսվեն:

Տարածքի պահանջներ.
Չնայած իրենց չափին, թռչուններին անհրաժեշտ են մեծ վանդակներ և օրական մի քանի ժամ հսկողության տակ դուրս վանդակ ժամանակ: Վանդակը պետք է բավականաչափ ընդարձակ լինի, որպեսզի թռչունը կարողանա ամբողջությամբ տարածել իր թևերը:

Դիետա և սնուցում.
Տարբեր դիետա, ներառյալ գրանուլաներ, թարմ մրգեր, բանջարեղեն և ընդհատվող ընկույզ, անհրաժեշտ է: Խուսափեք ավոկադոյից, շոկոլադից, կոֆեինից և աղից, որոնք թունավոր են թռչունների համար:

Շաղախի մակարդակ.
Շատ էկզոտիկ թռչուններ բարձրաձայն են, հատկապես արշալույսին և մթնշաղին: Բղավելը բնական վարքագիծ է, բայց կարող է լինել բարդ բնակարաններում կամ աղմուկի զգայուն միջավայրերում:

Անասնաբուժական խնամք.
Թռչունների անասնաբույժները մասնագիտացված են և կարող են մատչելի չլինել բոլոր տարածքներում: Կանոնավոր ստուգումներն անհրաժեշտ են, քանի որ թռչունները լավ թաքցնում են հիվանդությունը:

Չնայած այս մարտահրավերներին, թռչունների սեփականատերերը հաղորդում են անհավատալի պարգևների մասին: Թռչունները խելացի են, սիրող և կարող են ձևավորել խորը կապեր իրենց տերերի հետ: Նրանք կարող են սովորել հնարքներ, նմանակել խոսքը և ապահովել տարիների ընկերակցություն: Եթե պատրաստ եք պարտավորության, էկզոտիկ թռչունը կարող է ձեզ համար կատարյալ ընտանի կենդանի լինել:"""
                }
            }
        },
        {
            "title": "Understanding Rabbit Behavior: What Your Bunny Is Trying to Tell You",
            "summary": "Rabbits communicate through subtle body language. Learn to decode your rabbit's behaviors and strengthen your bond.",
            "content": """Rabbits are complex, expressive animals with a rich vocabulary of behaviors. Understanding these signals can help you better meet your rabbit's needs and deepen your relationship.

Happy Behaviors:

Binkying: When a rabbit jumps, twists, and kicks in mid-air, they're expressing pure joy. This adorable behavior is a sign of a happy, healthy rabbit.

Purring: Unlike cats, rabbits purr by gently grinding their teeth when content, especially during petting sessions.

Flopping: A rabbit that suddenly flops onto its side is completely relaxed and feels safe in its environment.

Aggressive or Unhappy Behaviors:

Thumping: A loud thump with the hind legs signals fear, annoyance, or a warning to other rabbits about potential danger.

Lunging or Boxing: These behaviors indicate the rabbit feels threatened and is defending itself.

Grunting: Often accompanies aggressive behavior and signals displeasure or territorial feelings.

Communication Behaviors:

Chinning: Rabbits have scent glands under their chins and "chin" objects to mark their territory.

Circling: Circling your feet usually indicates affection and sometimes hormonal behavior in unspayed/unneutered rabbits.

Nudging: A gentle nose nudge is a rabbit's way of asking for attention or treats.

Understanding these behaviors requires patience and observation. Each rabbit has a unique personality, and getting to know your individual bunny's communication style is key to a harmonious relationship. If you notice sudden behavioral changes, consult a rabbit-savvy veterinarian, as rabbits often hide illness until it's severe.""",
            "author": "Amanda Sullivan, Rabbit Behavior Consultant",
            "image_url": "https://images.unsplash.com/photo-1535241749838-299277b6305f",
            "published_at": datetime.now() - timedelta(days=14),
            "translations": {
                "ru": {
                    "title": "Понимание поведения кроликов: что ваш кролик пытается вам сказать",
                    "summary": "Кролики общаются через тонкий язык тела. Научитесь расшифровывать поведение вашего кролика и укрепляйте вашу связь.",
                    "content": """Кролики - сложные, выразительные животные с богатым словарем поведения. Понимание этих сигналов может помочь вам лучше удовлетворить потребности вашего кролика и углубить ваши отношения.

Счастливое поведение:

Бинкинг: когда кролик прыгает, крутится и пинается в воздухе, он выражает чистую радость. Это очаровательное поведение - признак счастливого, здорового кролика.

Мурлыканье: в отличие от кошек, кролики мурлыкают, нежно скрипя зубами, когда довольны, особенно во время сеансов ласки.

Плюхание: кролик, который внезапно плюхается на бок, полностью расслаблен и чувствует себя в безопасности в своей среде.

Агрессивное или несчастное поведение:

Топанье: громкий удар задними лапами сигнализирует о страхе, раздражении или предупреждении другим кроликам о потенциальной опасности.

Бросок или бокс: эти поведения указывают на то, что кролик чувствует угрозу и защищается.

Ворчание: часто сопровождает агрессивное поведение и сигнализирует о недовольстве или территориальных чувствах.

Коммуникативное поведение:

Подбородок: у кроликов есть запаховые железы под подбородком, и они "подбородком" метят предметы, чтобы пометить свою территорию.

Кружение: кружение вокруг ваших ног обычно указывает на привязанность, а иногда и на гормональное поведение у нестерилизованных/некастрированных кроликов.

Толчок: нежный толчок носом - это способ кролика просить внимания или угощений.

Понимание этого поведения требует терпения и наблюдения. Каждый кролик имеет уникальную личность, и знакомство с индивидуальным стилем общения вашего кролика является ключом к гармоничным отношениям. Если вы заметите внезапные изменения в поведении, обратитесь к ветеринару, знакомому с кроликами, так как кролики часто скрывают болезнь, пока она не станет тяжелой."""
                },
                "hy": {
                    "title": "Հասկանալով ճագարների վարքագիծը. ինչ է ձեր ճագարը փորձում ասել ձեզ",
                    "summary": "Ճագարները հաղորդակցվում են նուար մարմնի լեզվով: Սովորեք վերծանել ձեր ճագարի վարքագիծը և ամրապնդեք ձեր կապը:",
                    "content": """Ճագարները բարդ, արտահայտիչ կենդանիներ են՝ վարքագծերի հարուստ բառապաշարով: Այս ազդանշանները հասկանալը կարող է օգնել ձեզ ավելի լավ բավարարել ձեր ճագարի կարիքները և խորացնել ձեր հարաբերությունները:

Ուրախ վարքագիծ.

Բինկինգ. երբ ճագարը ցատկում է, ոլորվում և կռանում օդում, նա արտահայտում է մաքուր ուրախություն: Այս հրաշալի վարքագիծը երջանիկ, առողջ ճագարի նշան է:

Մռռալը. ի տարբերություն կատուների, ճագարները մռռում են, քնքշորեն ատամները մանրացնելով, երբ բավարարված են, հատկապես փայփայման ժամանակ:

Մեջքի վրա պառկելը. ճագարը, որը հանկարծակի մեջքի վրա է պառկում, ամբողջովին հանգստացած է և իրեն ապահով է զգում իր միջավայրում:

Ագրեսիվ կամ դժգոհ վարքագիծ.

Ծանր քայլեր. հետին ոտքերով բարձրաձայն հարվածը ազդանշան է վախի, գրգռվածության կամ այլ ճագարների համար նախազգուշացման պոտենցիալ վտանգի մասին:

Լանջի կամ բռնցքամարտ. այս վարքագծերը ցույց են տալիս, որ ճագարը զգում է սպառնալիք և պաշտպանում է իրեն:

Գռռալը. հաճախ ուղեկցում է ագրեսիվ վարքագծին և ազդանշանում է դժգոհություն կամ տարածքային զգացումներ:

Հաղորդակցության վարքագիծ.

Ծնոտի մազեր. ճագարները ունեն հոտի գեղձեր ծնոտի տակ և «ծնոտի» օբյեկտներ՝ իրենց տարածքը նշելու համար:

Շրջապտույտ. ձեր ոտքերի շուրջը շրջապտույտը սովորաբար ցույց է տալիս սեր և երբեմն հորմոնալ վարքագիծ չստերիլիզացված/չկաստրացված ճագարների մոտ:

Թեթև հրում. քնքուշ քթի հրումը ճագարի ձևն է ուշադրություն կամ համեղություններ խնդրելու համար:

Այս վարքագծերը հասկանալը պահանջում է հանդուրժողականություն և դիտարկում: Յուրաքանչյուր ճագար ունի եզակի անհատականություն, և ձեր անհատական ճագարի հաղորդակցության ոճին ծանոթանալը բանալի է ներդաշնակ հարաբերությունների համար: Եթե նկատում եք վարքագծի հանկարծակի փոփոխություններ, խորհրդակցեք ճագարների մասնագետ անասնաբույժի հետ, քանի որ ճագարները հաճախ թաքցնում են հիվանդությունը, մինչև այն լինի ծանր:"""
                }
            }
        },
        {
            "title": "Reptile Care 101: Essential Tips for Beginners",
            "summary": "Thinking about getting a reptile? Here's what you need to know about habitat setup, feeding, and health care.",
            "content": """Reptiles make unique and fascinating pets, but they have very different needs compared to traditional pets like dogs and cats. Before bringing home a reptile, it's essential to understand proper care requirements.

Choosing the Right Species:
For beginners, consider hardy species like Leopard Geckos, Corn Snakes, or Bearded Dragons. These reptiles are relatively forgiving and adapt well to captivity.

Habitat Requirements:

Temperature Control: Reptiles are ectothermic and rely on external heat sources. Most require both a basking spot (90-100°F) and a cooler area (75-80°F).

Lighting: Many reptiles need UVB lighting for vitamin D3 synthesis and calcium absorption. Replace bulbs every 6-12 months as UVB output decreases.

Humidity: Different species have different humidity needs. Tropical species need higher humidity (60-80%) while desert species need lower levels (30-40%).

Substrate: Choose appropriate substrate for your species. Avoid loose substrates for young reptiles due to impaction risk.

Feeding:
Research your specific reptile's dietary needs. Some are carnivores requiring live insects or rodents, while others are herbivores or omnivores. Proper supplementation with calcium and vitamins is crucial.

Health Monitoring:
Regular observation is key. Warning signs include lethargy, loss of appetite, abnormal shedding, respiratory issues, or unusual behavior. Find a reptile veterinarian before you need one.

Common Mistakes to Avoid:
- Inadequate enclosure size
- Improper temperature or humidity
- Poor diet or lack of supplementation
- Handling too much too soon
- Mixing incompatible species

With proper research, setup, and dedication, reptile keeping can be an incredibly rewarding hobby. These fascinating creatures offer a window into a different world and can live for many years with proper care.""",
            "author": "Dr. Nathan Brooks, Herpetologist",
            "image_url": "https://images.unsplash.com/photo-1503596476-1c12a8ba09a9",
            "published_at": datetime.now() - timedelta(days=18),
            "translations": {
                "ru": {
                    "title": "Уход за рептилиями 101: основные советы для начинающих",
                    "summary": "Думаете о получении рептилии? Вот что вам нужно знать о настройке среды обитания, кормлении и уходе за здоровьем.",
                    "content": """Рептилии делают уникальных и увлекательных домашних животных, но они имеют совершенно разные потребности по сравнению с традиционными домашними животными, такими как собаки и кошки. Прежде чем привести домой рептилию, важно понять правильные требования по уходу.

Выбор правильного вида:
Для начинающих рассмотрите выносливые виды, такие как Леопардовые гекконы, Кукурузные змеи или Бородатые агамы. Эти рептилии относительно снисходительны и хорошо адаптируются к неволе.

Требования к среде обитания:

Контроль температуры: рептилии экзотермичны и полагаются на внешние источники тепла. Большинство требует как места для обогрева (90-100°F), так и более прохладной области (75-80°F).

Освещение: многие рептилии нуждаются в UVB освещении для синтеза витамина D3 и абсорбции кальция. Заменяйте лампы каждые 6-12 месяцев, так как выход UVB снижается.

Влажность: разные виды имеют разные потребности во влажности. Тропические виды нуждаются в более высокой влажности (60-80%), в то время как пустынные виды нуждаются в более низких уровнях (30-40%).

Субстрат: выберите подходящий субстрат для вашего вида. Избегайте рыхлых субстратов для молодых рептилий из-за риска закупорки.

Кормление:
Исследуйте диетические потребности вашей конкретной рептилии. Некоторые являются плотоядными, требующими живых насекомых или грызунов, в то время как другие являются травоядными или всеядными. Правильное добавление кальция и витаминов имеет решающее значение.

Мониторинг здоровья:
Регулярное наблюдение является ключевым. Предупреждающие знаки включают летаргию, потерю аппетита, аномальную линьку, респираторные проблемы или необычное поведение. Найдите ветеринара по рептилиям до того, как он понадобится.

Общие ошибки, которых следует избегать:
- Неадекватный размер вольера
- Неправильная температура или влажность
- Плохая диета или отсутствие добавок
- Слишком много обработки слишком рано
- Смешивание несовместимых видов

При правильном исследовании, настройке и посвящении, содержание рептилий может быть невероятно вознаграждающим хобби. Эти увлекательные существа предлагают окно в другой мир и могут жить много лет при правильном уходе."""
                },
                "hy": {
                    "title": "Սողունների խնամք 101. հիմնական խորհուրդներ սկսնակների համար",
                    "summary": "Մտածում եք սողուն ստանալու մասին: Ահա այն, ինչ դուք պետք է իմանաք բնակավայրի կազմակերպման, կերակրման և առողջապահական խնամքի մասին:",
                    "content": """Սողունները դարձնում են եզակի և հետաքրքիր ընտանի կենդանիներ, բայց դրանք ունեն շատ տարբեր կարիքներ՝ համեմատած ավանդական ընտանի կենդանիների հետ, ինչպիսիք են շները և կատուները: Սողունը տուն բերելուց առաջ կարևոր է հասկանալ ճիշտ խնամքի պահանջները:

Ճիշտ տեսակի ընտրություն.
Սկսնակների համար հաշվի առեք ամուր տեսակներ, ինչպիսիք են Leopard Geckos, Corn Snakes կամ Bearded Dragons: Այս սողունները համեմատաբար ներողամիտ են և լավ հարմարվում են գերությանը:

Բնակավայրի պահանջներ.

Ջերմաստիճանի վերահսկում. սողունները էկտոթերմ են և հենվում են արտաքին ջերմության աղբյուրների վրա: Մեծ մասը պահանջում է և՛ արևավորման վայր (90-100°F), և՛ ավելի սառը տարածք (75-80°F):

Լուսավորություն. շատ սողունների կարիք ունեն UVB լուսավորության վիտամին D3 սինթեզի և կալցիումի ներծծման համար: Լամպերը փոխարինեք յուրաքանչյուր 6-12 ամիսը մեկ, քանի որ UVB արտադրությունը նվազում է:

Խոնավություն. տարբեր տեսակներ ունեն տարբեր խոնավության կարիքներ: Արևադարձային տեսակներին անհրաժեշտ է ավելի բարձր խոնավություն (60-80%), մինչդեռ անապատային տեսակներին անհրաժեշտ է ավելի ցածր մակարդակներ (30-40%):

Հիմք. ընտրեք համապատասխան հիմք ձեր տեսակի համար: Խուսափեք ազատ հիմքերից երիտասարդ սողունների համար պտղի վտանգի պատճառով:

Կերակրում.
Հետազոտեք ձեր կոնկրետ սողունի սննդային կարիքները: Ոմանք գիշատիչներ են, որոնք պահանջում են կենդանի միջատներ կամ կրծողներ, մինչդեռ մյուսները խոտակերներ կամ ամենակերներ են: Կալցիումի և վիտամինների պատշաճ հավելումը կարևոր է:

Առողջության մոնիտորինգ.
Կանոնավոր դիտարկումը բանալին է: Նախազգուշացման նշանները ներառում են դանդաղություն, ախորժակի կորուստ, աննորմալ թափվել, շնչառական խնդիրներ կամ անսովոր վարքագիծ: Գտեք սողունների անասնաբույժ նախքան այն ձեզ պետք գա:

Սովորական սխալներ, որոնցից պետք է խուսափել.
- Բավարար չափի վանդակ
- Անպատշաջ ջերմաստիճան կամ խոնավություն
- Վատ դիետա կամ հավելումների բացակայություն
- Շատ շուտ շատ մշակում
- Անհամատեղելի տեսակների խառնում

Ճիշտ հետազոտությամբ, կազմակերպմամբ և նվիրվածությամբ, սողունների պահպանումը կարող է լինել անհավատալիորեն մրցակցային հոբբի: Այս հետաքրքիր արարածները պատուհան են առաջարկում տարբեր աշխարհ և կարող են ապրել շատ տարիներ ճիշտ խնամքով:"""
                }
            }
        },
        {
            "title": "Spring Sale Announcement: Up to 40% Off Pet Supplies!",
            "summary": "Don't miss our biggest sale of the year! Huge discounts on food, toys, accessories, and more for all types of pets.",
            "content": """We're excited to announce our Annual Spring Sale with incredible savings across our entire store!

Sale Highlights:

• 40% off all premium pet foods
• Buy 2 Get 1 Free on all toys
• 30% off grooming supplies
• 25% off cages, tanks, and habitats
• Special bundles with up to 50% savings

Featured Deals:

Premium Dog Food: Now only $27.59 (was $45.99)
Cat Water Fountain: $24.49 (was $34.99)
Large Rabbit Hutch: $104.99 (was $149.99)
Glass Terrarium 20-Gallon: $89.99 (was $119.99)

Plus, free shipping on orders over $50!

The sale runs from March 15-31, so don't wait! Stock up on essentials and treat your pets to something special. Shop online or visit our store location.

Thank you for being part of our animal-loving community. Your pets deserve the best, and we're here to help you provide it at prices you'll love!""",
            "author": "Animal Store Team",
            "image_url": "https://images.unsplash.com/photo-1601758228041-f3b2795255f1",
            "published_at": datetime.now() - timedelta(days=1),
            "translations": {
                "ru": {
                    "title": "Объявление о весенней распродаже: скидки до 40% на товары для домашних животных!",
                    "summary": "Не пропустите нашу самую большую распродажу года! Огромные скидки на корм, игрушки, аксессуары и многое другое для всех видов домашних животных.",
                    "content": """Мы рады объявить нашу Ежегодную Весеннюю Распродажу с невероятными скидками по всему нашему магазину!

Основные моменты распродажи:

• 40% скидка на все премиальные корма для домашних животных
• Купи 2 Получи 1 Бесплатно на все игрушки
• 30% скидка на средства для груминга
• 25% скидка на клетки, аквариумы и среды обитания
• Специальные наборы со скидкой до 50%

Избранные предложения:

Премиум корм для собак: теперь всего $27.59 (было $45.99)
Фонтан для кошек: $24.49 (было $34.99)
Большая клетка для кроликов: $104.99 (было $149.99)
Стеклянный террариум 20 галлонов: $89.99 (было $119.99)

Плюс, бесплатная доставка на заказы свыше $50!

Распродажа проходит с 15 по 31 марта, так что не ждите! Запаситесь необходимым и порадуйте своих питомцев чем-то особенным. Покупайте онлайн или посетите наш магазин.

Спасибо, что являетесь частью нашего сообщества любителей животных. Ваши питомцы заслуживают лучшего, и мы здесь, чтобы помочь вам предоставить это по ценам, которые вам понравятся!"""
                },
                "hy": {
                    "title": "Գարնանային վաճառքի հայտարարություն. մինչև 40% զեղչ ընտանի կենդանիների պարագաների վրա:",
                    "summary": "Բաց մի թողեք մեր տարվա ամենամեծ վաճառքը: Հսկայական զեղչեր կերերի, խաղալիքների, աքսեսուարների և ավելի շատի վրա բոլոր տեսակի ընտանի կենդանիների համար:",
                    "content": """Մենք ուրախ ենք հայտարարել մեր Տարեկան Գարնանային Վաճառքը՝ անհավատալի խնայողություններով մեր ամբողջ խանութում:

Վաճառքի հիմնական կետերը.

• 40% զեղչ բոլոր պրեմիում ընտանի կենդանիների կերերի վրա
• Գնեք 2 Ստացեք 1 Անվճար բոլոր խաղալիքների վրա
• 30% զեղչ խնամքի միջոցների վրա
• 25% զեղչ վանդակների, ակվարիումների և բնակավայրերի վրա
• Հատուկ խմբեր մինչև 50% խնայողություններով

Առանձնացված առաջարկներ.

Շների պրեմիում կեր. այժմ միայն $27.59 (էր $45.99)
Կատուների ջրի շատրվան. $24.49 (էր $34.99)
Ճագարների մեծ վանդակ. $104.99 (էր $149.99)
Ապակե տերարիում 20 գալոն. $89.99 (էր $119.99)

Գումարած, անվճար առաքում $50-ից ավելի պատվերների համար:

Վաճառքը տևում է մարտի 15-ից մինչև 31-ը, այնպես որ մի սպասեք: Պաշարեք անհրաժեշտ իրերը և հաճույք պատճառեք ձեր կենդանիներին ինչ-որ հատուկ բանով: Գնումներ կատարեք առցանց կամ այցելեք մեր խանութի տեղը:

Շնորհակալություն, որ մեր կենդանիներին սիրող համայնքի մի մասն եք: Ձեր ընտանի կենդանիները արժանի են լավագույնին, և մենք այստեղ ենք՝ օգնելու ձեզ ապահովել այն գներով, որոնք դուք կսիրեք:"""
                }
            }
        },
        {
            "title": "New Arrivals: Premium Bird Supplies Now in Stock",
            "summary": "We've just received a shipment of high-quality bird cages, toys, and nutrition products perfect for your feathered friends.",
            "content": """Calling all bird enthusiasts! We're thrilled to announce the arrival of our new premium bird product line, featuring top-quality supplies from leading manufacturers.

New Products Include:

Spacious Aviaries:
Multiple size options for single or multiple birds, featuring powder-coated steel construction and easy-access doors.

Interactive Toy Collection:
Puzzle feeders, foraging toys, and activity centers designed to keep birds mentally stimulated and physically active.

Gourmet Nutrition Line:
Species-specific food blends, organic treats, and vitamin supplements formulated by avian nutritionists.

Perch Variety Pack:
Natural wood perches in different diameters to promote foot health and prevent arthritis.

Why Choose Our Premium Line?

Quality Materials: All products are made from bird-safe, non-toxic materials.
Expert Selection: Products chosen based on input from avian veterinarians and experienced bird keepers.
Durability: Built to withstand even the strongest beaks and claws.
Enrichment Focused: Designed to promote natural behaviors and prevent boredom.

Visit our bird section to see the full collection. Our knowledgeable staff can help you choose the perfect products for your specific bird species. Remember, happy birds make happy owners!

Limited quantities available, so come in soon to ensure you don't miss out on these exceptional products.""",
            "author": "Animal Store Team",
            "image_url": "https://images.unsplash.com/photo-1555169062-013468b47731",
            "published_at": datetime.now() - timedelta(days=3),
            "translations": {
                "ru": {
                    "title": "Новые поступления: премиальные товары для птиц теперь в наличии",
                    "summary": "Мы только что получили партию высококачественных клеток, игрушек и продуктов питания для птиц, идеально подходящих для ваших пернатых друзей.",
                    "content": """Всем энтузиастам птиц! Мы рады объявить о прибытии нашей новой премиальной линейки продуктов для птиц, включающей товары высшего качества от ведущих производителей.

Новые продукты включают:

Просторные вольеры:
Несколько вариантов размеров для одной или нескольких птиц, с конструкцией из стали с порошковым покрытием и легкодоступными дверцами.

Интерактивная коллекция игрушек:
Пазловые кормушки, игрушки для поиска пищи и центры активности, разработанные для поддержания умственной стимуляции и физической активности птиц.

Гурмэ линия питания:
Специфические для видов смеси корма, органические лакомства и витаминные добавки, разработанные птичьими диетологами.

Набор разнообразных насестов:
Натуральные деревянные насесты разного диаметра для поддержания здоровья лап и предотвращения артрита.

Почему выбирать нашу премиальную линию?

Качественные материалы: все продукты сделаны из безопасных для птиц, нетоксичных материалов.
Экспертный отбор: продукты выбраны на основе мнения птичьих ветеринаров и опытных птицеводов.
Долговечность: построены, чтобы выдерживать даже самые сильные клювы и когти.
Фокус на обогащение: разработаны для поощрения естественного поведения и предотвращения скуки.

Посетите наш раздел для птиц, чтобы увидеть полную коллекцию. Наши знающие сотрудники могут помочь вам выбрать идеальные продукты для вашего конкретного вида птиц. Помните, счастливые птицы делают счастливых владельцев!

Ограниченное количество в наличии, так что приходите скоро, чтобы убедиться, что вы не упустите эти исключительные продукты."""
                },
                "hy": {
                    "title": "Նոր ժամանումներ. պրեմիում թռչունների պարագաներ այժմ պահեստում",
                    "summary": "Մենք նոր ենք ստացել բարձրորակ թռչունների վանդակների, խաղալիքների և սնուցման ապրանքների առաքում, որոնք կատարյալ են ձեր փետրավոր ընկերների համար:",
                    "content": """Բոլոր թռչունների սիրահարներին կոչ ենք անում: Մենք ուրախ ենք հայտարարել մեր նոր պրեմիում թռչունների արտադրանքի գծի ժամանման մասին, որը ներառում է առաջատար արտադրողների գլխավոր որակի պարագաները:

Նոր արտադրանքները ներառում են.

Ընդարձակ թռչնանոցներ.
Մեկ կամ բազմաթիվ թռչունների համար բազմաթիվ չափի տարբերակներ՝ փոշի ծածկված պողպատե կառուցվածքով և հեշտ մուտքի դռներով:

Ինտերակտիվ խաղալիքների հավաքածու.
Խաղալիքներ՝ թռչունների մտավոր խթանում և ֆիզիկական ակտիվություն պահպանելու համար նախագծված:

Գուրման սնուցման գիծ.
Տեսակային կոնկրետ կերի խառնուրդներ, օրգանական համեղություններ և վիտամինային հավելումներ՝ ձևակերպված թռչունների սնուցման մասնագետների կողմից:

Տարբեր տրամագծերի բնական փայտե նստատեղեր.
Ոտքերի առողջությունը խթանելու և արթրիտը կանխելու համար:

Ինչու ընտրել մեր պրեմիում գիծը.

Որակյալ նյութեր. բոլոր արտադրանքները պատրաստված են թռչունների համար անվտանգ, ոչ թունավոր նյութերից:
Փորձագիտական ընտրություն. արտադրանքներ ընտրված են թռչունների անասնաբույժների և փորձառու թռչունների պահապանների կողմից:
Դիմացկունություն. կառուցված է դիմակայելու նույնիսկ ամենաուժեղ կտուցներին և ճանկերին:
Հարստացման կենտրոնացում. նախագծված է խթանելու բնական վարքագիծը և կանխելու ձանձրույթը:

Այցելեք մեր թռչունների բաժինը՝ ամբողջական հավաքածուն տեսնելու համար: Մեր գիտելիքներով անձնակազմը կարող է օգնել ձեզ ընտրել կատարյալ արտադրանքը ձեր կոնկրետ թռչունի տեսակի համար: Հիշեք, երջանիկ թռչունները երջանիկ տերեր են դարձնում:

Սահմանափակ քանակություններ առկա են, այնպես որ արագ գալու համար համոզվեք, որ չեք բաց թողնի այս բացառիկ արտադրանքները:"""
                }
            }
        }
    ]
    
    news_objects = []
    for news_item in news_data:
        translations = news_item.pop("translations")
        news = News(**news_item)
        db.add(news)
        db.flush()
        
        # Add translations
        for lang, trans_data in translations.items():
            translation = NewsTranslation(
                news_id=news.id,
                language=LanguageEnum(lang),
                **trans_data
            )
            db.add(translation)
        
        news_objects.append(news)
    
    db.commit()
    print(f"✅ Created {len(news_data)} news articles with translations")
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
        
        print()
        
        # Seed data in order
        seed_users(db)
        print()
        
        species = seed_animal_species(db)
        print()
        
        categories = seed_categories(db)
        print()
        
        seed_products(db, species, categories)
        print()
        
        seed_news(db)
        print()
        
        print("="*60)
        print("✨ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   • Users: {db.query(User).count()}")
        print(f"   • Animal Species: {db.query(AnimalSpecies).count()}")
        print(f"   • Categories: {db.query(ProductCategory).count()}")
        print(f"   • Products: {db.query(Product).count()}")
        print(f"   • News Articles: {db.query(News).count()}")
        print("\n🔐 Login Credentials:")
        print("   Admin: admin / admin123")
        print("   User: john_doe / password123")
        print("\n🚀 You can now start the server with: python main.py")
        print("   API Documentation: http://localhost:8000/docs\n")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()