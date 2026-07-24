from app.extensions import db
from datetime import datetime, timezone

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), index=True)
    email = db.Column(db.String(120)) # Added for notifications
    gender = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)
    blood_group = db.Column(db.String(5))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # user_id linking to authentication (optional if patient logs in)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    orders = db.relationship('TestOrder', backref='patient', lazy=True)
