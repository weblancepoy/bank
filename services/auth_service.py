# file: services/auth_service.py
import jwt
import datetime
from werkzeug.security import check_password_hash
from services.user_service import get_user_by_username

def login(username, password, secret_key):
    """Authenticates a user and returns a JWT token."""
    user = get_user_by_username(username)
    
    if not user or not check_password_hash(user['password'], password):
        return {'message': 'Invalid username or password'}, 401
        
    token = jwt.encode({
        'user_id': user['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, secret_key, "HS256")
    
    return {'token': token, 'user_id': user['id'], 'username': user['username']}, 200

