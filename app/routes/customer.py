from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models.customer import Customer
from sqlalchemy import or_

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/')
def index():
    search = request.args.get('search', '')
    query = Customer.query
    if search:
        query = query.filter(or_(
            Customer.name.ilike(f'%{search}%'),
            Customer.email.ilike(f'%{search}%'),
            Customer.phone.ilike(f'%{search}%')
        ))
    customers = query.order_by(Customer.created_at.desc()).all()
    return render_template('customer/index.html', customers=customers, search=search)

@customer_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        try:
            customer = Customer(
                name=request.form['name'],
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                address=request.form.get('address'),
                gst_no=request.form.get('gst_no')
            )
            db.session.add(customer)
            db.session.commit()
            flash('Customer added successfully!', 'success')
            return redirect(url_for('customer.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    return render_template('customer/add.html')

@customer_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        try:
            customer.name = request.form['name']
            customer.email = request.form.get('email')
            customer.phone = request.form.get('phone')
            customer.address = request.form.get('address')
            customer.gst_no = request.form.get('gst_no')
            db.session.commit()
            flash('Customer updated successfully!', 'success')
            return redirect(url_for('customer.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    return render_template('customer/edit.html', customer=customer)

@customer_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    customer = Customer.query.get_or_404(id)
    try:
        db.session.delete(customer)
        db.session.commit()
        flash('Customer deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: Cannot delete customer with existing quotations/orders', 'danger')
    return redirect(url_for('customer.index'))

@customer_bp.route('/search')
def search():
    query = request.args.get('q', '')
    customers = Customer.query.filter(Customer.name.ilike(f'%{query}%')).limit(10).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'email': c.email,
        'phone': c.phone,
        'gst_no': c.gst_no
    } for c in customers])