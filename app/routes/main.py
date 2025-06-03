from flask import Blueprint, render_template, jsonify
from app import db
from app.models.customer import Customer
from app.models.quotation import Quotation
from app.models.sales_order import SalesOrder
from sqlalchemy import func
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/api/dashboard-stats')
def dashboard_stats():
    """API endpoint for dashboard statistics"""
    try:
        # Basic counts
        total_customers = Customer.query.count()
        total_quotations = Quotation.query.count()
        total_sales_orders = SalesOrder.query.count()
        
        # Quotation statistics
        pending_quotations = Quotation.query.filter_by(status='Pending').count()
        accepted_quotations = Quotation.query.filter_by(status='Accepted').count()
        rejected_quotations = Quotation.query.filter_by(status='Rejected').count()
        
        # Sales Order statistics
        active_orders = SalesOrder.query.filter_by(status='Active').count()
        completed_orders = SalesOrder.query.filter_by(status='Completed').count()
        
        # Financial statistics
        total_quotation_value = db.session.query(func.sum(Quotation.total_amount)).scalar() or 0
        total_order_value = db.session.query(
            func.sum(Quotation.total_amount)
        ).join(
            SalesOrder, SalesOrder.quotation_id == Quotation.id
        ).scalar() or 0
        
        # Recent activities (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_quotations = Quotation.query.filter(
            Quotation.created_at >= seven_days_ago
        ).count()
        recent_orders = SalesOrder.query.filter(
            SalesOrder.created_at >= seven_days_ago
        ).count()
        
        # Monthly statistics (current month)
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        monthly_quotations = Quotation.query.filter(
            Quotation.created_at >= current_month_start
        ).count()
        monthly_orders = SalesOrder.query.filter(
            SalesOrder.created_at >= current_month_start
        ).count()
        monthly_revenue = db.session.query(
            func.sum(Quotation.total_amount)
        ).join(
            SalesOrder, SalesOrder.quotation_id == Quotation.id
        ).filter(
            SalesOrder.created_at >= current_month_start
        ).scalar() or 0
        
        # Conversion rate
        conversion_rate = 0
        if total_quotations > 0:
            conversion_rate = round((accepted_quotations / total_quotations) * 100, 2)
        
        # Latest activities
        latest_quotations = Quotation.query.order_by(
            Quotation.created_at.desc()
        ).limit(5).all()
        
        latest_orders = SalesOrder.query.order_by(
            SalesOrder.created_at.desc()
        ).limit(5).all()
        
        return jsonify({
            'success': True,
            'data': {
                'counts': {
                    'customers': total_customers,
                    'quotations': total_quotations,
                    'sales_orders': total_sales_orders,
                    'pending_quotations': pending_quotations,
                    'active_orders': active_orders
                },
                'quotation_stats': {
                    'pending': pending_quotations,
                    'accepted': accepted_quotations,
                    'rejected': rejected_quotations
                },
                'order_stats': {
                    'active': active_orders,
                    'completed': completed_orders
                },
                'financial': {
                    'total_quotation_value': total_quotation_value,
                    'total_order_value': total_order_value,
                    'monthly_revenue': monthly_revenue
                },
                'recent': {
                    'quotations': recent_quotations,
                    'orders': recent_orders
                },
                'monthly': {
                    'quotations': monthly_quotations,
                    'orders': monthly_orders
                },
                'conversion_rate': conversion_rate,
                'latest_quotations': [
                    {
                        'number': q.quotation_number,
                        'customer': q.customer.name,
                        'amount': q.total_amount,
                        'status': q.status,
                        'date': q.created_at.strftime('%d-%m-%Y %H:%M')
                    } for q in latest_quotations
                ],
                'latest_orders': [
                    {
                        'number': so.so_number,
                        'customer': so.customer.name,
                        'amount': so.quotation.total_amount,
                        'status': so.status,
                        'date': so.created_at.strftime('%d-%m-%Y %H:%M')
                    } for so in latest_orders
                ],
                'timestamp': datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})