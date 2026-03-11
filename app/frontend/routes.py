from flask import render_template, redirect, url_for, flash, request
from app.frontend import bp
from app.models import User, Patient, TestOrder, ReferralDoctor, Appointment
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import bcrypt, db
from app.frontend.decorators import role_required

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('frontend.dashboard'))
    return render_template('public_home.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('frontend.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash("Account suspended.", "danger")
                return redirect(url_for('frontend.login'))
                
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('frontend.dashboard'))
            
        flash('Invalid username or password', 'danger')
        
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('frontend.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    from datetime import date
    from app.extensions import db
    from app.models import Patient, TestOrder, Invoice
    
    today = date.today()
    today_patients = Patient.query.filter(db.func.date(Patient.created_at) == today).count()
    today_tests = TestOrder.query.filter(db.func.date(TestOrder.order_date) == today).count()
    pending_reports = TestOrder.query.filter(TestOrder.status != 'completed').count()
    revenue = db.session.query(db.func.sum(Invoice.total_amount)).filter(db.func.date(Invoice.created_at) == today).scalar() or 0.0
    
    recent_orders = TestOrder.query.order_by(TestOrder.order_date.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
        today_patients=today_patients, 
        today_tests=today_tests, 
        pending_reports=pending_reports, 
        revenue=revenue,
        recent_orders=recent_orders
    )

@bp.route('/orders/view/<int:order_id>')
@login_required
def view_order(order_id):
    order = TestOrder.query.get_or_404(order_id)
    return render_template('orders/view.html', order=order)

@bp.route('/doctors-management', methods=['GET'])
@login_required
@role_required('admin')
def doctors_list():
    doctors = ReferralDoctor.query.all()
    return render_template('doctors/list.html', doctors=doctors)

@bp.route('/doctors-management/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_doctor_admin():
    if request.method == 'POST':
        try:
            doctor = ReferralDoctor(
                doctor_name=request.form.get('doctor_name'),
                name=request.form.get('doctor_name'),
                specialization=request.form.get('specialization'),
                hospital_name=request.form.get('hospital_name'),
                hospital=request.form.get('hospital_name'),
                phone=request.form.get('phone'),
                commission_rate=float(request.form.get('commission_rate', 0)),
                is_active=True
            )
            
            db.session.add(doctor)
            db.session.commit()
            
            flash(f'Doctor {doctor.doctor_name} added successfully!', 'success')
            return redirect(url_for('frontend.doctors_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding doctor: {str(e)}', 'danger')
    
    return render_template('doctors/add.html')

@bp.route('/appointments-admin')
@login_required
@role_required('admin', 'receptionist')
def appointments_admin():
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    return render_template('appointments/admin_list.html', appointments=appointments)

@bp.route('/appointments/update-status/<int:appointment_id>/<status>')
@login_required
@role_required('admin', 'receptionist')
def update_appointment_status(appointment_id, status):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = status
    db.session.commit()
    flash(f'Appointment status updated to {status}', 'success')
    return redirect(url_for('frontend.appointments_admin'))
