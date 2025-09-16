# file: services/transaction_service.py
import uuid
from datetime import datetime
from database import accounts_db, transactions_db, billers_db
from services.account_service import get_account_by_user_id, get_account_by_number

def _create_transaction_record(from_account, to_account, amount, tx_type, description):
    """Helper function to create and save a transaction record."""
    transaction_id = str(uuid.uuid4())
    new_transaction = {
        'id': transaction_id,
        'from_account': from_account,
        'to_account': to_account,
        'amount': amount,
        'type': tx_type, # e.g., 'Transfer', 'Bill Payment'
        'description': description,
        'timestamp': datetime.utcnow().isoformat()
    }
    transactions_db.append(new_transaction)
    return new_transaction

def create_transfer(from_user_id, to_account_number, amount, description):
    """Processes a transfer between two accounts."""
    try:
        amount = float(amount)
        if amount <= 0:
            return {'message': 'Transfer amount must be positive'}, 400
    except ValueError:
        return {'message': 'Invalid transfer amount'}, 400

    from_account_data, _ = get_account_by_user_id(from_user_id)
    from_account = from_account_data.get('account')
    to_account = get_account_by_number(to_account_number)

    if not from_account: return {'message': 'Sender account not found'}, 404
    if not to_account: return {'message': 'Recipient account not found'}, 404
    if from_account['account_number'] == to_account['account_number']: return {'message': 'Cannot transfer to the same account'}, 400
    if from_account['balance'] < amount: return {'message': 'Insufficient funds'}, 400

    from_account['balance'] -= amount
    to_account['balance'] += amount

    transaction = _create_transaction_record(
        from_account['account_number'],
        to_account['account_number'],
        amount,
        'Transfer',
        description
    )
    
    return {'message': 'Transfer successful', 'transaction': transaction}, 201

def pay_bill(user_id, biller_id, amount):
    """Processes a bill payment."""
    try:
        amount = float(amount)
        if amount <= 0: return {'message': 'Bill amount must be positive'}, 400
    except ValueError: return {'message': 'Invalid bill amount'}, 400

    from_account_data, _ = get_account_by_user_id(user_id)
    from_account = from_account_data.get('account')
    biller = billers_db.get(biller_id)

    if not from_account: return {'message': 'User account not found'}, 404
    if not biller: return {'message': 'Biller not found'}, 404
    if from_account['balance'] < amount: return {'message': 'Insufficient funds'}, 400

    from_account['balance'] -= amount

    transaction = _create_transaction_record(
        from_account['account_number'],
        biller['name'],
        amount,
        biller['category'], # Use biller category for transaction type
        f"Payment to {biller['name']}"
    )
    
    return {'message': 'Bill paid successfully', 'transaction': transaction}, 201

def get_transactions_by_user_id(user_id):
    """Retrieves all transactions for a given user."""
    account_data, _ = get_account_by_user_id(user_id)
    if not account_data or 'account' not in account_data:
        return {'message': 'User account not found'}, 404
    
    user_account_number = account_data.get('account').get('account_number')
    
    user_transactions = [
        t for t in transactions_db 
        if t['from_account'] == user_account_number or t['to_account'] == user_account_number
    ]
    
    return {'transactions': user_transactions}, 200

def get_spending_insights(user_id):
    """Calculates spending insights by category for a user."""
    account_data, _ = get_account_by_user_id(user_id)
    if not account_data: return {'message': 'Account not found'}, 404
    
    user_account_number = account_data.get('account').get('account_number')
    
    spending = {}
    
    user_debits = [t for t in transactions_db if t['from_account'] == user_account_number]
    
    for tx in user_debits:
        category = tx.get('type', 'Uncategorized')
        spending[category] = spending.get(category, 0) + tx['amount']
        
    labels = list(spending.keys())
    data = list(spending.values())
    
    return {'labels': labels, 'data': data}, 200

