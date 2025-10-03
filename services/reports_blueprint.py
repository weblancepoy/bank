import io
from flask import Blueprint, jsonify, g, Response, request
# FIX: Ensure report_service is imported to use its ReportLab implementation
from services import transaction_service, pdf_service, report_service 
from services.decorators import admin_required

# Create a blueprint for report-related routes
reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/transactions.pdf', methods=['GET'])
@admin_required
def download_transactions_report_pdf():
    """
    Handles the API request to download a PDF report of all transactions,
    with optional date filtering.
    (FIX: Updated to use report_service's ReportLab implementation instead of pdf_service's pdfkit,
    which was causing wkhtmltopdf dependency errors.)
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Ensure transactions_response is a tuple of (data, status_code)
    transactions_response, status_code = transaction_service.get_all_transactions(
        start_date=start_date, end_date=end_date
    )
    
    # Check for errors from the transaction service (e.g., Auth/DB errors)
    if status_code != 200:
        return jsonify(transactions_response), status_code
    
    transactions = transactions_response['transactions']
    
    # Handle case where no transactions are found
    if not transactions:
        # Return a JSON error message instead of an empty file
        return jsonify({'message': 'No transactions found to generate a report.'}), 404
        
    try:
        # FIX: Use the ReportLab implementation from report_service.py
        pdf_data = report_service.generate_transaction_report_pdf(transactions, start_date=start_date, end_date=end_date)
        
        # Return the PDF data as a downloadable file
        return Response(
            pdf_data,
            mimetype="application/pdf",
            headers={"Content-disposition": "attachment; filename=transactions_report.pdf"}
        )
    except RuntimeError as e:
        # Catch ReportLab's specific error messages and return a 500
        print(f"ERROR during PDF report generation (ReportLab failure): {e}")
        return jsonify({'message': f'Report generation failed: {e}'}), 500
    except Exception as e:
        # Catch any other generic errors
        print(f"ERROR during PDF report generation: {e}")
        return jsonify({'message': f'An unexpected error occurred during report generation.'}), 500
