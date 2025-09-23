import jwt
from functools import wraps
from flask import jsonify, request, g
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get SECRET_KEY from environment variables with a fallback
SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-secure-and-long-secret-key-that-you-should-change')

def token_required(f):
    """Decorator to require a valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            g.current_user_id = data['user_id']
            g.is_admin = data.get('is_admin', False)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except Exception:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if not g.is_admin:
            return jsonify({'message': 'Admin access required!'}), 403
        return f(*args, **kwargs)
    return decorated
