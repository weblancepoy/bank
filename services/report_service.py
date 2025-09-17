import csv
import io
from datetime import datetime, timedelta
from database import db_instance

def get_dashboard_stats():
    """Gathers various statistics for the admin dashboard."""
    users_collection = db_instance.get_collection('users')
    accounts_collection = db_instance.get_collection('accounts')
    transactions_collection = db_instance.get_collection('transactions')

    if not all([users_collection, accounts_collection, transactions_collection]):
        return {"error": "Database connection failed"}, 500

    total_users = users_collection.count_documents({'is_admin': False})
    total_accounts = accounts_collection.count_documents({})
    
    # Transactions in the last 24 hours
    twenty_four_hours_ago = datetime.utcnow() - timedelta(days=1)
    transactions_today = transactions_collection.count_documents({'timestamp': {'$gte': twenty_four_hours_ago}})
    
    # Placeholder for security alerts
    security_alerts = 0 

    return {
        "totalUsers": total_users,
        "totalAccounts": total_accounts,
        "transactionsToday": transactions_today,
        "securityAlerts": security_alerts
    }

def generate_transaction_report_csv():
    """Generates a CSV report of all transactions."""
    transactions_collection = db_instance.get_collection('transactions')
    if not transactions_collection:
        return "Database connection error."

    transactions = transactions_collection.find({})
    
    # Use io.StringIO to create an in-memory text buffer
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    header = ['Transaction ID', 'From Account', 'To Account', 'Amount', 'Type', 'Description', 'Timestamp']
    writer.writerow(header)
    
    # Write data rows
    for tx in transactions:
        row = [
            str(tx['_id']),
            tx.get('from_account', 'N/A'),
            tx.get('to_account', 'N/A'),
            tx.get('amount', 0),
            tx.get('type', 'N/A'),
            tx.get('description', ''),
            tx.get('timestamp').isoformat() if tx.get('timestamp') else 'N/A'
        ]
        writer.writerow(row)
    
    # Get the content of the in-memory file
    return output.getvalue()

