from app import db
from datetime import datetime

class SalesOrder(db.Model):
    __tablename__ = 'sales_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    so_number = db.Column(db.String(50), unique=True, nullable=False)
    po_number = db.Column(db.String(50))
    date = db.Column(db.Date, nullable=False)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotations.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    delivery_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Active')  # Active, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    quotation = db.relationship('Quotation', backref='sales_orders')