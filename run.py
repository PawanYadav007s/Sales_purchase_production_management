from app import create_app, db
from app.models.customer import Customer

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Add sample customer if none exists
        if not Customer.query.first():
            customer = Customer(
                name='Tata Motors',
                email='contact@tata.com',
                phone='1234567890',
                address='Mumbai, Maharashtra',
                gst_no='27AAACT2727Q1ZV'
            )
            db.session.add(customer)
            db.session.commit()
            print("Sample customer added!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)