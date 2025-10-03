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

def create_biller(name, category):
    """Admin: Creates a new biller."""
    billers_collection = _get_billers_collection()
    if billers_collection is None:
        return {'message': 'Database connection error'}, 500
    
    if not name or not category:
        return {'message': 'Biller name and category are required'}, 400

    # Basic check for duplicates, although multiple billers can have the same name
    if billers_collection.find_one({'name': name, 'category': category}):
        return {'message': 'Biller already exists in this category'}, 409

    new_biller = {
        'name': name,
        'category': category
    }
    billers_collection.insert_one(new_biller)
    return {'message': 'Biller created successfully'}, 201

def update_biller(biller_id, name, category):
    """Admin: Updates an existing biller."""
    billers_collection = _get_billers_collection()
    if billers_collection is None:
        return {'message': 'Database connection error'}, 500
    
    if not ObjectId.is_valid(biller_id):
        return {'message': 'Invalid biller ID'}, 400

    update_data = {}
    if name: update_data['name'] = name
    if category: update_data['category'] = category

    if not update_data:
        return {'message': 'No fields to update'}, 400
    
    result = billers_collection.update_one(
        {'_id': ObjectId(biller_id)}, 
        {'$set': update_data}
    )
    
    if result.matched_count == 0:
        return {'message': 'Biller not found'}, 404
    return {'message': 'Biller updated successfully'}, 200

def delete_biller(biller_id):
    """Admin: Deletes a biller."""
    billers_collection = _get_billers_collection()
    if billers_collection is None:
        return {'message': 'Database connection error'}, 500

    if not ObjectId.is_valid(biller_id):
        return {'message': 'Invalid biller ID'}, 400
        
    result = billers_collection.delete_one({'_id': ObjectId(biller_id)})
    
    if result.deleted_count == 0:
        return {'message': 'Biller not found'}, 404
    return {'message': 'Biller deleted successfully'}, 200
