import csv
import io
from datetime import datetime, timedelta
from database import db_instance

def get_dashboard_stats():
    """Gathers various statistics for the admin dashboard."""
    users_collection = db_instance.get_collection('users')
    accounts_collection = db_instance.get_collection('accounts')
    transactions_collection = db_instance.get_collection('transactions')

    if users_collection is None or accounts_collection is None or transactions_collection is None:
        return {"error": "Database connection failed"}, 500

    total_users = users_collection.count_documents({'is_admin': False})
    total_accounts = accounts_collection.count_documents({})
    
    twenty_four_hours_ago = datetime.utcnow() - timedelta(days=1)
    transactions_today = transactions_collection.count_documents({'timestamp': {'$gte': twenty_four_hours_ago}})
    
    security_alerts = 0 

    return {
        "totalUsers": total_users,
        "totalAccounts": total_accounts,
        "transactionsToday": transactions_today,
        "securityAlerts": security_alerts
    }, 200

def generate_transaction_report_csv():
    """Generates a CSV report of all transactions."""
    transactions_collection = db_instance.get_collection('transactions')
    if transactions_collection is None:
        return "Database connection error."

    transactions = transactions_collection.find({})
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    header = ['Transaction ID', 'From Account', 'To Account', 'Amount', 'Type', 'Description', 'Timestamp']
    writer.writerow(header)
    
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
    
    return output.getvalue()
