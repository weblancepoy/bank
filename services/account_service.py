# file: services/account_service.py
import uuid
import random
from database import accounts_db

def create_account(user_id):
    """Creates a new bank account for a user."""
    account_id = str(uuid.uuid4())
    account_number = f"ACC{random.randint(100000000, 999999999)}"
    
    new_account = {
        'id': account_id,
        'user_id': user_id,
        'account_number': account_number,
        'balance': 5000.00  # Give a more generous starting balance
    }
    
    accounts_db[account_id] = new_account
    return {'message': 'Account created successfully', 'account': new_account}, 201

def get_account_by_user_id(user_id):
    """Retrieves an account by user ID."""
    for account in accounts_db.values():
        if account['user_id'] == user_id:
            return {'account': account}, 200
    return {'message': 'Account not found'}, 404
    
def get_account_by_number(account_number):
    """Retrieves an account by account number."""
    for account in accounts_db.values():
        if account['account_number'] == account_number:
            return account
    return None

