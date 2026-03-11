import os
import barcode
from barcode.writer import ImageWriter
import qrcode
from flask import current_app

class BarcodeService:
    @staticmethod
    def generate_sample_barcode(sample_id, barcode_value):
        """Generates a barcode image for a sample tube."""
        try:
            CODE128 = barcode.get('code128')
            code = CODE128(barcode_value, writer=ImageWriter())
            
            # Directory to store barcodes
            barcode_dir = os.path.join(current_app.root_path, 'static', 'barcodes')
            os.makedirs(barcode_dir, exist_ok=True)
            
            file_path = os.path.join(barcode_dir, f"sample_{sample_id}")
            filename = code.save(file_path)
            
            return filename
        except Exception as e:
            print(f"Error generating barcode: {e}")
            return None

    @staticmethod
    def generate_report_qr(order_uuid):
        """Generates a QR code for report verification."""
        try:
            # The verification URL - in a real app, this would be your public domain
            # For now, we use a placeholder that would lead to a verification route
            verification_url = f"https://yourclinic.com/verify/report/{order_uuid}"
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(verification_url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            
            # Directory to store QR codes
            qr_dir = os.path.join(current_app.root_path, 'static', 'qrcodes')
            os.makedirs(qr_dir, exist_ok=True)
            
            file_path = os.path.join(qr_dir, f"report_{order_uuid}.png")
            img.save(file_path)
            
            return file_path
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return None
