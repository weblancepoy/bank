from datetime import datetime
from bson import ObjectId
from database import db_instance

def _get_collections():
    """Helper to get all required collections."""
    transactions = db_instance.get_collection('transactions')
    accounts = db_instance.get_collection('accounts')
    billers = db_instance.get_collection('billers')
    return transactions, accounts, billers

def _serialize_transaction(tx):
    """Converts MongoDB transaction document to a JSON-serializable format."""
    if tx:
        tx['_id'] = str(tx['_id'])
        if 'timestamp' in tx and isinstance(tx['timestamp'], datetime):
            tx['timestamp'] = tx['timestamp'].isoformat()
    return tx

def create_transfer(from_user_id, to_account_number, amount, description):
    """Creates a new transfer transaction between two accounts."""
    transactions_collection, accounts_collection, _ = _get_collections()
    if not all([transactions_collection, accounts_collection]):
        return {'message': 'Database connection error'}, 500

    try: amount = float(amount)
    except (ValueError, TypeError): return {'message': 'Invalid amount'}, 400
    if amount <= 0: return {'message': 'Amount must be positive'}, 400
    
    from_account = accounts_collection.find_one({'user_id': ObjectId(from_user_id)})
    to_account = accounts_collection.find_one({'account_number': to_account_number})

    if not from_account: return {'message': 'Sender account not found'}, 404
    if not to_account: return {'message': 'Recipient account not found'}, 404
    if from_account['balance'] < amount: return {'message': 'Insufficient funds'}, 400
    
    with db_instance.client.start_session() as session:
        with session.in_transaction():
            accounts_collection.update_one({'_id': from_account['_id']}, {'$inc': {'balance': -amount}}, session=session)
            accounts_collection.update_one({'_id': to_account['_id']}, {'$inc': {'balance': amount}}, session=session)
            transactions_collection.insert_one({
                'from_account': from_account['account_number'], 
                'to_account': to_account['account_number'], 
                'amount': amount, 
                'type': 'Transfer', 
                'description': description or "Sent Money", 
                'timestamp': datetime.utcnow()
            }, session=session)
    return {'message': 'Transfer successful'}, 201

def pay_bill(user_id, biller_id, amount):
    """Creates a new bill payment transaction."""
    transactions_collection, accounts_collection, billers_collection = _get_collections()
    if not all([transactions_collection, accounts_collection, billers_collection]):
        return {'message': 'Database connection error'}, 500

    try: amount = float(amount)
    except (ValueError, TypeError): return {'message': 'Invalid amount'}, 400
    if amount <= 0: return {'message': 'Amount must be positive'}, 400
    
    from_account = accounts_collection.find_one({'user_id': ObjectId(user_id)})
    biller = billers_collection.find_one({'_id': ObjectId(biller_id)})

    if not from_account: return {'message': 'User account not found'}, 404
    if not biller: return {'message': 'Biller not found'}, 404
    if from_account['balance'] < amount: return {'message': 'Insufficient funds'}, 400
    
    with db_instance.client.start_session() as session:
        with session.in_transaction():
            accounts_collection.update_one({'_id': from_account['_id']}, {'$inc': {'balance': -amount}}, session=session)
            transactions_collection.insert_one({
                'from_account': from_account['account_number'], 
                'to_account': biller['name'], 
                'amount': amount, 
                'type': biller['category'], 
                'description': f"Payment to {biller['name']}", 
                'timestamp': datetime.utcnow()
            }, session=session)
    return {'message': 'Bill paid successfully'}, 201

def get_transactions_by_user_id(user_id):
    """Retrieves all transactions for a specific user."""
    transactions_collection, accounts_collection, _ = _get_collections()
    if not all([transactions_collection, accounts_collection]):
        return {'message': 'Database connection error'}, 500
        
    account = accounts_collection.find_one({'user_id': ObjectId(user_id)})
    if not account: return {'message': 'Account not found'}, 404
    
    user_transactions = list(transactions_collection.find({
        '$or': [{'from_account': account['account_number']}, {'to_account': account['account_number']}]
    }).sort('timestamp', -1))
    
    return {'transactions': [_serialize_transaction(tx) for tx in user_transactions]}, 200

def get_spending_insights(user_id):
    """Aggregates spending data by category for a user."""
    transactions_collection, accounts_collection, _ = _get_collections()
    if not all([transactions_collection, accounts_collection]):
        return {'message': 'Database connection error'}, 500

    account = accounts_collection.find_one({'user_id': ObjectId(user_id)})
    if not account: return {'message': 'Account not found'}, 404

    pipeline = [
        {'$match': {'from_account': account['account_number']}},
        {'$group': {'_id': '$type', 'totalAmount': {'$sum': '$amount'}}},
        {'$sort': {'totalAmount': -1}}
    ]
    results = list(transactions_collection.aggregate(pipeline))
    return {'labels': [r['_id'] for r in results], 'data': [r['totalAmount'] for r in results]}, 200

def get_all_transactions():
    """Retrieves all transactions (Admin)."""
    transactions_collection, _, _ = _get_collections()
    if not transactions_collection:
        return {'message': 'Database connection error'}, 500
        
    transactions = list(transactions_collection.find({}).sort('timestamp', -1))
    return {'transactions': [_serialize_transaction(tx) for tx in transactions]}, 200

def update_transaction(tx_id, data):
    """Updates a transaction's description or type (Admin)."""
    transactions_collection, _, _ = _get_collections()
    if not transactions_collection:
        return {'message': 'Database connection error'}, 500

    update_data = {k: v for k, v in data.items() if k in ['description', 'type']}
    if not update_data: return {'message': 'No valid fields to update'}, 400

    result = transactions_collection.update_one({'_id': ObjectId(tx_id)}, {'$set': update_data})
    return ({'message': 'Transaction updated'}, 200) if result.matched_count else ({'message': 'Transaction not found'}, 404)

def delete_transaction(tx_id):
    """Deletes a transaction (Admin)."""
    transactions_collection, _, _ = _get_collections()
    if not transactions_collection:
        return {'message': 'Database connection error'}, 500
        
    result = transactions_collection.delete_one({'_id': ObjectId(tx_id)})
    return ({'message': 'Transaction deleted'}, 200) if result.deleted_count else ({'message': 'Transaction not found'}, 404)

