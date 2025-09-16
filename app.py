# file: app.py
import os
from functools import wraps
from flask import Flask, jsonify, request, render_template, g
import jwt
from werkzeug.security import check_password_hash, generate_password_hash

# Import services
from services import user_service, account_service, transaction_service, auth_service, biller_service
from database import users_db, accounts_db, transactions_db, billers_db # Make sure billers_db is imported

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-super-secret-key-change-me')

# --- JWT Token Decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            g.current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(*args, **kwargs)
    return decorated

# --- Frontend Route ---
@app.route('/')
def index():
    """Renders the main banking application page."""
    return render_template('index.html')

# --- API Routes ---

# User and Auth Routes
@app.route('/api/register', methods=['POST'])
def register_user():
    """Handles user registration."""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    response, status_code = user_service.create_user(data)
    
    # If user created successfully, create an account for them
    if status_code == 201:
        user_id = response['user']['id']
        account_service.create_account(user_id)
        
    return jsonify(response), status_code

@app.route('/api/login', methods=['POST'])
def login_user():
    """Handles user login and token generation."""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username or password missing'}), 400
        
    response, status_code = auth_service.login(data['username'], data['password'], app.config['SECRET_KEY'])
    return jsonify(response), status_code

@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile():
    """Get profile information for the logged-in user."""
    user_id = g.current_user_id
    response, status_code = user_service.get_user_profile(user_id)
    return jsonify(response), status_code

# Account Routes
@app.route('/api/account', methods=['GET'])
@token_required
def get_account_details():
    """Fetches account details for the logged-in user."""
    user_id = g.current_user_id
    response, status_code = account_service.get_account_by_user_id(user_id)
    return jsonify(response), status_code

# Transaction and Billing Routes
@app.route('/api/transactions', methods=['POST'])
@token_required
def create_transaction_route():
    """Creates a new transfer transaction."""
    data = request.get_json()
    from_user_id = g.current_user_id
    
    if not data or not data.get('to_account_number') or not data.get('amount') or not data.get('description'):
        return jsonify({'message': 'Missing required fields for transaction'}), 400
        
    response, status_code = transaction_service.create_transfer(
        from_user_id,
        data['to_account_number'],
        data['amount'],
        data['description']
    )
    return jsonify(response), status_code

@app.route('/api/transactions', methods=['GET'])
@token_required
def get_transactions():
    """Fetches transaction history for the logged-in user."""
    user_id = g.current_user_id
    response, status_code = transaction_service.get_transactions_by_user_id(user_id)
    return jsonify(response), status_code

@app.route('/api/billers', methods=['GET'])
@token_required
def get_billers_route():
    """Fetches a list of available billers."""
    response, status_code = biller_service.get_all_billers()
    return jsonify(response), status_code
    
@app.route('/api/bill-payment', methods=['POST'])
@token_required
def pay_bill_route():
    """Handles a bill payment transaction."""
    data = request.get_json()
    user_id = g.current_user_id
    if not data or not data.get('biller_id') or not data.get('amount'):
        return jsonify({'message': 'Biller ID and amount are required'}), 400
    
    response, status_code = transaction_service.pay_bill(
        user_id,
        data['biller_id'],
        data['amount']
    )
    return jsonify(response), status_code

@app.route('/api/insights', methods=['GET'])
@token_required
def get_insights():
    """Gets financial insights data for the logged-in user."""
    user_id = g.current_user_id
    response, status_code = transaction_service.get_spending_insights(user_id)
    return jsonify(response), status_code

if __name__ == '__main__':
    # Initialize some mock billers
    biller_service.initialize_billers()
    app.run(host='0.0.0.0', port=5000, debug=True)

