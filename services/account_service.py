# file: services/account_service.py
# No changes from previous version, file is included for completeness.
import random
from bson import ObjectId
from db_config import accounts_collection

def _serialize_account(account):
    if account:
        account['_id'] = str(account['_id'])
        account['user_id'] = str(account['user_id'])
    return account

def create_account(user_id):
    account_number = f"ACC{random.randint(100000000, 999999999)}"
    accounts_collection.insert_one({'user_id': ObjectId(user_id), 'account_number': account_number, 'balance': 5000.00, 'type': 'checking'})
    return {'message': 'Account created'}, 201

def get_account_by_user_id(user_id):
    account = accounts_collection.find_one({'user_id': ObjectId(user_id)})
    return {'account': _serialize_account(account)} if account else ({'message': 'Account not found'}, 404)

