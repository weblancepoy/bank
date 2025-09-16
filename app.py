# file: app.py
import os
from functools import wraps
from flask import Flask, jsonify, request, render_template, g, Response
import jwt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from db_config import db
from services import (
    user_service, account_service, transaction_service, 
    auth_service, biller_service, report_service, chatbot_service
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secure-and-long-secret-key-that-you-should-change')
app.config['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY')

if not app.config['GEMINI_API_KEY']:
    print("WARNING: GEMINI_API_KEY environment variable not set. Chatbot will have limited functionality.")

# --- JWT Token Decorators ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            g.current_user_id = data['user_id']
            g.is_admin = data.get('is_admin', False)
        except Exception:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if not g.is_admin:
            return jsonify({'message': 'Admin access required!'}), 403
        return f(*args, **kwargs)
    return decorated

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

# Auth Routes
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    response, status_code = user_service.create_user(data)
    if status_code == 201:
        user_id = str(response['user']['_id'])
        account_service.create_account(user_id)
    return jsonify(response), status_code

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    return jsonify(auth_service.login(data.get('username'), data.get('password'), app.config['SECRET_KEY']))

@app.route('/api/admin/login', methods=['POST'])
def login_admin():
    data = request.get_json()
    return jsonify(auth_service.admin_login(data.get('username'), data.get('password'), app.config['SECRET_KEY']))

# Chatbot Route
@app.route('/api/chatbot', methods=['POST'])
@token_required
def chatbot_response():
    data = request.get_json()
    user_message = data.get('message')
    if not user_message:
        return jsonify({'reply': 'Please provide a message.'}), 400
    
    api_key = app.config.get('GEMINI_API_KEY')
    ai_response = chatbot_service.get_gemini_response(g.current_user_id, user_message, api_key)
    return jsonify({'reply': ai_response})

# User Routes
@app.route('/api/account', methods=['GET'])
@token_required
def get_account_details():
    return jsonify(account_service.get_account_by_user_id(g.current_user_id))

@app.route('/api/transactions', methods=['GET'])
@token_required
def get_transactions():
    return jsonify(transaction_service.get_transactions_by_user_id(g.current_user_id))

@app.route('/api/transactions', methods=['POST'])
@token_required
def create_transaction_route():
    data = request.get_json()
    return jsonify(transaction_service.create_transfer(g.current_user_id, data.get('to_account_number'), data.get('amount'), data.get('description')))

# Admin Routes
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    return jsonify(user_service.get_all_users())

@app.route('/api/admin/users', methods=['POST'])
@admin_required
def admin_create_user():
    data = request.get_json()
    response, status_code = user_service.create_user(data, created_by_admin=True)
    if status_code == 201:
        user_id = str(response['user']['_id'])
        account_service.create_account(user_id)
    return jsonify(response), status_code
    
@app.route('/api/admin/transactions', methods=['GET'])
@admin_required
def admin_get_transactions():
    return jsonify(transaction_service.get_all_transactions())

@app.route('/api/admin/reports/transactions.csv', methods=['GET'])
@admin_required
def download_transaction_report():
    csv_data = report_service.generate_transaction_report_csv()
    return Response(csv_data, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=transaction_report.csv"})

# ... Other routes for billers, insights, admin stats, etc. remain largely the same ...
# (Included here for completeness but without showing unchanged code)

@app.route('/api/billers', methods=['GET'])
@token_required
def get_billers_route(): return jsonify(biller_service.get_all_billers())
    
@app.route('/api/bill-payment', methods=['POST'])
@token_required
def pay_bill_route(): return jsonify(transaction_service.pay_bill(g.current_user_id, request.json.get('biller_id'), request.json.get('amount')))

@app.route('/api/insights', methods=['GET'])
@token_required
def get_insights(): return jsonify(transaction_service.get_spending_insights(g.current_user_id))

@app.route('/api/admin/users/<user_id>', methods=['PUT'])
@admin_required
def update_user_status(user_id): return jsonify(user_service.update_user_status(user_id, request.json.get('status')))

@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user_route(user_id): return jsonify(user_service.delete_user(user_id))
    
@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_admin_stats(): return jsonify(report_service.get_dashboard_stats())

@app.route('/api/admin/transactions/<tx_id>', methods=['PUT'])
@admin_required
def admin_update_transaction(tx_id): return jsonify(transaction_service.update_transaction(tx_id, request.json))

@app.route('/api/admin/transactions/<tx_id>', methods=['DELETE'])
@admin_required
def admin_delete_transaction(tx_id): return jsonify(transaction_service.delete_transaction(tx_id))


if __name__ == '__main__':
    with app.app_context():
        user_service.create_admin_user_if_not_exists()
        biller_service.initialize_billers()
    app.run(host='0.0.0.0', port=5000, debug=True)

