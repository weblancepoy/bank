import random
from datetime import datetime, timedelta
from bson import ObjectId
from werkzeug.security import generate_password_hash
from services.user_service import create_user
from services.account_service import create_account, deposit
from services.transaction_service import create_transfer, pay_bill
from services.biller_service import get_all_billers
from database import db_instance

def seed_initial_data():
    """Seeds the database with a sample user, account, and transactions."""
    users_collection = db_instance.get_collection('users')
    
    # Check if a sample user already exists to avoid duplication
    if users_collection is not None and users_collection.find_one({'username': 'sampleuser'}):
        print("Initial data already seeded. Skipping...")
        return

    print("Seeding initial data...")
    
    try:
        # Create a sample user and their account
        sample_user_data = {
            'username': 'sampleuser',
            'email': 'sample@bank.com',
            'password': 'password123',
            'is_admin': False
        }
        user_response, user_status = create_user(sample_user_data, created_by_admin=True)
        
        if user_status == 201:
            user_id = user_response['user']['_id']
            account_response, account_status = create_account(user_id)
            sample_account_number = account_response['account']['account_number']

            # Get a list of available billers
            billers_response, _ = get_all_billers()
            billers = billers_response.get('billers', [])
            
            # Add some transactions using the correct service functions
            deposit(
                user_id=user_id,
                amount=2500
            )
            
            create_transfer(
                from_user_id=user_id,
                to_account_number='ACC987654321', # Dummy account number for demo
                amount=500,
                description='Transfer to friend'
            )

            if billers:
                pay_bill(
                    user_id=user_id,
                    biller_id=billers[0]['_id'],
                    amount=150
                )
            
            print("Initial data seeding complete!")
        else:
            print(f"Failed to create sample user: {user_response['message']}")
            
    except Exception as e:
        print(f"An error occurred during data seeding: {e}")
