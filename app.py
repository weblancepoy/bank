import os
from functools import wraps
from flask import Flask, jsonify, request, render_template, g, Response, send_from_directory
import jwt
from dotenv import load_dotenv
from bson import ObjectId
import datetime

# Load environment variables
load_dotenv()

# Import services and database instance
from database import db_instance
from services import (
    user_service, account_service, transaction_service,
    auth_service, biller_service, chatbot_service, report_service
)
from services.seed_data import seed_initial_data # Import the new seeding function
from services.reports_blueprint import reports_bp # Import reports blueprint

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secure-and-long-secret-key-that-you-should-change')
# Load the Gemini API key from environment variables
app.config['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY')

# Warning if Gemini Key is missing
if not app.config['GEMINI_API_KEY']:
    print("WARNING: GEMINI_API_KEY environment variable not set. Chatbot will have limited functionality.")

# Register blueprints
app.register_blueprint(reports_bp, url_prefix='/api/admin/reports')

# --- Decorators for authentication (Included for completeness, logic assumed correct) ---
def token_required(f):
    """Decorator to require a valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            # We use the key defined in app.config
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"]) 
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

# --- Static File Serving and Root Route ---
@app.route('/')
def index():
    """Serves the main index.html file."""
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    """Serves files from the static directory (e.g., CSS, JS)."""
    return send_from_directory('static', path)

# --- API Routes ---
@app.route('/api/register', methods=['POST'])
def register_user():
    """Endpoint for user registration."""
    data = request.get_json()
    response, status_code = user_service.create_user(data)
    # DELETED: Removed account creation from here. It will now be handled on admin approval.
    return jsonify(response), status_code

@app.route('/api/login', methods=['POST'])
def login():
    """Endpoint for user login (initiates 2FA)."""
    data = request.get_json()
    response, status_code = auth_service.login(data.get('username'), data.get('password'))
    return jsonify(response), status_code

@app.route('/api/login/verify', methods=['POST'])
def verify_login():
    """Endpoint to verify 2FA code."""
    data = request.get_json()
    response, status_code = auth_service.verify_login_code(data.get('user_id'), data.get('code'))
    return jsonify(response), status_code

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Endpoint for admin login."""
    data = request.get_json()
    response, status_code = auth_service.admin_login(data.get('username'), data.get('password'))
    return jsonify(response), status_code

@app.route('/api/account', methods=['GET'])
@token_required
def get_user_account():
    """Get the logged-in user's account details."""
    response, status_code = account_service.get_account_by_user_id(g.current_user_id)
    return jsonify(response), status_code

@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile():
    """Endpoint to get the logged-in user's profile details."""
    response, status_code = user_service.get_user_profile(g.current_user_id)
    return jsonify(response), status_code

@app.route('/api/transactions', methods=['GET'])
@token_required
def get_user_transactions():
    """Get transactions for the logged-in user."""
    response, status_code = transaction_service.get_transactions_by_user_id(g.current_user_id)
    return jsonify(response), status_code

@app.route('/api/transactions', methods=['POST'])
@token_required
def create_transfer():
    """Create a new money transfer transaction."""
    data = request.get_json()
    response, status_code = transaction_service.create_transfer(
        from_user_id=g.current_user_id,
        to_account_number=data.get('to_account_number'),
        amount=data.get('amount'),
        description=data.get('description')
    )
    return jsonify(response), status_code

@app.route('/api/billers', methods=['GET'])
@token_required
def get_billers():
    """Get a list of all available billers."""
    response, status_code = biller_service.get_all_billers()
    return jsonify(response), status_code

@app.route('/api/bill-payment', methods=['POST'])
@token_required
def pay_bill():
    """Pay a bill to a specific biller."""
    data = request.get_json()
    response, status_code = transaction_service.pay_bill(
        user_id=g.current_user_id,
        biller_id=data.get('biller_id'),
        amount=data.get('amount')
    )
    return jsonify(response), status_code

