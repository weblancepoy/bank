# file: services/biller_service.py
# No changes from previous version, file is included for completeness.
from bson import ObjectId
from db_config import billers_collection

def initialize_billers():
    if billers_collection.count_documents({}) == 0:
        print("Initializing mock billers...")
        billers_collection.insert_many([
            {'name': 'City Power & Light', 'category': 'Utilities'}, {'name': 'AquaFlow Water', 'category': 'Utilities'},
            {'name': 'ConnectNet ISP', 'category': 'Internet'}, {'name': 'SecureHome Insurance', 'category': 'Insurance'},
            {'name': 'Capital Credit Card', 'category': 'Credit Card'}
        ])

def get_all_billers():
    billers = list(billers_collection.find({}))
    return {'billers': [{**b, '_id': str(b['_id'])} for b in billers]}

