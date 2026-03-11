import os
from flask import render_template, make_response, current_app
from app.models import TestOrder
from app.services.barcode_service import BarcodeService
from datetime import datetime

class PDFService:
    @staticmethod
    def generate_report_pdf(order_id):
        try:
            # Try WeasyPrint first
            from weasyprint import HTML, CSS
            use_weasyprint = True
        except (ImportError, OSError) as e:
            print(f"WeasyPrint not available: {e}")
            # Fallback to simple HTML file
            use_weasyprint = False
            
        order = TestOrder.query.get(order_id)
        if not order:
            return None
            
        # Generate QR code for verification
        qr_path = BarcodeService.generate_report_qr(order.uuid)
        
        # Compile data for the report
        report_data = {
            'order': order,
            'patient': order.patient,
            'items': [item for item in order.items if item.result], # Only items with results
            'date_generated': datetime.now().strftime('%Y-%m-%d %I:%M %p'),
            'qr_code': qr_path
        }
        
        # Render HTML template to a string
        rendered_html = render_template('pdf/medical_report.html', **report_data)
        
        # Determine output path
        output_dir = os.path.join(current_app.root_path, '..', 'out')
        os.makedirs(output_dir, exist_ok=True)
        
        if use_weasyprint:
            # Use WeasyPrint for PDF
            pdf_path = os.path.join(output_dir, f'Report_ORD_{order.id}.pdf')
            HTML(string=rendered_html).write_pdf(pdf_path)
            return pdf_path
        else:
            # Try ReportLab as fallback
            try:
                from app.services.simple_pdf_service import SimplePDFService
                pdf_path = SimplePDFService.generate_simple_report(order_id)
                if pdf_path:
                    return pdf_path
            except Exception as e:
                print(f"ReportLab also failed: {e}")
            
            # Final fallback: Save as HTML file
            html_path = os.path.join(output_dir, f'Report_ORD_{order.id}.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(rendered_html)
            return html_path
