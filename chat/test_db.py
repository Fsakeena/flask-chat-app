from app import db, User
from werkzeug.security import generate_password_hash

new_user = User(
    username="testuser",
    email="test@example.com",
    password=generate_password_hash("password123")
)

with db.session.begin():
    db.session.add(new_user)

print("Inserted test user.")
