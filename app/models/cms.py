from app.extensions import db

class SiteSetting(db.Model):
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)

class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    is_active = db.Column(db.Boolean, default=True)

class Partner(db.Model):
    __tablename__ = 'partners'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon_class = db.Column(db.String(100), nullable=True)
    partner_type = db.Column(db.String(50), nullable=False) # 'corporate' or 'service'
    description = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
