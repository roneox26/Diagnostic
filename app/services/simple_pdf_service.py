from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os
from flask import current_app
from datetime import datetime

class SimplePDFService:
    @staticmethod
    def generate_simple_report(order_id):
        try:
            from app.models import TestOrder
            
            order = TestOrder.query.get(order_id)
            if not order:
                return None
                
            # Create output directory
            output_dir = os.path.join(current_app.root_path, '..', 'out')
            os.makedirs(output_dir, exist_ok=True)
            pdf_path = os.path.join(output_dir, f'Report_ORD_{order.id}.pdf')
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Header
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.darkblue,
                alignment=TA_CENTER,
                spaceAfter=20
            )
            
            story.append(Paragraph("MEDCARE DIAGNOSTIC CENTER", header_style))
            story.append(Paragraph("Medical Laboratory Report", styles['Heading2']))
            story.append(Spacer(1, 20))
            
            # Patient Info
            patient_data = [
                ['Patient Name:', order.patient.name],
                ['Patient ID:', order.patient.patient_code],
                ['Phone:', order.patient.phone],
                ['Gender:', order.patient.gender],
                ['Report Date:', datetime.now().strftime('%d %B, %Y')]
            ]
            
            patient_table = Table(patient_data, colWidths=[2*inch, 3*inch])
            patient_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(patient_table)
            story.append(Spacer(1, 30))
            
            # Test Results
            story.append(Paragraph("TEST RESULTS", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            test_data = [['Test Name', 'Result', 'Reference Range']]
            
            for item in order.items:
                if item.result:
                    test_data.append([
                        item.test.test_name,
                        item.result.result_text,
                        'Normal Range'
                    ])
            
            if len(test_data) > 1:
                test_table = Table(test_data, colWidths=[3*inch, 2*inch, 2*inch])
                test_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(test_table)
            
            story.append(Spacer(1, 50))
            
            # Footer
            footer_text = "This is a computer generated report. For any queries, contact: +880-1234-567890"
            story.append(Paragraph(footer_text, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            return pdf_path
            
        except Exception as e:
            print(f"Error generating simple PDF: {e}")
            return None