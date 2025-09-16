# file: services/biller_service.py
import uuid
from database import billers_db

def initialize_billers():
    """Initializes the database with some mock billers if it's empty."""
    if not billers_db:
        mock_billers = [
            {'name': 'City Power & Light', 'category': 'Utilities'},
            {'name': 'AquaFlow Water', 'category': 'Utilities'},
            {'name': 'ConnectNet ISP', 'category': 'Internet'},
            {'name': 'SecureHome Insurance', 'category': 'Insurance'},
            {'name': 'Capital Credit Card', 'category': 'Credit Card'},
        ]
        for biller in mock_billers:
            biller_id = str(uuid.uuid4())
            billers_db[biller_id] = {'id': biller_id, 'name': biller['name'], 'category': biller['category']}
    
def get_all_billers():
    """Returns a list of all available billers."""
    return {'billers': list(billers_db.values())}, 200

def get_biller_by_id(biller_id):
    """Retrieves a single biller by its ID."""
    return billers_db.get(biller_id)

