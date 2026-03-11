from app.extensions import db

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50)) # Reagent, Consumable, Equipment
    stock_quantity = db.Column(db.Integer, default=0)
    expiry_date = db.Column(db.Date)
    unit_price = db.Column(db.Float, default=0.0)
    low_stock_threshold = db.Column(db.Integer, default=10) # Alert if stock falls below this
    
class TestReagentConsumption(db.Model):
    """Maps how much of a reagent is consumed per test."""
    __tablename__ = 'test_reagent_consumption'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    quantity_consumed = db.Column(db.Float, nullable=False) # e.g., 5.0 ml
    
    test = db.relationship('Test', backref='reagent_requirements', lazy=True)
    item = db.relationship('InventoryItem', backref='used_in_tests', lazy=True)
