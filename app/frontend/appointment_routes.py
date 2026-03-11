from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import ReferralDoctor, Appointment, DoctorSchedule
from app.extensions import db
from datetime import datetime, date, timedelta

bp_appointments = Blueprint('appointments', __name__)

@bp_appointments.route('/book-appointment')
def book_appointment():
    doctors = ReferralDoctor.query.filter_by(is_active=True).all()
    return render_template('appointments/book_appointment.html', doctors=doctors)

@bp_appointments.route('/api/doctor-slots/<int:doctor_id>/<appointment_date>')
def get_doctor_slots(doctor_id, appointment_date):
    try:
        appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        day_name = appointment_date.strftime('%A')
        
        # Get doctor's schedule for the day
        schedule = DoctorSchedule.query.filter_by(
            doctor_id=doctor_id, 
            day_of_week=day_name,
            is_available=True
        ).first()
        
        if not schedule:
            return jsonify({'slots': []})
        
        # Generate time slots (30-minute intervals)
        slots = []
        current_time = datetime.combine(appointment_date, schedule.start_time)
        end_time = datetime.combine(appointment_date, schedule.end_time)
        
        while current_time < end_time:
            # Check if slot is already booked
            existing_appointment = Appointment.query.filter_by(
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                appointment_time=current_time.time(),
                status='confirmed'
            ).first()
            
            if not existing_appointment:
                slots.append({
                    'time': current_time.strftime('%H:%M'),
                    'display': current_time.strftime('%I:%M %p')
                })
            
            current_time += timedelta(minutes=30)
        
        return jsonify({'slots': slots})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp_appointments.route('/book-appointment', methods=['POST'])
def submit_appointment():
    try:
        # Debug form data
        print("Form data:", dict(request.form))
        
        doctor_id = request.form.get('doctor_id')
        print(f"Doctor ID: {doctor_id}")
        
        if not doctor_id:
            flash('Please select a doctor.', 'danger')
            return redirect(url_for('appointments.book_appointment'))
        
        appointment = Appointment(
            patient_name=request.form.get('patient_name'),
            patient_phone=request.form.get('patient_phone'),
            patient_email=request.form.get('patient_email'),
            doctor_id=int(doctor_id),
            appointment_date=datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%d').date(),
            appointment_time=datetime.strptime(request.form.get('appointment_time'), '%H:%M').time(),
            notes=request.form.get('notes'),
            status='confirmed'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        flash(f'Appointment booked successfully! Appointment ID: {appointment.id}', 'success')
        return redirect(url_for('appointments.appointment_confirmation', appointment_id=appointment.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error booking appointment: {str(e)}', 'danger')
        return redirect(url_for('appointments.book_appointment'))

@bp_appointments.route('/appointment-confirmation/<int:appointment_id>')
def appointment_confirmation(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    return render_template('appointments/confirmation.html', appointment=appointment)