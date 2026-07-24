from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import TestOrder, Patient, ReferralDoctor
from app.frontend.decorators import role_required
from datetime import datetime

bp_portal = Blueprint('portal', __name__)

@bp_portal.route('/report-access', methods=['GET', 'POST'])
def public_report_access():
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        search_id = request.form.get('order_id', '').strip()
        
        # Clean phone number - remove spaces, dashes, etc.
        phone = ''.join(filter(str.isdigit, phone))
        
        if not phone or not search_id:
            flash('Mobile number and Patient/Order ID are required.', 'danger')
            return render_template('portal/report_access.html')
            
        # Try to find by Order ID first
        order = None
        if search_id.isdigit():
            order = TestOrder.query.get(search_id)
            
        # If not found by Order ID, try by Patient Code
        if not order:
            patient = Patient.query.filter_by(patient_code=search_id).first()
            if patient:
                # Get the latest completed order for this patient
                order = TestOrder.query.filter_by(
                    patient_id=patient.id, 
                    status='completed'
                ).order_by(TestOrder.order_date.desc()).first()
                
        if order:
            # Verify phone matches
            order_phone = ''.join(filter(str.isdigit, order.patient.phone or ''))
                
        if not order or (''.join(filter(str.isdigit, order.patient.phone or '')) != phone):
            flash('Invalid Patient/Order ID or Mobile number. Please check your details.', 'danger')
            return render_template('portal/report_access.html')
            
        if order.status != 'completed':
            flash('Report is not ready yet. Please check back later.', 'warning')
            return render_template('portal/report_access.html')
            
        # Redirect to preview report
        return redirect(url_for('portal.public_preview_report', order_id=order.id))
        
    return render_template('portal/report_access.html')

@bp_portal.route('/report-preview/<int:order_id>')
def public_preview_report(order_id):
    order = TestOrder.query.get_or_404(order_id)
    if order.status != 'completed':
        flash('Report is not ready yet.', 'warning')
        return redirect(url_for('portal.public_report_access'))
    items = [item for item in order.items if item.result]
    return render_template('portal/public_report_preview.html', order=order, patient=order.patient, items=items)

@bp_portal.route('/portal/patient')
@login_required
@role_required('patient', 'admin')
def patient_dashboard():
    # Find the patient record linked to the current user
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient and current_user.role != 'admin':
        flash("Patient record not found for your account.", "danger")
        return redirect(url_for('frontend.index'))
    
    orders = patient.orders if patient else []
    return render_template('portal/patient_dashboard.html', patient=patient, orders=orders)

@bp_portal.route('/portal/doctor')
@login_required
@role_required('doctor', 'admin')
def doctor_dashboard():
    # Find the doctor record linked to the current user
    doctor = ReferralDoctor.query.filter_by(user_id=current_user.id).first()
    if not doctor and current_user.role != 'admin':
        flash("Doctor record not found for your account.", "danger")
        return redirect(url_for('frontend.index'))
    
    # Get all orders referred by this doctor
    orders = TestOrder.query.filter_by(referral_id=doctor.id).order_by(TestOrder.order_date.desc()).all() if doctor else []
    
    return render_template('portal/doctor_dashboard.html', doctor=doctor, orders=orders)
