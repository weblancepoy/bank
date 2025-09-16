# file: services/biller_service.py
# No changes from previous version, file is included for completeness.
from bson import ObjectId
from db_config import billers_collection

def _serialize_biller(biller):
    if biller:
        biller['_id'] = str(biller['_id'])
    return biller

def initialize_billers():
    if billers_collection.count_documents({}) == 0:
        print("No billers found, initializing mock data...")
        mock_billers = [
            {'name': 'City Power & Light', 'category': 'Utilities'},
            {'name': 'AquaFlow Water', 'category': 'Utilities'},
            {'name': 'ConnectNet ISP', 'category': 'Internet'},
            {'name': 'SecureHome Insurance', 'category': 'Insurance'},
            {'name': 'Capital Credit Card', 'category': 'Credit Card'},
        ]
        billers_collection.insert_many(mock_billers)
        print(f"{len(mock_billers)} billers have been added.")
    
def get_all_billers():
    billers = list(billers_collection.find({}))
    return {'billers': [_serialize_biller(b) for b in billers]}, 200

