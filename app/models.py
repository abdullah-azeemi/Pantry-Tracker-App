from app import db

def get_user_by_email(email):
    return db.users.find_one({"email": email})

def create_user(email, password_hash):
    user_id = db.users.insert_one({"email": email, "password": password_hash}).inserted_id
    return user_id
