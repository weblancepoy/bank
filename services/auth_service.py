import jwt
import datetime
import random
import os
from werkzeug.security import check_password_hash, generate_password_hash
from bson import ObjectId
from database import db_instance
from . import email_service

# Get SECRET_KEY from environment variables with a fallback
SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-secure-and-long-secret-key-that-you-should-change')

def _get_users_collection():
    """Helper to safely get the users collection."""
    return db_instance.get_collection('users')

def generate_2fa_code(user_id):
    """Generates and stores a 6-digit 2FA code for a user."""
    users_collection = _get_users_collection()
    if users_collection is None:
        return None
    code = str(random.randint(100000, 999999))
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    users_collection.update_one(
        {'_id': user_id},
        {'$set': {'2fa_code': code, '2fa_code_expires': expiry}}
    )
    return code

def verify_2fa_code(user_id, code):
    """Verifies a user's 2FA code."""
    users_collection = _get_users_collection()
    if users_collection is None:
        return False
    user = users_collection.find_one({'_id': user_id, '2fa_code': code})
    if user and user.get('2fa_code_expires', datetime.datetime.min) > datetime.datetime.utcnow():
        # Clear the code after successful verification
        users_collection.update_one(
            {'_id': user['_id']},
            {'$unset': {'2fa_code': "", '2fa_code_expires': ""}}
        )
        return True
    return False

def login(username, password):
    """Handles user login, including 2FA code generation and sending."""
    try:
        users_collection = _get_users_collection()
        if users_collection is None:
            return {'message': 'Database connection error'}, 500

        user = users_collection.find_one({'username': username, 'is_admin': False})

        if not user or not check_password_hash(user.get('password', ''), password):
            return {'message': 'Invalid username or password'}, 401
        
        if user.get('status') == 'suspended':
            return {'message': 'Your account has been suspended'}, 403
        if user.get('status') == 'pending':
            return {'message': 'Your account is pending admin approval'}, 403
        
        code = generate_2fa_code(user['_id'])
        if code is None:
            return {'message': 'Could not generate 2FA code.'}, 500

        email_sent = email_service.send_2fa_code(user['email'], code)
        if not email_sent:
            return {'message': 'Failed to send 2FA code. Please check server logs.'}, 500
        
        return {'message': '2FA code sent to your email', 'user_id': str(user['_id'])}, 200
    except Exception as e:
        print(f"ERROR in login service: {e}")
        return {'message': 'An internal server error occurred.'}, 500

def verify_login_code(user_id, code):
    """Verifies a 2FA code and issues a JWT token."""
    users_collection = _get_users_collection()
    if users_collection is None:
        return {'message': 'Database connection error'}, 500
    
    if verify_2fa_code(ObjectId(user_id), code):
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        token = jwt.encode({
            'user_id': str(user['_id']),
            'is_admin': user['is_admin'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, "HS256")
        
        users_collection.update_one({'_id': user['_id']}, {'$set': {'last_login': datetime.datetime.utcnow()}})

        return {'message': 'Login successful!', 'token': token, 'username': user['username']}, 200
    
    return {'message': 'Invalid or expired 2FA code.'}, 401

def admin_login(username, password):
    """Handles admin login with robust error handling."""
    try:
        users_collection = _get_users_collection()
        if users_collection is None:
            return {'message': 'Database connection error'}, 500

        user = users_collection.find_one({'username': username, 'is_admin': True})

        if not user or not check_password_hash(user.get('password', ''), password):
            return {'message': 'Invalid admin credentials'}, 401
        
        token = jwt.encode({
            'user_id': str(user['_id']), 
            'is_admin': True, 
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        }, SECRET_KEY, "HS256")
        
        users_collection.update_one({'_id': user['_id']}, {'$set': {'last_login': datetime.datetime.utcnow()}})
        
        return {'token': token, 'username': user['username']}, 200
    except Exception as e:
        print(f"ERROR in admin_login service: {e}")
        return {'message': 'An internal server error occurred.'}, 500
