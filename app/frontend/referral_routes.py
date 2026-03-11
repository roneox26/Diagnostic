from flask import render_template, redirect, url_for, flash, request
from app.frontend import bp
from app.models import ReferralDoctor, ReferralCommission
from flask_login import login_required
from app.frontend.decorators import role_required
from app.extensions import db

@bp.route('/referrals', methods=['GET'])
@login_required
@role_required('admin')
def referrals_list():
    doctors = ReferralDoctor.query.all()
    # Calculate some basic stats
    for doc in doctors:
        doc.total_commissions = sum(c.commission_amount for c in doc.commissions)
        doc.pending_commissions = sum(c.commission_amount for c in doc.commissions if c.status == 'pending')
        
    return render_template('referrals/list.html', doctors=doctors)

@bp.route('/referrals/add', methods=['POST'])
@login_required
@role_required('admin')
def add_doctor():
    name = request.form.get('name')
    hospital = request.form.get('hospital')
    phone = request.form.get('phone')
    commission_rate = request.form.get('commission_rate', type=float)
    
    if name:
        doc = ReferralDoctor(
            name=name,
            hospital=hospital,
            phone=phone,
            commission_rate=commission_rate or 0.0
        )
        db.session.add(doc)
        db.session.commit()
        flash(f'Doctor {name} added to referral system.', 'success')
    else:
        flash('Doctor name is required.', 'danger')
        
    return redirect(url_for('frontend.referrals_list'))

@bp.route('/referrals/<int:doctor_id>/pay', methods=['POST'])
@login_required
@role_required('admin')
def pay_commission(doctor_id):
    doc = ReferralDoctor.query.get_or_404(doctor_id)
    pending_commissions = [c for c in doc.commissions if c.status == 'pending']
    
    for c in pending_commissions:
        c.status = 'paid'
        
    db.session.commit()
    flash(f'Paid pending commissions for Dr. {doc.name}', 'success')
    return redirect(url_for('frontend.referrals_list'))
