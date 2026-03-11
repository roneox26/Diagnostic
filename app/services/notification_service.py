from flask_mail import Message
from app.extensions import mail
from flask import current_app, render_template
import threading

class NotificationService:
    @staticmethod
    def send_async_email(app, msg):
        """Sends an email in a background thread."""
        with app.app_context():
            try:
                mail.send(msg)
                print(f"Email sent successfully to {msg.recipients}")
            except Exception as e:
                print(f"Failed to send email: {e}")

    @staticmethod
    def send_report_email(patient_email, patient_name, order_id, pdf_path):
        """Sends the diagnostic report to the patient's email."""
        if not patient_email:
            print("No email provided for patient. Skipping email notification.")
            return

        app = current_app._get_current_object()
        msg = Message(
            subject=f"Your Diagnostic Report - Order #{order_id}",
            recipients=[patient_email],
            body=f"Dear {patient_name},\n\nYour diagnostic report for Order #{order_id} is ready. Please find the attached PDF.\n\nThank you for choosing DiagnosticPro Center."
        )
        
        # Attach the PDF
        with open(pdf_path, 'rb') as f:
            msg.attach(
                filename=f"Report_ORD_{order_id}.pdf",
                content_type="application/pdf",
                data=f.read()
            )
        
        # Send asynchronously to avoid blocking the request
        thread = threading.Thread(target=NotificationService.send_async_email, args=(app, msg))
        thread.start()

    @staticmethod
    def send_collection_alert(patient_mobile, patient_name, order_id):
        """Placeholder for SMS/WhatsApp notification."""
        # In a real app, integrate with an SMS gateway (e.g., Twilio, Nexmo)
        print(f"SMS Alert: Dear {patient_name}, your sample for Order #{order_id} has been collected. We will notify you when the report is ready.")
