from app.extensions import db
from datetime import datetime, timezone

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('test_orders.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Numeric(10, 2), default=0.0)
    paid_amount = db.Column(db.Numeric(10, 2), default=0.0)
    payment_status = db.Column(db.String(20), default='unpaid') # unpaid, partial, paid
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Optional relationship
    patient = db.relationship('Patient', backref='invoices', lazy=True)
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade="all, delete-orphan")

class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    test_name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)
