from app import db
from datetime import datetime
import json

class Quotation(db.Model):
    __tablename__ = 'quotations'
    
    id = db.Column(db.Integer, primary_key=True)
    quotation_number = db.Column(db.String(50), unique=True, nullable=False)
    rfq_number = db.Column(db.String(50))
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    items = db.Column(db.Text)  # JSON string
    total_amount = db.Column(db.Float, default=0.0)
    valid_until = db.Column(db.Date)
    status = db.Column(db.String(20), default='Pending')  # Pending, Accepted, Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_items(self):
        return json.loads(self.items) if self.items else []
    
    def set_items(self, items_list):
        self.items = json.dumps(items_list)