import random
from bson import ObjectId
from database import db_instance

def _get_accounts_collection():
    """Helper to get the accounts collection."""
    return db_instance.get_collection('accounts')

def _serialize_account(account):
    """Converts MongoDB account document to a JSON-serializable format."""
    if account:
        account['_id'] = str(account['_id'])
        account['user_id'] = str(account['user_id'])
    return account

def create_account(user_id):
    """Creates a new bank account for a user."""
    accounts_collection = _get_accounts_collection()
    if not accounts_collection:
        return {'message': 'Database connection error'}, 500
        
    account_number = f"ACC{random.randint(100000000, 999999999)}"
    accounts_collection.insert_one({
        'user_id': ObjectId(user_id),
        'account_number': account_number,
        'balance': 5000.00,  # Starting balance
        'type': 'checking'
    })
    return {'message': 'Account created'}, 201

def get_account_by_user_id(user_id):
    """Retrieves an account by the user's ID."""
    accounts_collection = _get_accounts_collection()
    if not accounts_collection:
        return {'message': 'Database connection error'}, 500

    account = accounts_collection.find_one({'user_id': ObjectId(user_id)})
    if account:
        return {'account': _serialize_account(account)}, 200
    return {'message': 'Account not found'}, 404

