from app.extensions import db
from datetime import datetime
import uuid

class TestOrder(db.Model):
    __tablename__ = 'test_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(30), default='pending') # pending, sample_collected, processing, completed
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # receptionist who created it
    referral_id = db.Column(db.Integer, db.ForeignKey('referral_doctors.id'), nullable=True)
    
    # Linking models
    items = db.relationship('TestOrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
    samples = db.relationship('Sample', backref='order', lazy=True)
    report = db.relationship('Report', backref='order', uselist=False, lazy=True)
    invoice = db.relationship('Invoice', backref='order', uselist=False, lazy=True)

class TestOrderItem(db.Model):
    __tablename__ = 'test_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('test_orders.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    test = db.relationship('Test', lazy=True)
    result = db.relationship('TestResult', backref='order_item', uselist=False, lazy=True)
