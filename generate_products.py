import mysql.connector
import random

# DATABASE CONNECTION
db = mysql.connector.connect(
    host="gateway01.us-east-1.prod.aws.tidbcloud.com",
    port=4000,
    user="nqdjDChayqizKrd.root",
    password="VqpHxbMv82DIDwzS",
    database="test",
    ssl_verify_identity=False,
    ssl_verify_cert=False
)

cursor = db.cursor()

# Automatically fetch categories from DB
cursor.execute("SELECT id, name FROM categories")
categories = {name: cid for cid, name in cursor.fetchall()}

# Product name parts
adjectives = ["Premium","Ultra","Smart","Elite","Luxury","Modern","Classic","Advanced","Pro","Eco"]

category_items = {
    "Fashion": ["T-Shirt","Hoodie","Jeans","Jacket","Shirt","Polo","Sweater","Blazer","Shorts","Pants"],
    "Electronics": ["Laptop","Mouse","Keyboard","Monitor","Speaker","Headphone","Earbuds","Webcam","Router","Tablet"],
    "Shoes": ["Running Shoes","Sneakers","Boots","Sandals","Loafers","Sports Shoes","Canvas Shoes","Slippers"],
    "Accessories": ["Watch","Bag","Wallet","Belt","Sunglasses","Cap","Bracelet","Necklace","Ring","Backpack"],
    "Gaming": ["Gaming Mouse","Gaming Keyboard","Controller","Gaming Chair","Gaming Headset","Microphone","Mouse Pad","Joystick","RGB Fan","Webcam"],
    "Beauty": ["Perfume","Lipstick","Face Wash","Moisturizer","Shampoo","Conditioner","Body Spray","Face Cream","Serum","Beauty Kit"]
}

# Insert 160 products per category
for cat_name, cat_id in categories.items():
    for i in range(160):
        name = f"{random.choice(adjectives)} {random.choice(category_items[cat_name])} {random.randint(1000,99999)}"
        price = round(random.uniform(10, 1000), 2)
        description = f"High quality {name}. Best product from our {cat_name} collection."
        image = f"https://picsum.photos/500/500?random={random.randint(1,100000)}"

        cursor.execute("""
            INSERT INTO products (name, price, image, description, category_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, price, image, description, cat_id))

db.commit()
cursor.close()
db.close()

print("960 products inserted successfully!")