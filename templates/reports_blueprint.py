import io
from flask import Blueprint, jsonify, g, Response
from services import report_service, transaction_service, pdf_service
from app import admin_required

# Create a blueprint for report-related routes
reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/transactions.pdf', methods=['GET'])
@admin_required
def download_transactions_report_pdf():
    """
    Handles the API request to download a PDF report of all transactions.
    """
    transactions_response, status_code = transaction_service.get_all_transactions()
    
    # Check for errors from the transaction service
    if status_code != 200:
        return jsonify(transactions_response), status_code
    
    transactions = transactions_response['transactions']
    
    # Handle case where no transactions are found
    if not transactions:
        return jsonify({'message': 'No transactions found to generate a report.'}), 404
        
    try:
        # Generate the PDF data using the service
        pdf_data = pdf_service.generate_transaction_report_pdf(transactions)
        
        # Return the PDF data as a downloadable file
        return Response(
            pdf_data,
            mimetype="application/pdf",
            headers={"Content-disposition": "attachment; filename=transactions_report.pdf"}
        )
    except Exception as e:
        # Catch any errors during PDF generation and return a user-friendly message
        print(f"ERROR during PDF report generation: {e}")
        return jsonify({'message': f'An error occurred during report generation: {e}'}), 500
