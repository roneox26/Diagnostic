from flask import jsonify
from app.api import bp
from app.extensions import db
from app.models import Patient, TestOrder, Invoice
from flask_jwt_extended import jwt_required
from app.api.decorators import role_required
from datetime import datetime, date

@bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_dashboard_stats():
    # Example logic for dashboard metrics
    today = date.today()
    
    today_patients = Patient.query.filter(db.func.date(Patient.created_at) == today).count()
    today_tests = TestOrder.query.filter(db.func.date(TestOrder.order_date) == today).count()
    
    pending_reports = TestOrder.query.filter(TestOrder.status != 'completed').count()
    
    revenue = db.session.query(db.func.sum(Invoice.paid_amount))\
                .filter(db.func.date(Invoice.created_at) == today)\
                .scalar() or 0.0
                
    return jsonify({
        'today_patients': today_patients,
        'today_tests': today_tests,
        'pending_reports': pending_reports,
        'daily_revenue': revenue
    }), 200
