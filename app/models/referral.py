from app.extensions import db

class ReferralDoctor(db.Model):
    __tablename__ = 'referral_doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    hospital_name = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    commission_rate = db.Column(db.Numeric(5, 2), default=0.0) # Percentage e.g., 10.0 for 10%
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # For portal access
    
    commissions = db.relationship('ReferralCommission', backref='doctor', lazy=True)
    
    @property
    def name(self):
        """Backward compatibility alias for doctor_name."""
        return self.doctor_name
    
    @property
    def hospital(self):
        """Backward compatibility alias for hospital_name."""
        return self.hospital_name

class ReferralCommission(db.Model):
    __tablename__ = 'referral_commissions'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('referral_doctors.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('test_orders.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, paid
