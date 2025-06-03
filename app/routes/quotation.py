from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from app import db
from app.models.quotation import Quotation
from app.models.customer import Customer
from datetime import datetime, date
from sqlalchemy import or_
import json
import io
import csv

quotation_bp = Blueprint('quotation', __name__)

@quotation_bp.route('/')
def index():
    search = request.args.get('search', '')
    query = Quotation.query.join(Customer)
    if search:
        query = query.filter(or_(
            Quotation.quotation_number.ilike(f'%{search}%'),
            Quotation.rfq_number.ilike(f'%{search}%'),
            Customer.name.ilike(f'%{search}%')
        ))
    quotations = query.order_by(Quotation.created_at.desc()).all()
    return render_template('quotation/index.html', quotations=quotations, search=search)

@quotation_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        try:
            # Generate quotation number
            last_quotation = Quotation.query.order_by(Quotation.id.desc()).first()
            if last_quotation:
                last_num = int(last_quotation.quotation_number.split('-')[-1])
                quotation_number = f"QT-{datetime.now().year}-{str(last_num + 1).zfill(4)}"
            else:
                quotation_number = f"QT-{datetime.now().year}-0001"
            
            # Collect items
            items = []
            descriptions = request.form.getlist('description[]')
            quantities = request.form.getlist('quantity[]')
            unit_prices = request.form.getlist('unit_price[]')
            
            total_amount = 0
            for i in range(len(descriptions)):
                if descriptions[i]:
                    qty = float(quantities[i])
                    price = float(unit_prices[i])
                    total = qty * price
                    total_amount += total
                    items.append({
                        'description': descriptions[i],
                        'quantity': qty,
                        'unit_price': price,
                        'total': total
                    })
            
            quotation = Quotation(
                quotation_number=quotation_number,
                rfq_number=request.form.get('rfq_number'),
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                customer_id=request.form['customer_id'],
                total_amount=total_amount,
                valid_until=datetime.strptime(request.form['valid_until'], '%Y-%m-%d').date() if request.form.get('valid_until') else None,
                status='Pending'
            )
            quotation.set_items(items)
            
            db.session.add(quotation)
            db.session.commit()
            flash('Quotation created successfully!', 'success')
            return redirect(url_for('quotation.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('quotation.add'))
    
    customers = Customer.query.order_by(Customer.name).all()
    today = date.today().isoformat()
    return render_template('quotation/add.html', customers=customers, today=today)

@quotation_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    quotation = Quotation.query.get_or_404(id)
    
    # Check if quotation is already accepted
    if quotation.status == 'Accepted':
        flash('Cannot edit accepted quotation!', 'warning')
        return redirect(url_for('quotation.index'))
    
    if request.method == 'POST':
        try:
            # Collect items
            items = []
            descriptions = request.form.getlist('description[]')
            quantities = request.form.getlist('quantity[]')
            unit_prices = request.form.getlist('unit_price[]')
            
            total_amount = 0
            for i in range(len(descriptions)):
                if descriptions[i]:
                    qty = float(quantities[i])
                    price = float(unit_prices[i])
                    total = qty * price
                    total_amount += total
                    items.append({
                        'description': descriptions[i],
                        'quantity': qty,
                        'unit_price': price,
                        'total': total
                    })
            
            quotation.rfq_number = request.form.get('rfq_number')
            quotation.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            quotation.customer_id = request.form['customer_id']
            quotation.total_amount = total_amount
            quotation.valid_until = datetime.strptime(request.form['valid_until'], '%Y-%m-%d').date() if request.form.get('valid_until') else None
            quotation.set_items(items)
            
            db.session.commit()
            flash('Quotation updated successfully!', 'success')
            return redirect(url_for('quotation.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    customers = Customer.query.order_by(Customer.name).all()
    quotation.items_list = quotation.get_items()
    return render_template('quotation/edit.html', quotation=quotation, customers=customers)

@quotation_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    quotation = Quotation.query.get_or_404(id)
    
    # Check if quotation has sales orders
    if quotation.sales_orders:
        flash('Cannot delete quotation with existing sales orders!', 'danger')
        return redirect(url_for('quotation.index'))
    
    try:
        db.session.delete(quotation)
        db.session.commit()
        flash('Quotation deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('quotation.index'))

@quotation_bp.route('/view/<int:id>')
def view(id):
    quotation = Quotation.query.get_or_404(id)
    quotation.items_list = quotation.get_items()
    return render_template('quotation/view.html', quotation=quotation)

@quotation_bp.route('/export/csv')
def export_csv():
    quotations = Quotation.query.join(Customer).order_by(Quotation.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Quotation No', 'RFQ No', 'Date', 'Customer', 'Total Amount', 'Status', 'Valid Until'])
    
    for q in quotations:
        writer.writerow([
            q.quotation_number,
            q.rfq_number or '',
            q.date.strftime('%Y-%m-%d'),
            q.customer.name,
            f'₹{q.total_amount:,.2f}',
            q.status,
            q.valid_until.strftime('%Y-%m-%d') if q.valid_until else ''
        ])
    
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    
    return send_file(mem, mimetype='text/csv', as_attachment=True, download_name='quotations.csv')