from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import TestOrder, Patient, ReferralDoctor
from app.frontend.decorators import role_required
from datetime import datetime

bp_portal = Blueprint('portal', __name__)

@bp_portal.route('/create-sample-doctors')
def create_sample_doctors():
    from app.models import ReferralDoctor
    from app.extensions import db
    
    try:
        doctors_data = [
            {'doctor_name': 'Ahmed Rahman', 'specialization': 'Cardiologist', 'hospital_name': 'MedCare Heart Center', 'phone': '01711111111'},
            {'doctor_name': 'Fatima Khan', 'specialization': 'Gynecologist', 'hospital_name': 'MedCare Women Care', 'phone': '01722222222'},
            {'doctor_name': 'Mohammad Ali', 'specialization': 'Neurologist', 'hospital_name': 'MedCare Neuro Center', 'phone': '01733333333'},
            {'doctor_name': 'Rashida Begum', 'specialization': 'Pediatrician', 'hospital_name': 'MedCare Child Care', 'phone': '01744444444'}
        ]
        
        for doc_data in doctors_data:
            existing = ReferralDoctor.query.filter_by(doctor_name=doc_data['doctor_name']).first()
            if not existing:
                doctor = ReferralDoctor(
                    doctor_name=doc_data['doctor_name'],
                    name=doc_data['doctor_name'],  # For backward compatibility
                    specialization=doc_data['specialization'],
                    hospital_name=doc_data['hospital_name'],
                    hospital=doc_data['hospital_name'],  # For backward compatibility
                    phone=doc_data['phone'],
                    is_active=True
                )
                db.session.add(doctor)
        
        db.session.commit()
        return "Sample doctors created successfully!"
        
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}"

@bp_portal.route('/create-sample-data')
def create_sample_data():
    from app.models import Patient, TestOrder, Test, TestCategory, TestOrderItem, TestResult
    from app.extensions import db
    from datetime import date
    
    try:
        # Create test category
        category = TestCategory.query.first()
        if not category:
            category = TestCategory(name='Blood Test')
            db.session.add(category)
            db.session.flush()
        
        # Create test
        test = Test.query.first()
        if not test:
            test = Test(
                category_id=category.id,
                test_name='Complete Blood Count',
                price=500.0,
                sample_type='Blood'
            )
            db.session.add(test)
            db.session.flush()
        
        # Create patient
        patient = Patient(
            patient_code='P001',
            name='John Doe',
            phone='01712345678',
            gender='Male',
            date_of_birth=date(1990, 1, 1)
        )
        db.session.add(patient)
        db.session.flush()
        
        # Create order
        from app.models import User
        user = User.query.first()
        if user:
            order = TestOrder(
                patient_id=patient.id,
                created_by=user.id,
                status='completed'
            )
            db.session.add(order)
            db.session.flush()
            
            # Create order item
            item = TestOrderItem(
                order_id=order.id,
                test_id=test.id,
                price=500.0
            )
            db.session.add(item)
            db.session.flush()
            
            # Create test result
            result = TestResult(
                order_item_id=item.id,
                result_text='Normal',
                technician_id=user.id
            )
            db.session.add(result)
            
            db.session.commit()
            return f"Sample data created! Patient Code: P001, Phone: 01712345678, Order ID: {order.id}"
        else:
            return "No user found. Please create a user first."
            
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}"

@bp_portal.route('/public/preview/<int:order_id>')
def public_preview_report(order_id):
    order = TestOrder.query.get_or_404(order_id)
    report_data = {
        'order': order,
        'patient': order.patient,
        'items': [item for item in order.items if item.result],
        'date_generated': datetime.now().strftime('%Y-%m-%d %I:%M %p')
    }
    return render_template('portal/public_report_preview.html', **report_data)

@bp_portal.route('/test-db')
def test_db():
    from app.models import Patient, TestOrder
    
    # Get all patients and orders
    patients = Patient.query.all()
    orders = TestOrder.query.all()
    
    result = "<h3>Database Contents:</h3>"
    
    result += "<h4>Patients:</h4><ul>"
    for p in patients:
        result += f"<li>ID: {p.id}, Code: {p.patient_code}, Name: {p.name}, Phone: {p.phone}</li>"
    result += "</ul>"
    
    result += "<h4>Orders:</h4><ul>"
    for o in orders:
        result += f"<li>Order ID: {o.id}, Patient: {o.patient.name if o.patient else 'None'}, Status: {o.status}, Phone: {o.patient.phone if o.patient else 'None'}</li>"
    result += "</ul>"
    
    return result

@bp_portal.route('/debug-data')
def debug_data():
    from app.models import Patient, TestOrder
    
    patients = Patient.query.all()
    orders = TestOrder.query.all()
    
    debug_info = {
        'patients': [(p.id, p.patient_code, p.phone, p.name) for p in patients],
        'orders': [(o.id, o.patient_id, o.status, o.patient.phone if o.patient else 'No patient') for o in orders]
    }
    
    return f"<pre>{debug_info}</pre>"

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
            
        # Debug: Print search parameters
        print(f"Searching with Phone: {phone}, ID: {search_id}")
        
        # Try to find by Order ID first
        order = None
        if search_id.isdigit():
            order = TestOrder.query.get(search_id)
            print(f"Order found by ID: {order}")
            
        # If not found by Order ID, try by Patient Code
        if not order:
            patient = Patient.query.filter_by(patient_code=search_id).first()
            print(f"Patient found by code: {patient}")
            if patient:
                # Get the latest completed order for this patient
                order = TestOrder.query.filter_by(
                    patient_id=patient.id, 
                    status='completed'
                ).order_by(TestOrder.order_date.desc()).first()
                print(f"Latest completed order: {order}")
                
        if order:
            # Clean both phone numbers for comparison
            order_phone = ''.join(filter(str.isdigit, order.patient.phone or ''))
            print(f"Order patient phone: {order_phone}, Input phone: {phone}")
            print(f"Order status: {order.status}")
                
        if not order or (''.join(filter(str.isdigit, order.patient.phone or '')) != phone):
            flash('Invalid Patient/Order ID or Mobile number. Please check your details.', 'danger')
            return render_template('portal/report_access.html')
            
        if order.status != 'completed':
            flash('Report is not ready yet. Please check back later.', 'warning')
            return render_template('portal/report_access.html')
            
        # Redirect to preview report
        return redirect(url_for('portal.public_preview_report', order_id=order.id))
        
    return render_template('portal/report_access.html')

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
