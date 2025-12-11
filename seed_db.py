import random
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Import models from main.py
from db import engine, SessionLocal
from db import Base, User, AnimalSpecies, ProductCategory, Product, News

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base.metadata.create_all(bind=engine)

def get_password_hash(password):
    return pwd_context.hash(password)

def clear_database(db):
    """Clear all existing data"""
    print("🗑️  Clearing existing data...")
    db.query(Product).delete()
    db.query(News).delete()
    db.query(AnimalSpecies).delete()
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
    """Create sample animal species"""
    print("🐾 Creating animal species...")
    
    species_list = [
        {
            "name": "Dogs",
            "description": "Man's best friend. Dogs are loyal, loving, and make wonderful companions for families and individuals alike.",
            "image_url": "https://images.unsplash.com/photo-1587300003388-59208cc962cb"
        },
        {
            "name": "Cats",
            "description": "Independent and graceful pets. Cats are perfect for those who want a loving companion with a bit more independence.",
            "image_url": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba"
        },
        {
            "name": "Birds",
            "description": "Colorful and melodious companions. Birds bring joy with their songs and beautiful plumage.",
            "image_url": "https://images.unsplash.com/photo-1552728089-57bdde30beb3"
        },
        {
            "name": "Fish",
            "description": "Peaceful aquatic pets. Fish create a calming atmosphere and are perfect for smaller living spaces.",
            "image_url": "https://images.unsplash.com/photo-1520990269312-e4e1bb9e0e01"
        },
        {
            "name": "Rabbits",
            "description": "Gentle and social animals. Rabbits are affectionate pets that love to play and cuddle.",
            "image_url": "https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308"
        },
        {
            "name": "Hamsters",
            "description": "Small and adorable rodents. Hamsters are easy to care for and perfect for children learning responsibility.",
            "image_url": "https://images.unsplash.com/photo-1425082661705-1834bfd09dca"
        },
        {
            "name": "Reptiles",
            "description": "Exotic and fascinating creatures. Reptiles offer a unique pet ownership experience for enthusiasts.",
            "image_url": "https://images.unsplash.com/photo-1531466877279-9c0d35b7b8c0"
        },
        {
            "name": "Guinea Pigs",
            "description": "Social and friendly rodents. Guinea pigs are vocal, interactive pets that thrive on companionship.",
            "image_url": "https://images.unsplash.com/photo-1548681528-6a5c45b66b42"
        }
    ]
    
    species_objects = []
    for species_data in species_list:
        species = AnimalSpecies(**species_data)
        db.add(species)
        species_objects.append(species)
    
    db.commit()
    print(f"✅ Created {len(species_list)} animal species")
    return species_objects

def seed_categories(db):
    """Create sample product categories"""
    print("📦 Creating product categories...")
    
    categories_list = [
        {
            "name": "Food",
            "description": "Nutritious and delicious food for all types of pets"
        },
        {
            "name": "Toys",
            "description": "Fun and engaging toys to keep your pets entertained"
        },
        {
            "name": "Accessories",
            "description": "Essential accessories for pet care and comfort"
        },
        {
            "name": "Healthcare",
            "description": "Vitamins, supplements, and healthcare products for pet wellness"
        },
        {
            "name": "Grooming",
            "description": "Grooming tools and products to keep your pet looking their best"
        },
        {
            "name": "Housing",
            "description": "Cages, tanks, beds, and housing solutions for pets"
        },
        {
            "name": "Training",
            "description": "Training aids and tools for pet behavior and obedience"
        }
    ]
    
    category_objects = []
    for category_data in categories_list:
        category = ProductCategory(**category_data)
        db.add(category)
        category_objects.append(category)
    
    db.commit()
    print(f"✅ Created {len(categories_list)} categories")
    return category_objects

