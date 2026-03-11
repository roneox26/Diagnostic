import os
from flask import Blueprint, redirect, url_for, flash, send_file, render_template
from flask_login import login_required
from app.services.pdf_service import PDFService
from app.services.notification_service import NotificationService
from app.frontend.decorators import role_required
from app.models import TestOrder
from datetime import datetime

bp_reports = Blueprint('reports', __name__)

@bp_reports.route('/reports/preview/<int:order_id>')
@login_required
def preview_report(order_id):
    order = TestOrder.query.get_or_404(order_id)
    report_data = {
        'order': order,
        'patient': order.patient,
        'items': [item for item in order.items if item.result],
        'date_generated': datetime.now().strftime('%Y-%m-%d %I:%M %p')
    }
    return render_template('pdf/medical_report.html', **report_data)

@bp_reports.route('/public/report/<int:order_id>')
def public_download_report(order_id):
    order = TestOrder.query.get_or_404(order_id)
    
    # Check if any results are entered
    has_results = any(item.result for item in order.items)
    if not has_results:
        flash("Report is not ready yet. Please check back later.", "warning")
        return redirect(url_for('portal.public_report_access'))
        
    file_path = PDFService.generate_report_pdf(order_id)
    
    if file_path and os.path.exists(file_path):
        # Determine file type and download name
        if file_path.endswith('.pdf'):
            download_name = f"Report_ORD_{order_id}.pdf"
            mimetype = 'application/pdf'
        else:
            download_name = f"Report_ORD_{order_id}.html"
            mimetype = 'text/html'
            
        return send_file(file_path, as_attachment=True, download_name=download_name, mimetype=mimetype)
    else:
        flash("Error generating report. Please try again.", "danger")
        return redirect(url_for('portal.public_report_access'))

@bp_reports.route('/reports/generate/<int:order_id>')
@login_required
@role_required('admin', 'doctor', 'receptionist')
def download_report(order_id):
    order = TestOrder.query.get_or_404(order_id)
    
    # Check if any results are entered
    has_results = any(item.result for item in order.items)
    if not has_results:
        flash("Cannot generate report: No lab results entered yet.", "warning")
        return redirect(url_for('frontend.orders_list'))
        
    file_path = PDFService.generate_report_pdf(order_id)
    
    if file_path and os.path.exists(file_path):
        # Determine file type and download name
        if file_path.endswith('.pdf'):
            download_name = f"Report_ORD_{order_id}.pdf"
            mimetype = 'application/pdf'
        else:
            download_name = f"Report_ORD_{order_id}.html"
            mimetype = 'text/html'
            
        # Send Email to patient
        if order.patient.email:
            NotificationService.send_report_email(
                order.patient.email, 
                order.patient.name, 
                order.id, 
                file_path
            )
            flash(f"Report sent to {order.patient.email}", "success")
            
        return send_file(file_path, as_attachment=True, download_name=download_name, mimetype=mimetype)
    else:
        flash("Error generating report. Please try again.", "danger")
        return redirect(url_for('frontend.orders_list'))
