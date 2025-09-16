# file: services/user_service.py
# No changes from previous version, file is included for completeness.
from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash
from db_config import users_collection

def _serialize_user(user):
    if user:
        user['_id'] = str(user['_id'])
        user['created_at'] = user['created_at'].isoformat()
        if user.get('last_login'): user['last_login'] = user['last_login'].isoformat()
        user.pop('password', None)
    return user

def create_user(data, created_by_admin=False):
    if not all([data.get('username'), data.get('email'), data.get('password')]): return {'message': 'Missing required fields'}, 400
    if users_collection.find_one({'username': data['username']}): return {'message': 'Username already exists'}, 409
    if users_collection.find_one({'email': data['email']}): return {'message': 'Email already registered'}, 409
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = {'username': data['username'], 'email': data['email'], 'password': hashed_password, 'created_at': datetime.utcnow(), 'is_admin': False, 'status': 'active', 'last_login': None, 'created_by_admin': created_by_admin}
    result = users_collection.insert_one(new_user)
    created_user = users_collection.find_one({'_id': result.inserted_id})
    return {'message': 'User registered successfully', 'user': _serialize_user(created_user)}, 201

def create_admin_user_if_not_exists():
    if not users_collection.find_one({'is_admin': True}):
        hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
        users_collection.insert_one({'username': 'admin', 'email': 'admin@bank.com', 'password': hashed_password, 'created_at': datetime.utcnow(), 'is_admin': True, 'status': 'active', 'last_login': None, 'created_by_admin': True})
        print("Admin user 'admin' with password 'admin123' created.")

def get_user_profile(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    return {'profile': _serialize_user(user)} if user else ({'message': 'User not found'}, 404)

def get_all_users():
    users = list(users_collection.find({'is_admin': False}))
    return {'users': [_serialize_user(user) for user in users]}

def update_user_status(user_id, status):
    if status not in ['active', 'suspended']: return {'message': 'Invalid status'}, 400
    result = users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'status': status}})
    return ({'message': f'User status updated to {status}'}, 200) if result.matched_count else ({'message': 'User not found'}, 404)

def delete_user(user_id):
    result = users_collection.delete_one({'_id': ObjectId(user_id)})
    return ({'message': 'User deleted successfully'}, 200) if result.deleted_count else ({'message': 'User not found'}, 404)