def seed_products(db, species_list, categories):
    """Create sample products"""
    print("🛍️  Creating products...")
    
    products_data = [
        # Dog Products
        {"name": "Premium Dog Food - Chicken & Rice", "description": "High-quality dry dog food with real chicken and brown rice. Perfect for adult dogs of all breeds.", "price": 45.99, "stock": 150, "species": "Dogs", "category": "Food", "is_new": True},
        {"name": "Interactive Dog Toy Ball", "description": "Durable rubber ball that bounces unpredictably to keep your dog entertained for hours.", "price": 12.99, "stock": 200, "species": "Dogs", "category": "Toys", "is_new": False},
        {"name": "Adjustable Dog Collar - Large", "description": "Comfortable nylon collar with quick-release buckle. Available in multiple colors.", "price": 15.99, "stock": 100, "species": "Dogs", "category": "Accessories", "is_new": False},
        {"name": "Dog Multivitamin Supplements", "description": "Daily vitamins to support your dog's immune system and overall health.", "price": 24.99, "stock": 80, "species": "Dogs", "category": "Healthcare", "is_new": True},
        {"name": "Professional Dog Grooming Kit", "description": "Complete grooming set with brush, comb, nail clippers, and scissors.", "price": 39.99, "stock": 60, "species": "Dogs", "category": "Grooming", "is_new": False},
        
        # Cat Products
        {"name": "Gourmet Cat Food - Salmon Feast", "description": "Premium wet cat food made with real salmon. Rich in protein and omega-3.", "price": 29.99, "stock": 120, "species": "Cats", "category": "Food", "is_new": False},
        {"name": "Catnip Mouse Toy Set", "description": "Set of 5 colorful mice filled with organic catnip to drive your cat wild.", "price": 9.99, "stock": 180, "species": "Cats", "category": "Toys", "is_new": True},
        {"name": "Automatic Cat Water Fountain", "description": "Circulating water fountain encourages cats to drink more water. Ultra-quiet pump.", "price": 34.99, "stock": 70, "species": "Cats", "category": "Accessories", "is_new": True},
        {"name": "Cat Dental Care Treats", "description": "Crunchy treats that help reduce tartar and freshen breath.", "price": 11.99, "stock": 150, "species": "Cats", "category": "Healthcare", "is_new": False},
        {"name": "Cat Self-Grooming Arch", "description": "Bristle arch allows cats to groom themselves while you watch them enjoy.", "price": 19.99, "stock": 90, "species": "Cats", "category": "Grooming", "is_new": False},
        
        # Bird Products
        {"name": "Premium Bird Seed Mix", "description": "Nutritious blend of seeds, nuts, and dried fruits for all bird species.", "price": 18.99, "stock": 100, "species": "Birds", "category": "Food", "is_new": False},
        {"name": "Bird Swing Perch with Bell", "description": "Natural wood swing with entertaining bell. Perfect for parakeets and small birds.", "price": 8.99, "stock": 140, "species": "Birds", "category": "Toys", "is_new": False},
        {"name": "Stainless Steel Bird Cage", "description": "Spacious cage with multiple perches and feeding stations. Easy to clean.", "price": 89.99, "stock": 35, "species": "Birds", "category": "Housing", "is_new": True},
        
        # Fish Products
        {"name": "Tropical Fish Flakes", "description": "Complete nutrition for all tropical fish. Enhances colors naturally.", "price": 13.99, "stock": 200, "species": "Fish", "category": "Food", "is_new": False},
        {"name": "Aquarium Decoration Castle", "description": "Detailed resin castle provides hiding spots and enhances aquarium aesthetics.", "price": 22.99, "stock": 85, "species": "Fish", "category": "Accessories", "is_new": False},
        {"name": "LED Aquarium Light", "description": "Energy-efficient LED lighting with adjustable color spectrum for plant growth.", "price": 44.99, "stock": 50, "species": "Fish", "category": "Housing", "is_new": True},
        
        # Rabbit Products
        {"name": "Timothy Hay for Rabbits - 5lb", "description": "Fresh, high-fiber timothy hay essential for rabbit dental and digestive health.", "price": 16.99, "stock": 110, "species": "Rabbits", "category": "Food", "is_new": False},
        {"name": "Rabbit Chew Toy Bundle", "description": "Set of natural wood chews to keep rabbit teeth healthy and trim.", "price": 14.99, "stock": 95, "species": "Rabbits", "category": "Toys", "is_new": False},
        {"name": "Large Rabbit Hutch", "description": "Spacious indoor/outdoor hutch with separate sleeping and play areas.", "price": 149.99, "stock": 25, "species": "Rabbits", "category": "Housing", "is_new": True},
        
        # Hamster Products
        {"name": "Hamster Food Pellets", "description": "Balanced nutrition pellets fortified with vitamins and minerals.", "price": 9.99, "stock": 160, "species": "Hamsters", "category": "Food", "is_new": False},
        {"name": "Hamster Exercise Wheel", "description": "Silent spinner wheel for safe and quiet exercise. Multiple sizes available.", "price": 12.99, "stock": 130, "species": "Hamsters", "category": "Toys", "is_new": False},
        {"name": "Deluxe Hamster Cage with Tubes", "description": "Multi-level habitat with colorful tubes and hideouts for exploration.", "price": 59.99, "stock": 40, "species": "Hamsters", "category": "Housing", "is_new": True},
        
        # Reptile Products
        {"name": "Live Crickets (50 count)", "description": "Fresh live crickets, gut-loaded for maximum nutrition. Perfect for reptiles.", "price": 11.99, "stock": 75, "species": "Reptiles", "category": "Food", "is_new": False},
        {"name": "Reptile Heating Lamp", "description": "UVB heating lamp essential for reptile health and metabolism.", "price": 32.99, "stock": 65, "species": "Reptiles", "category": "Accessories", "is_new": False},
        {"name": "Glass Terrarium 20-Gallon", "description": "Front-opening terrarium with screen top. Ideal for most reptile species.", "price": 119.99, "stock": 30, "species": "Reptiles", "category": "Housing", "is_new": True},
        
        # Guinea Pig Products
        {"name": "Guinea Pig Pellet Food", "description": "Vitamin C fortified pellets specially formulated for guinea pigs.", "price": 14.99, "stock": 125, "species": "Guinea Pigs", "category": "Food", "is_new": False},
        {"name": "Guinea Pig Hideout House", "description": "Wooden hideout provides security and privacy for nervous guinea pigs.", "price": 18.99, "stock": 80, "species": "Guinea Pigs", "category": "Accessories", "is_new": False},
        {"name": "Guinea Pig Vitamin C Drops", "description": "Essential vitamin C supplement to prevent scurvy and boost immunity.", "price": 13.99, "stock": 90, "species": "Guinea Pigs", "category": "Healthcare", "is_new": True}
    ]
    
    # Create species and category lookup dictionaries
    species_dict = {s.name: s for s in species_list}
    category_dict = {c.name: c for c in categories}
    
    product_objects = []
    for product_data in products_data:
        species_name = product_data.pop("species")
        category_name = product_data.pop("category")
        
        product = Product(
            **product_data,
            species_id=species_dict[species_name].id,
            category_id=category_dict[category_name].id,
            image_url=f"https://images.unsplash.com/photo-{random.randint(1500000000000, 1700000000000)}"
        )
        db.add(product)
        product_objects.append(product)
    
    db.commit()
    print(f"✅ Created {len(products_data)} products")
    return product_objects

def seed_news(db):
    """Create sample news articles"""
    print("📰 Creating news articles...")
    
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
            "published_at": datetime.now() - timedelta(days=2)
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
            "published_at": datetime.now() - timedelta(days=5)
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
            "published_at": datetime.now() - timedelta(days=7)
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
            "published_at": datetime.now() - timedelta(days=10)
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
            "published_at": datetime.now() - timedelta(days=14)
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
            "published_at": datetime.now() - timedelta(days=18)
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
            "published_at": datetime.now() - timedelta(days=1)
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
            "published_at": datetime.now() - timedelta(days=3)
        }
    ]
    
    news_objects = []
    for news_item in news_data:
        news = News(**news_item)
        db.add(news)
        news_objects.append(news)
    
    db.commit()
    print(f"✅ Created {len(news_data)} news articles")
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
    print(get_password_hash("admin123."))