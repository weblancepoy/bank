import random
from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash
from database import db_instance
from . import account_service

def _get_users_collection():
    """Helper to get the users collection."""
    return db_instance.get_collection('users')

def _serialize_user(user):
    """Converts MongoDB user document to a JSON-serializable format, excluding sensitive data."""
    if user:
        user['_id'] = str(user['_id'])
        user['created_at'] = user['created_at'].isoformat()
        if user.get('last_login'):
            user['last_login'] = user['last_login'].isoformat()
        user.pop('password', None)
        user.pop('2fa_code', None) # Ensure 2FA code is not leaked
        user.pop('2fa_code_expires', None) # Ensure 2FA expiry is not leaked
    return user

def create_user(data, created_by_admin=False):
    users_collection = _get_users_collection()
    if users_collection is None:
        return {'message': 'Database connection error'}, 500
    if not all([data.get('username'), data.get('email'), data.get('password')]):
        return {'message': 'Missing required fields'}, 400
    if users_collection.find_one({'username': data['username']}):
        return {'message': 'Username already exists'}, 409
    if users_collection.find_one({'email': data['email']}):
        return {'message': 'Email already registered'}, 409
        
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = {
        'username': data['username'],
        'email': data['email'],
        'password': hashed_password,
        'created_at': datetime.utcnow(),
        'is_admin': False,
        'status': 'pending',  # CHANGED: New users are now 'pending'
        'last_login': None,
        'created_by_admin': created_by_admin
    }
    result = users_collection.insert_one(new_user)
    created_user = users_collection.find_one({'_id': result.inserted_id})
    return {'message': 'User registered successfully', 'user': _serialize_user(created_user)}, 201

def create_user_account(user_id):
    """Helper function to create a bank account for a user."""
    return account_service.create_account(user_id)

def create_admin_user_if_not_exists():
    users_collection = _get_users_collection()
    if users_collection is not None and not users_collection.find_one({'is_admin': True}):
        hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
        users_collection.insert_one({
            'username': 'admin',
            'email': 'admin@bank.com',
            'password': hashed_password,
            'created_at': datetime.utcnow(),
            'is_admin': True,
            'status': 'active',
            'last_login': None,
            'created_by_admin': True
        })
        print("Admin user 'admin' with password 'admin123' created.")

def get_user_profile(user_id):
    """Retrieves a user's profile information."""
    users_collection = _get_users_collection()
    if users_collection is None: 
        return {'message': 'Database error'}, 500
    
    # Ensure user_id is a valid ObjectId before querying
    if not ObjectId.is_valid(user_id):
        return {'message': 'Invalid user ID format'}, 400
        
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    
    if user:
        return {'profile': _serialize_user(user)}, 200
    else:
        return {'message': 'User not found'}, 404

def get_all_users():
    users_collection = _get_users_collection()
    if users_collection is None: return {'message': 'Database error'}, 500
    users = list(users_collection.find({'is_admin': False}))
    return {'users': [_serialize_user(user) for user in users]}, 200

def update_user_status(user_id, status):
    users_collection = _get_users_collection()
    if users_collection is None: return {'message': 'Database error'}, 500
    
    # Check for valid status and user existence
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return {'message': 'User not found'}, 404
        
    if status not in ['active', 'suspended']:
        return {'message': 'Invalid status'}, 400
        
    # If the status is being changed from 'pending' to 'active', create the account
    if user['status'] == 'pending' and status == 'active':
        create_user_account(user_id)

    result = users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'status': status}})
    return ({'message': f'User status updated to {status}'}, 200) if result.matched_count else ({'message': 'User not found'}, 404)

def delete_user(user_id):
    users_collection = _get_users_collection()
    if users_collection is None: return {'message': 'Database error'}, 500
    result = users_collection.delete_one({'_id': ObjectId(user_id)})
    return ({'message': 'User deleted successfully'}, 200) if result.deleted_count else ({'message': 'User not found'}, 404)
