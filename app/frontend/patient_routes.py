from flask import render_template, redirect, url_for, flash, request
from app.frontend import bp
from app.models import Patient
from flask_login import login_required
from app.frontend.decorators import role_required
from app.extensions import db

@bp.route('/patients', methods=['GET'])
@login_required
@role_required('admin', 'receptionist')
def patients_list():
    patients = Patient.query.order_by(Patient.created_at.desc()).all()
    return render_template('patients/list.html', patients=patients)

@bp.route('/patients/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'receptionist')
def add_patient():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        blood_group = request.form.get('blood_group')
        address = request.form.get('address')
        
        last_patient = Patient.query.order_by(Patient.id.desc()).first()
        new_id = last_patient.id + 1 if last_patient else 1
        p_code = f"PT-{new_id:04d}"
        
        patient = Patient(
            patient_code=p_code,
            name=name,
            phone=phone,
            gender=gender,
            blood_group=blood_group,
            address=address
        )
        
        db.session.add(patient)
        db.session.commit()
        
        flash(f'Patient registered successfully with ID {p_code}', 'success')
        return redirect(url_for('frontend.patients_list'))
        
    return render_template('patients/add.html')