@app.route('/api/deposit', methods=['POST'])
@token_required
def deposit_funds():
    """Endpoint to deposit funds into the user's account."""
    data = request.get_json()
    response, status_code = account_service.deposit(
        user_id=g.current_user_id,
        amount=data.get('amount')
    )
    return jsonify(response), status_code

@app.route('/api/withdraw', methods=['POST'])
@token_required
def withdraw_funds():
    """Endpoint to withdraw funds from the user's account."""
    data = request.get_json()
    response, status_code = account_service.withdraw(
        user_id=g.current_user_id,
        amount=data.get('amount')
    )
    return jsonify(response), status_code

@app.route('/api/insights', methods=['GET'])
@token_required
def get_insights():
    """Get user spending insights."""
    response, status_code = transaction_service.get_spending_insights(g.current_user_id)
    return jsonify(response), status_code

@app.route('/api/chatbot', methods=['POST'])
@token_required
def get_chatbot_response():
    """Get a response from the AI chatbot."""
    data = request.get_json()
    user_message = data.get('message')
    api_key = app.config['GEMINI_API_KEY']
    reply = chatbot_service.get_gemini_response(g.current_user_id, user_message, api_key)
    return jsonify({'reply': reply}), 200

# Admin Routes
@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    """Admin endpoint to get dashboard statistics."""
    response, status_code = report_service.get_dashboard_stats()
    return jsonify(response), status_code

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    """Admin endpoint to get a list of all non-admin users."""
    response, status_code = user_service.get_all_users()
    return jsonify(response), status_code

@app.route('/api/admin/users/<user_id>', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    """Admin endpoint to update a user's status (active/suspended)."""
    data = request.get_json()
    status = data.get('status')
    response, status_code = user_service.update_user_status(user_id, status)
    return jsonify(response), status_code

@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Admin endpoint to delete a user."""
    response, status_code = user_service.delete_user(user_id)
    return jsonify(response), status_code

# --- NEW ADMIN BILLER ROUTES ---
@app.route('/api/admin/billers', methods=['GET'])
@admin_required
def get_admin_billers():
    """Admin endpoint to get all billers."""
    response, status_code = biller_service.get_all_billers()
    return jsonify(response), status_code

@app.route('/api/admin/billers', methods=['POST'])
@admin_required
def create_biller_admin():
    """Admin endpoint to create a new biller."""
    data = request.get_json()
    response, status_code = biller_service.create_biller(
        name=data.get('name'), 
        category=data.get('category')
    )
    return jsonify(response), status_code

@app.route('/api/admin/billers/<biller_id>', methods=['PUT'])
@admin_required
def update_biller_admin(biller_id):
    """Admin endpoint to update an existing biller."""
    data = request.get_json()
    response, status_code = biller_service.update_biller(
        biller_id=biller_id,
        name=data.get('name'),
        category=data.get('category')
    )
    return jsonify(response), status_code

@app.route('/api/admin/billers/<biller_id>', methods=['DELETE'])
@admin_required
def delete_biller_admin(biller_id):
    """Admin endpoint to delete a biller."""
    response, status_code = biller_service.delete_biller(biller_id)
    return jsonify(response), status_code
# --- END NEW ADMIN BILLER ROUTES ---

@app.route('/api/admin/transactions', methods=['GET'])
@admin_required
def get_all_transactions_admin():
    """Admin endpoint to get a list of all transactions."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    response, status_code = transaction_service.get_all_transactions(start_date=start_date, end_date=end_date)
    return jsonify(response), status_code

@app.route('/api/admin/reports/transactions.csv', methods=['GET'])
@admin_required
def download_transactions_report_csv():
    """
    Handles the API request to download a CSV report of all transactions.
    """
    csv_data = report_service.generate_transaction_report_csv()
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=transactions_report.csv"}
    )


# --- Application Runner ---
if __name__ == '__main__':
    with app.app_context():
        # This will create collections and an admin user if they don't exist
        user_service.create_admin_user_if_not_exists()
        biller_service.initialize_billers()
        seed_initial_data() # Call the new function to seed data
    # The debug flag is useful for development as it enables a debugger and auto-reloader
    app.run(host='0.0.0.0', port=5000, debug=True)
