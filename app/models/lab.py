from app.extensions import db
from datetime import datetime, timezone

class Sample(db.Model):
    __tablename__ = 'samples'
    
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50), unique=True, nullable=True, index=True) # Generated upon collection
    order_id = db.Column(db.Integer, db.ForeignKey('test_orders.id'), nullable=False)
    sample_type = db.Column(db.String(50), nullable=False) # Blood, Urine, Swab, etc.
    collection_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    collector_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # receptionist or lab tech
    status = db.Column(db.String(30), default='collected', index=True) # collected, sent_to_lab, processing, completed

class TestResult(db.Model):
    __tablename__ = 'test_results'
    
    id = db.Column(db.Integer, primary_key=True)
    order_item_id = db.Column(db.Integer, db.ForeignKey('test_order_items.id'), nullable=False)
    result_text = db.Column(db.Text)
    result_file = db.Column(db.String(255)) # Path to any uploaded raw machine file
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id')) # Doctor ID if verified
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('test_orders.id'), nullable=False)
    report_file = db.Column(db.String(255)) # Path to generated PDF
    generated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
