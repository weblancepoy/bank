# file: services/user_service.py
import uuid
from werkzeug.security import generate_password_hash
from database import users_db

def create_user(data):
    """Creates a new user and stores it in the users_db."""
    username = data.get('username')
    email = data.get('email')
    
    if any(u['username'] == username for u in users_db.values()):
        return {'message': 'Username already exists'}, 409
    if any(u['email'] == email for u in users_db.values()):
        return {'message': 'Email already registered'}, 409

    hashed_password = generate_password_hash(data.get('password'), method='pbkdf2:sha256')
    
    user_id = str(uuid.uuid4())
    
    new_user = {
        'id': user_id,
        'username': username,
        'email': email,
        'password': hashed_password,
        'created_at': __import__('datetime').datetime.utcnow().isoformat()
    }
    
    users_db[user_id] = new_user
    
    user_info = {k: v for k, v in new_user.items() if k != 'password'}
    
    return {'message': 'User registered successfully', 'user': user_info}, 201

def get_user_by_username(username):
    """Retrieves a user by their username."""
    for user in users_db.values():
        if user['username'] == username:
            return user
    return None

def get_user_profile(user_id):
    """Retrieves a user's profile information by ID, excluding sensitive data."""
    user = users_db.get(user_id)
    if user:
        profile_info = {
            'id': user.get('id'),
            'username': user.get('username'),
            'email': user.get('email'),
            'member_since': user.get('created_at')
        }
        return {'profile': profile_info}, 200
    return {'message': 'User not found'}, 404

