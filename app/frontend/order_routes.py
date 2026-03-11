from flask import render_template, redirect, url_for, flash, request
from app.frontend import bp
from app.models import TestOrder, TestOrderItem, Patient, Test, Sample
from app.services.barcode_service import BarcodeService
from app.services.notification_service import NotificationService
from flask_login import login_required, current_user
from app.frontend.decorators import role_required
from app.extensions import db

@bp.route('/orders', methods=['GET'])
@login_required
@role_required('admin', 'receptionist')
def orders_list():
    orders = TestOrder.query.order_by(TestOrder.order_date.desc()).all()
    return render_template('orders/list.html', orders=orders)

@bp.route('/orders/new', methods=['GET', 'POST'])
@login_required
def new_order():
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        test_ids = request.form.getlist('test_ids')
        
        if not patient_id or not test_ids:
            flash('Please select a patient and at least one test.', 'warning')
            return redirect(url_for('frontend.new_order'))
            
        order = TestOrder(
            patient_id=patient_id,
            created_by=current_user.id
        )
        db.session.add(order)
        db.session.flush()
        
        for tid in test_ids:
            test = Test.query.get(tid)
            if test:
                item = TestOrderItem(
                    order_id=order.id,
                    test_id=test.id,
                    price=test.price
                )
                db.session.add(item)
                
        db.session.commit()
        flash(f'Order #{order.id} booked successfully!', 'success')
        return redirect(url_for('frontend.orders_list'))
        
    patients = Patient.query.all()
    tests = Test.query.all()
    return render_template('orders/new.html', patients=patients, tests=tests)
@bp.route('/orders/<int:order_id>/collect', methods=['POST'])
@login_required
@role_required('admin', 'receptionist', 'lab_tech')
def collect_sample(order_id):
    order = TestOrder.query.get_or_404(order_id)
    if order.status == 'pending':
        # Create a sample record
        sample = Sample(
            order_id=order.id,
            sample_type="General", # This could be dynamic based on tests
            collector_id=current_user.id
        )
        db.session.add(sample)
        db.session.flush()
        
        # Generate barcode value based on order and sample
        barcode_value = f"SMP-{order.id}-{sample.id}"
        sample.barcode = barcode_value
        
        # Generate barcode image
        BarcodeService.generate_sample_barcode(sample.id, barcode_value)
        
        order.status = 'sample_collected'
        db.session.commit()
        
        # Send notification to patient
        NotificationService.send_collection_alert(order.patient.phone, order.patient.name, order.id)
        
        flash(f'Sample collected for Order #{order.id}. Barcode generated: {barcode_value}', 'success')
    return redirect(url_for('frontend.orders_list'))
