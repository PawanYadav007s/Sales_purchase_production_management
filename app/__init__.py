from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.customer import customer_bp
    from app.routes.quotation import quotation_bp
    from app.routes.sales_order import sales_order_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(quotation_bp, url_prefix='/quotation')
    app.register_blueprint(sales_order_bp, url_prefix='/sales_order')
    
    with app.app_context():
        db.create_all()
    
    return app