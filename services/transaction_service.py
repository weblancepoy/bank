# file: services/transaction_service.py
# No changes from previous version, file is included for completeness.
from datetime import datetime
from bson import ObjectId
from db_config import db, transactions_collection, accounts_collection, billers_collection

def _serialize_transaction(tx):
    if tx:
        tx['_id'] = str(tx['_id'])
        tx['timestamp'] = tx['timestamp'].isoformat()
    return tx

def create_transfer(from_user_id, to_account_number, amount, description):
    try: amount = float(amount)
    except (ValueError, TypeError): return {'message': 'Invalid amount'}, 400
    if amount <= 0: return {'message': 'Amount must be positive'}, 400
    from_account = accounts_collection.find_one({'user_id': ObjectId(from_user_id)})
    to_account = accounts_collection.find_one({'account_number': to_account_number})
    if not from_account: return {'message': 'Sender account not found'}, 404
    if not to_account: return {'message': 'Recipient account not found'}, 404
    if from_account['balance'] < amount: return {'message': 'Insufficient funds'}, 400
    with db.client.start_session() as session:
        with session.in_transaction():
            accounts_collection.update_one({'_id': from_account['_id']}, {'$inc': {'balance': -amount}}, session=session)
            accounts_collection.update_one({'_id': to_account['_id']}, {'$inc': {'balance': amount}}, session=session)
            transactions_collection.insert_one({'from_account': from_account['account_number'], 'to_account': to_account['account_number'], 'amount': amount, 'type': 'Transfer', 'description': description or "Sent Money", 'timestamp': datetime.utcnow()}, session=session)
    return {'message': 'Transfer successful'}, 201

def pay_bill(user_id, biller_id, amount):
    try: amount = float(amount)
    except (ValueError, TypeError): return {'message': 'Invalid amount'}, 400
    if amount <= 0: return {'message': 'Amount must be positive'}, 400
    from_account = accounts_collection.find_one({'user_id': ObjectId(user_id)})
    biller = billers_collection.find_one({'_id': ObjectId(biller_id)})
    if not from_account: return {'message': 'User account not found'}, 404
    if not biller: return {'message': 'Biller not found'}, 404
    if from_account['balance'] < amount: return {'message': 'Insufficient funds'}, 400
    with db.client.start_session() as session:
        with session.in_transaction():
            accounts_collection.update_one({'_id': from_account['_id']}, {'$inc': {'balance': -amount}}, session=session)
            transactions_collection.insert_one({'from_account': from_account['account_number'], 'to_account': biller['name'], 'amount': amount, 'type': biller['category'], 'description': f"Payment to {biller['name']}", 'timestamp': datetime.utcnow()}, session=session)
    return {'message': 'Bill paid successfully'}, 201

def get_transactions_by_user_id(user_id):
    account = accounts_collection.find_one({'user_id': ObjectId(user_id)})
    if not account: return {'message': 'Account not found'}, 404
    user_transactions = list(transactions_collection.find({'$or': [{'from_account': account['account_number']}, {'to_account': account['account_number']}]}).sort('timestamp', -1))
    return {'transactions': [_serialize_transaction(tx) for tx in user_transactions]}

def get_spending_insights(user_id):
    account = accounts_collection.find_one({'user_id': ObjectId(user_id)})
    if not account: return {'message': 'Account not found'}, 404
    pipeline = [{'$match': {'from_account': account['account_number']}}, {'$group': {'_id': '$type', 'totalAmount': {'$sum': '$amount'}}}, {'$sort': {'totalAmount': -1}}]
    results = list(transactions_collection.aggregate(pipeline))
    return {'labels': [r['_id'] for r in results], 'data': [r['totalAmount'] for r in results]}

def get_all_transactions():
    transactions = list(transactions_collection.find({}).sort('timestamp', -1))
    return {'transactions': [_serialize_transaction(tx) for tx in transactions]}

def update_transaction(tx_id, data):
    update_data = {k: v for k, v in data.items() if k in ['description', 'type']}
    if not update_data: return {'message': 'No valid fields to update'}, 400
    result = transactions_collection.update_one({'_id': ObjectId(tx_id)}, {'$set': update_data})
    return ({'message': 'Transaction updated'}, 200) if result.matched_count else ({'message': 'Transaction not found'}, 404)

def delete_transaction(tx_id):
    result = transactions_collection.delete_one({'_id': ObjectId(tx_id)})
    return ({'message': 'Transaction deleted'}, 200) if result.deleted_count else ({'message': 'Transaction not found'}, 404)

