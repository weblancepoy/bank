import io
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import traceback
import csv # Added for CSV functionality

# Import the database instance to allow querying MongoDB
from database import db_instance
# Import transaction service to utilize its data fetching and CSV logic
from services import transaction_service

def generate_transaction_report_pdf(transactions, start_date=None, end_date=None):
    """
    Generates a PDF report of all transactions using ReportLab (pure Python solution).

    Args:
        transactions (list): A list of transaction dictionaries.
        start_date (str): The start date for the report (optional).
        end_date (str): The end date for the report (optional).

    Returns:
        bytes: The raw PDF data as bytes.
    """
    buffer = io.BytesIO()
    # Use a smaller margin for better use of space on A4
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=30, leftMargin=30, rightMargin=30)
    styles = getSampleStyleSheet()
    Story = []

    # --- 1. Title and Header Information ---
    report_date = datetime.utcnow().strftime('%Y-%m-%d')
    
    # Use different styles for better visual hierarchy
    Story.append(Paragraph("<b>SmartBank Transaction Report</b>", styles['Heading1']))
    Story.append(Paragraph(f"Generated on: {report_date}", styles['Normal']))
    
    date_filter_text = ""
    if start_date or end_date:
        start = start_date if start_date else 'Start'
        end = end_date if end_date else 'End'
        date_filter_text = f"Filtered Range: {start} to {end}"
    
    Story.append(Paragraph(date_filter_text, styles['Normal']))
    Story.append(Paragraph("<br/>", styles['Normal'])) # Spacer

    # --- 2. Table Data ---
    table_data = []
    
    # Header Row
    table_data.append([
        'ID (Short)', 'Date/Time', 'From Account', 'To Account', 'Type', 'Amount', 'Description'
    ])

    # Data Rows
    for tx in transactions:
        tx_id_short = str(tx.get('_id', 'N/A'))[:8] + '...'
        amount_str = f"₹{tx.get('amount', 0.0):.2f}"
        
        timestamp_obj = tx.get('timestamp')
        if isinstance(timestamp_obj, str):
            # If it's a string (due to serialization), parse it first
            try:
                # Handle ISO format including optional 'Z' and ensure timezone info is handled
                timestamp_obj = datetime.fromisoformat(timestamp_obj.replace('Z', '+00:00'))
            except ValueError:
                timestamp_obj = None

        timestamp_str = timestamp_obj.strftime('%Y-%m-%d %H:%M') if timestamp_obj else 'N/A'

        table_data.append([
            tx_id_short,
            timestamp_str,
            tx.get('from_account', 'N/A'),
            tx.get('to_account', 'N/A'),
            tx.get('type', 'N/A'),
            amount_str,
            tx.get('description', '')
        ])

    # --- 3. Table Style and Creation ---
    # Adjusted column widths for A4 (A4 width is ~510pts with 30pt margins)
    col_widths = [60, 90, 80, 80, 50, 70, 100]
    table = Table(table_data, colWidths=col_widths)
    
    # Determine the color based on the transaction type for each row
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC2626')), # Header background (Admin Red)
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]

    for i in range(1, len(table_data)):
        tx_type = table_data[i][4] # 'Type' column is at index 4
        if tx_type in ['Deposit']:
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#E6FFED'))) # Light Green
        elif tx_type in ['Withdrawal', 'Bill Payment']:
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFECE6'))) # Light Red/Orange
        else:
             table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F9F9F9'))) # Light Gray for transfers

    table.setStyle(TableStyle(table_style))
    Story.append(table)

    # --- 4. Build Document ---
    try:
        doc.build(Story)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        print(f"ERROR: ReportLab document build failed. Details: {e}")
        traceback.print_exc()
        # Raise a RuntimeError which is caught by the blueprint
        raise RuntimeError(f"PDF generation failed during document assembly: {e}")

# FIX: Add the missing CSV generation function. 
# We call the logic from transaction_service.py which handles the actual data query.
def generate_transaction_report_csv(start_date=None, end_date=None):
    """
    Generates a CSV report of all transactions by delegating to transaction_service.
    
    Args:
        start_date (str): Optional start date for filtering (ISO format).
        end_date (str): Optional end date for filtering (ISO format).

    Returns:
        str: The CSV data as a string.
    """
    # Fetch data and generate CSV using transaction_service's utility
    # Note: If transaction_service.py doesn't have this function, we must implement it fully here.
    # Based on the typical project structure, the full implementation is included below 
    # to make report_service self-contained for reporting functions.
    
    transactions_response, status_code = transaction_service.get_all_transactions(start_date, end_date)
    
    if status_code != 200 or not transactions_response['transactions']:
        # Return CSV headers only if no transactions are found
        return "ID,Date,From,To,Amount,Type,Description\n"

    transactions = transactions_response['transactions']
    
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['ID', 'Date', 'From Account', 'To Account', 'Amount', 'Type', 'Description'])

    # Write data rows
    for tx in transactions:
        writer.writerow([
            str(tx.get('_id')),
            tx.get('timestamp'),
            tx.get('from_account', 'N/A'),
            tx.get('to_account', 'N/A'),
            tx.get('type', 'N/A'),
            f"₹{tx.get('amount', 0.0):.2f}",
            tx.get('description', '')
        ])

    return output.getvalue()


def get_dashboard_stats():
    """
    Retrieves key metrics for the Admin Dashboard.
    """
    users_collection = db_instance.get_collection('users')
    accounts_collection = db_instance.get_collection('accounts')
    transactions_collection = db_instance.get_collection('transactions')

    # FIX: Check explicitly for None, as pymongo collection objects do not support bool()
    if users_collection is None or accounts_collection is None or transactions_collection is None:
        return {'message': 'Database connection error'}, 500

    try:
        # 1. Total Users (Non-Admin)
        total_users = users_collection.count_documents({'is_admin': False})

        # 2. Total Accounts
        total_accounts = accounts_collection.count_documents({})

        # 3. Transactions Today (Start of day in UTC)
        start_of_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        transactions_today = transactions_collection.count_documents(
            {'timestamp': {'$gte': start_of_today}}
        )
        
        # 4. Security Alerts (Count of pending users for admin approval)
        security_alerts = users_collection.count_documents({'status': 'pending'})

        return {
            'totalUsers': total_users,
            'totalAccounts': total_accounts,
            'transactionsToday': transactions_today,
            'securityAlerts': security_alerts
        }, 200

    except Exception as e:
        print(f"ERROR fetching dashboard stats: {e}")
        traceback.print_exc()
        return {'message': 'An error occurred fetching dashboard statistics.'}, 500
