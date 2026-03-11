from app.extensions import db

class TestCategory(db.Model):
    __tablename__ = 'test_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    tests = db.relationship('Test', backref='category', lazy=True)

class Test(db.Model):
    __tablename__ = 'tests'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('test_categories.id'), nullable=False)
    test_name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    sample_type = db.Column(db.String(50)) # Blood, Urine, etc.
    description = db.Column(db.Text)
