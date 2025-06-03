from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from app import db
from app.models.sales_order import SalesOrder
from app.models.quotation import Quotation
from app.models.customer import Customer
from datetime import datetime, date
from sqlalchemy import or_
import io
import csv

sales_order_bp = Blueprint('sales_order', __name__)

@sales_order_bp.route('/')
def index():
    search = request.args.get('search', '')
    query = SalesOrder.query.join(Customer).join(Quotation)
    if search:
        query = query.filter(or_(
            SalesOrder.so_number.ilike(f'%{search}%'),
            SalesOrder.po_number.ilike(f'%{search}%'),
            Customer.name.ilike(f'%{search}%'),
            Quotation.quotation_number.ilike(f'%{search}%')
        ))
    sales_orders = query.order_by(SalesOrder.created_at.desc()).all()
    return render_template('sales_order/index.html', sales_orders=sales_orders, search=search)

@sales_order_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        try:
            # Generate SO number
            last_so = SalesOrder.query.order_by(SalesOrder.id.desc()).first()
            if last_so:
                last_num = int(last_so.so_number.split('-')[-1])
                so_number = f"SO-{datetime.now().year}-{str(last_num + 1).zfill(4)}"
            else:
                so_number = f"SO-{datetime.now().year}-0001"
            
            quotation_id = request.form['quotation_id']
            quotation = Quotation.query.get(quotation_id)
            
            sales_order = SalesOrder(
                so_number=so_number,
                po_number=request.form['po_number'],
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                quotation_id=quotation_id,
                customer_id=quotation.customer_id,
                delivery_date=datetime.strptime(request.form['delivery_date'], '%Y-%m-%d').date() if request.form.get('delivery_date') else None,
                status='Active'
            )
            
            # Update quotation status to Accepted
            quotation.status = 'Accepted'
            
            db.session.add(sales_order)
            db.session.commit()
            flash('Sales Order created successfully!', 'success')
            return redirect(url_for('sales_order.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('sales_order.add'))
    
    # Get only pending quotations
    quotations = Quotation.query.filter_by(status='Pending').order_by(Quotation.created_at.desc()).all()
    today = date.today().isoformat()
    return render_template('sales_order/add.html', quotations=quotations, today=today)

@sales_order_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    sales_order = SalesOrder.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            sales_order.po_number = request.form['po_number']
            sales_order.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            sales_order.delivery_date = datetime.strptime(request.form['delivery_date'], '%Y-%m-%d').date() if request.form.get('delivery_date') else None
            sales_order.status = request.form['status']
            
            db.session.commit()
            flash('Sales Order updated successfully!', 'success')
            return redirect(url_for('sales_order.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('sales_order/edit.html', sales_order=sales_order)

@sales_order_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    sales_order = SalesOrder.query.get_or_404(id)
    
    try:
        # Revert quotation status if needed
        if sales_order.quotation and not SalesOrder.query.filter(
            SalesOrder.quotation_id == sales_order.quotation_id,
            SalesOrder.id != sales_order.id
        ).first():
            sales_order.quotation.status = 'Pending'
        
        db.session.delete(sales_order)
        db.session.commit()
        flash('Sales Order deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('sales_order.index'))

@sales_order_bp.route('/view/<int:id>')
def view(id):
    sales_order = SalesOrder.query.get_or_404(id)
    return render_template('sales_order/view.html', sales_order=sales_order)

@sales_order_bp.route('/export/csv')
def export_csv():
    sales_orders = SalesOrder.query.join(Customer).join(Quotation).order_by(SalesOrder.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['SO No', 'PO No', 'Date', 'Customer', 'Quotation No', 'Delivery Date', 'Status'])
    
    for so in sales_orders:
        writer.writerow([
            so.so_number,
            so.po_number,
            so.date.strftime('%Y-%m-%d'),
            so.customer.name,
            so.quotation.quotation_number,
            so.delivery_date.strftime('%Y-%m-%d') if so.delivery_date else '',
            so.status
        ])
    
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    
    return send_file(mem, mimetype='text/csv', as_attachment=True, download_name='sales_orders.csv')