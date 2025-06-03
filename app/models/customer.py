from app import db
from datetime import datetime

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    gst_no = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    quotations = db.relationship('Quotation', backref='customer', lazy=True)
    sales_orders = db.relationship('SalesOrder', backref='customer', lazy=True)