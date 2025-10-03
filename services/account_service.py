import random
from bson import ObjectId
from database import db_instance
from services.transaction_service import record_transaction

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
    if accounts_collection is None:
        return {'message': 'Database connection error'}, 500
        
    account_number = f"ACC{random.randint(100000000, 999999999)}"
    accounts_collection.insert_one({
        'user_id': ObjectId(user_id),
        'account_number': account_number,
        'balance': 0.00,  # CHANGED: Starting balance is now 0.00
        'type': 'checking'
    })
    return {'message': 'Account created'}, 201

def get_account_by_user_id(user_id):
    """Retrieves an account by the user's ID."""
    accounts_collection = _get_accounts_collection()
    if accounts_collection is None:
        return {'message': 'Database connection error'}, 500

    account = accounts_collection.find_one({'user_id': ObjectId(user_id)})
    if account:
        return {'account': _serialize_account(account)}, 200
    return {'message': 'Account not found'}, 404

def deposit(user_id, amount):
    """Deposits funds into a user's account."""
    accounts_collection = _get_accounts_collection()
    if accounts_collection is None:
        return {'message': 'Database connection error'}, 500
    
    try:
        amount = float(amount)
        if amount <= 0:
            return {'message': 'Amount must be positive'}, 400
    except (ValueError, TypeError):
        return {'message': 'Invalid amount'}, 400

    account = accounts_collection.find_one({'user_id': ObjectId(user_id)})
    if not account:
        return {'message': 'User account not found'}, 404

    # These operations are now separate and do not require a session
    accounts_collection.update_one(
        {'user_id': ObjectId(user_id)},
        {'$inc': {'balance': amount}}
    )

    # Record transaction separately
    record_transaction(
        account_number=account['account_number'],
        amount=amount,
        type='Deposit',
        description='Online Deposit',
        session=None  # We pass None as there is no session
    )

    return {'message': 'Deposit successful'}, 200

def withdraw(user_id, amount):
    """Withdraws funds from a user's account."""
    accounts_collection = _get_accounts_collection()
    if accounts_collection is None:
        return {'message': 'Database connection error'}, 500

    try:
        amount = float(amount)
        if amount <= 0:
            return {'message': 'Amount must be positive'}, 400
    except (ValueError, TypeError):
        return {'message': 'Invalid amount'}, 400
    
    account = accounts_collection.find_one({'user_id': ObjectId(user_id)})
    if not account:
        return {'message': 'User account not found'}, 404
    
    if account['balance'] < amount:
        return {'message': 'Insufficient funds'}, 400
    
    # These operations are now separate and do not require a session
    accounts_collection.update_one(
        {'user_id': ObjectId(user_id)},
        {'$inc': {'balance': -amount}}
    )
    
    # Record transaction separately
    record_transaction(
        account_number=account['account_number'],
        amount=amount,
        type='Withdrawal',
        description='Online Withdrawal',
        session=None  # We pass None as there is no session
    )

    return {'message': 'Withdrawal successful'}, 200
