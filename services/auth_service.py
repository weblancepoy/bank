# file: services/auth_service.py
# No changes from previous version, file is included for completeness.
import jwt
import datetime
from werkzeug.security import check_password_hash
from db_config import users_collection

def login(username, password, secret_key):
    user = users_collection.find_one({'username': username, 'is_admin': False})
    if not user or not check_password_hash(user['password'], password): return {'message': 'Invalid username or password'}, 401
    if user.get('status') == 'suspended': return {'message': 'Your account has been suspended'}, 403
    token = jwt.encode({'user_id': str(user['_id']), 'is_admin': False, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, secret_key, "HS256")
    users_collection.update_one({'_id': user['_id']}, {'$set': {'last_login': datetime.datetime.utcnow()}})
    return {'token': token, 'username': user['username']}, 200

def admin_login(username, password, secret_key):
    user = users_collection.find_one({'username': username, 'is_admin': True})
    if not user or not check_password_hash(user['password'], password): return {'message': 'Invalid admin credentials'}, 401
    token = jwt.encode({'user_id': str(user['_id']), 'is_admin': True, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)}, secret_key, "HS256")
    users_collection.update_one({'_id': user['_id']}, {'$set': {'last_login': datetime.datetime.utcnow()}})
    return {'token': token, 'username': user['username']}, 200

