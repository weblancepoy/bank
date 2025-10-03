import random
from datetime import datetime, date, timedelta
from bson import ObjectId
from werkzeug.security import generate_password_hash
from database import db_instance
import csv
import io

def _get_collections():
    """Helper to get all required collections."""
    transactions = db_instance.get_collection('transactions')
    accounts = db_instance.get_collection('accounts')
    billers = db_instance.get_collection('billers')
    # Add a check to log if any collection is not found
    if transactions is None or accounts is None or billers is None:
        print("ERROR: A database collection could not be retrieved. Please check MongoDB connection and ensure collections exist.")
        # Return tuple with None for collections if any are missing
        return transactions, accounts, billers 
    return transactions, accounts, billers

def _serialize_transaction(tx):
    """Converts MongoDB transaction document to a JSON-serializable format."""
    if tx:
        tx['_id'] = str(tx['_id'])
        if 'timestamp' in tx and isinstance(tx['timestamp'], datetime):
            tx['timestamp'] = tx['timestamp'].isoformat()
    return tx

def create_transfer(from_user_id, to_account_number, amount, description):
    """
    Creates a new money transfer transaction between two accounts.
    NOTE: This function uses a MongoDB session for ACID compliance.
    Ensure your MongoDB instance is a replica set to support transactions.
    """
    transactions_collection, accounts_collection, _ = _get_collections()
    if transactions_collection is None or accounts_collection is None:
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
        try:
            session.start_transaction()
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
            session.commit_transaction()
        except Exception as e:
            session.abort_transaction()
            print(f"ERROR: Transaction failed. Details: {e}")
            return {'message': 'Transaction failed. Please try again.'}, 500
            
    return {'message': 'Transfer successful'}, 201

def pay_bill(user_id, biller_id, amount):
    """
    Creates a new bill payment transaction.
    NOTE: This function uses a MongoDB session for ACID compliance.
    Ensure your MongoDB instance is a replica set to support transactions.
    """
    transactions_collection, accounts_collection, billers_collection = _get_collections()
    if transactions_collection is None or accounts_collection is None or billers_collection is None:
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
        try:
            session.start_transaction()
            accounts_collection.update_one({'_id': from_account['_id']}, {'$inc': {'balance': -amount}}, session=session)
            transactions_collection.insert_one({
                'from_account': from_account['account_number'], 
                'to_account': biller['name'], 
                'amount': amount, 
                'type': biller['category'], 
                'description': f"Payment to {biller['name']}", 
                'timestamp': datetime.utcnow()
            }, session=session)
            session.commit_transaction()
        except Exception as e:
            session.abort_transaction()
            print(f"ERROR: Transaction failed. Details: {e}")
            return {'message': 'Transaction failed. Please try again.'}, 500
    return {'message': 'Bill paid successfully'}, 201

def record_transaction(account_number, amount, type, description, session=None):
    """Creates a transaction record for a single account within a session."""
    transactions_collection, _, _ = _get_collections()
    if transactions_collection is None:
        # Note: This return won't be hit if the caller uses a session correctly.
        return {'message': 'Database connection error'}, 500
    
    # FIX: Ensure all mandatory fields are present even for single records
    new_tx = {
        'from_account': account_number if type == 'Withdrawal' else 'N/A',
        'to_account': account_number if type == 'Deposit' else 'N/A',
        'amount': amount,
        'type': type,
        'description': description,
        'timestamp': datetime.utcnow()
    }
    
    if session:
        transactions_collection.insert_one(new_tx, session=session)
    else:
        transactions_collection.insert_one(new_tx)
        
    return {'message': 'Transaction recorded successfully'}, 201

def get_transactions_by_user_id(user_id):
    """Retrieves all transactions for a specific user."""
    transactions_collection, accounts_collection, _ = _get_collections()
    if transactions_collection is None or accounts_collection is None:
        return {'message': 'Database connection error'}, 500
        
    account = accounts_collection.find_one({'user_id': ObjectId(user_id)})
    if not account: return {'message': 'Account not found'}, 404
    
    user_transactions = list(transactions_collection.find({
        '$or': [{'from_account': account['account_number']}, {'to_account': account['account_number']}]
    }).sort('timestamp', -1))
    
    # FIX: Ensure serialization is applied to the list of transactions
    serialized_transactions = [_serialize_transaction(tx) for tx in user_transactions]
    
    return {'transactions': serialized_transactions}, 200

def get_all_transactions(start_date=None, end_date=None):
    """
    Retrieves all transactions from the database, with optional date filtering.
    This function is primarily used by the Admin panel and for report generation.
    """
    transactions_collection, _, _ = _get_collections()
    if transactions_collection is None:
        return {'message': 'Database connection error'}, 500

    query = {}
    date_filter = {}

    try:
        if start_date:
            # Convert start_date string (ISO or YYYY-MM-DD) to datetime object (start of the day)
            if 'T' in start_date: # Handle ISO format
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            else: # Handle YYYY-MM-DD format (set to start of the day UTC)
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=None)
            date_filter['$gte'] = start_dt

        if end_date:
            # Convert end_date string (ISO or YYYY-MM-DD) to datetime object (end of the day)
            if 'T' in end_date: # Handle ISO format
                 end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else: # Handle YYYY-MM-DD format (set to end of the day UTC)
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                # Add one day and set time to 00:00:00 to represent the end of the specified day
                end_dt = (end_dt + timedelta(days=1)).replace(tzinfo=None)
                date_filter['$lt'] = end_dt 

    except ValueError as e:
        return {'message': f'Invalid date format provided: {e}'}, 400
    except Exception as e:
        print(f"ERROR during date parsing in get_all_transactions: {e}")
        return {'message': 'An unexpected error occurred during date parsing.'}, 500

    if date_filter:
        query['timestamp'] = date_filter
    
    # Fetch and sort all transactions
    all_transactions = list(transactions_collection.find(query).sort('timestamp', -1))

    return {'transactions': [_serialize_transaction(tx) for tx in all_transactions]}, 200

def get_spending_insights(user_id):
    """Aggregates spending data by category for a user."""
    transactions_collection, accounts_collection, _ = _get_collections()
    if transactions_collection is None or accounts_collection is None:
        return {'message': 'Database connection error'}, 500

    account = accounts_collection.find_one({'user_id': ObjectId(user_id)})
    if not account: return {'message': 'Account not found'}, 404

    # We only aggregate transactions where money left the user's account (from_account)
    pipeline = [
        {'$match': {'from_account': account['account_number']}},
        {'$group': {'_id': '$type', 'totalAmount': {'$sum': '$amount'}}},
        {'$sort': {'totalAmount': -1}}
    ]
    results = list(transactions_collection.aggregate(pipeline))
    
    # Format the results for Chart.js
    labels = [r['_id'] for r in results]
    data = [r['totalAmount'] for r in results]

    return {'labels': labels, 'data': data}, 200
