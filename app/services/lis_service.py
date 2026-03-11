import os
import csv
import json
from flask import current_app
from app.models import TestOrder, TestOrderItem, TestResult, Sample, User
from app.extensions import db

class LISService:
    @staticmethod
    def process_machine_files():
        """Scans the machine_inputs directory and imports results."""
        input_dir = os.path.join(current_app.root_path, '..', 'machine_inputs')
        os.makedirs(input_dir, exist_ok=True)
        
        # Get a system user to associate with machine imports
        system_user = User.query.filter_by(role='lab_tech').first()
        if not system_user:
            print("No lab_tech user found to associate with LIS imports.")
            return
            
        files = os.listdir(input_dir)
        processed_count = 0
        
        for filename in files:
            if filename.endswith('.csv'):
                file_path = os.path.join(input_dir, filename)
                if LISService._import_csv_result(file_path, system_user.id):
                    # Move to processed folder or delete
                    processed_dir = os.path.join(input_dir, 'processed')
                    os.makedirs(processed_dir, exist_ok=True)
                    os.rename(file_path, os.path.join(processed_dir, filename))
                    processed_count += 1
                    
        return processed_count

    @staticmethod
    def _import_csv_result(file_path, tech_id):
        """
        Expects CSV format: Barcode,TestID,ResultValue
        Example: SMP-1-1,5,12.5
        """
        try:
            with open(file_path, mode='r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    barcode = row.get('Barcode')
                    test_id = row.get('TestID')
                    result_value = row.get('ResultValue')
                    
                    if not barcode or not result_value:
                        continue
                        
                    # Find the sample and order item
                    sample = Sample.query.filter_by(barcode=barcode).first()
                    if not sample:
                        print(f"Sample with barcode {barcode} not found.")
                        continue
                        
                    order = sample.order
                    # Find item for the specific test
                    item = TestOrderItem.query.filter_by(order_id=order.id, test_id=test_id).first()
                    
                    # If test_id not specified, find the first item without a result
                    if not item:
                        item = TestOrderItem.query.filter_by(order_id=order.id).filter(TestOrderItem.result == None).first()
                        
                    if item:
                        # Create or update result
                        if not item.result:
                            result = TestResult(
                                order_item_id=item.id,
                                result_text=result_value,
                                technician_id=tech_id
                            )
                            db.session.add(result)
                        else:
                            item.result.result_text = result_value
                            item.result.technician_id = tech_id
                
                db.session.commit()
                return True
        except Exception as e:
            print(f"Error importing machine file {file_path}: {e}")
            return False
