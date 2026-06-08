import mysql.connector
from faker import Faker
from werkzeug.security import generate_password_hash

fake = Faker()

db = mysql.connector.connect(
    host="gateway01.us-east-1.prod.aws.tidbcloud.com",
    port=4000,
    user="nqdjDChayqizKrd.root",
    password="VqpHxbMv82DIDwzS",
    database="test",
    ssl_verify_identity=False,
    ssl_verify_cert=False
)


cursor = db.cursor(dictionary=True)

for i in range(1000):

    fullname = fake.name()

    email = f"user{i}@example.com"

    password = generate_password_hash("123456")

    cursor.execute("""
        INSERT INTO users (fullname, email, password)
        VALUES (%s, %s, %s)
    """, (fullname, email, password))

db.commit()

print("1000 users inserted successfully!")

cursor.close()
db.close()