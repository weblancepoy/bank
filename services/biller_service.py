from bson import ObjectId
from database import db_instance

def _get_billers_collection():
    """Helper to get the billers collection."""
    return db_instance.get_collection('billers')

def _serialize_biller(biller):
    """Converts ObjectId to string for JSON serialization."""
    if biller:
        biller['_id'] = str(biller['_id'])
    return biller

def initialize_billers():
    """Initializes the billers collection with mock data if it's empty."""
    billers_collection = _get_billers_collection()
    if billers_collection is not None and billers_collection.count_documents({}) == 0:
        print("Initializing mock billers...")
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
    """Retrieves all billers from the collection."""
    billers_collection = _get_billers_collection()
    if billers_collection is None:
        return {'message': 'Database connection error'}, 500

    billers = list(billers_collection.find({}))
    return {'billers': [_serialize_biller(b) for b in billers]}, 200
