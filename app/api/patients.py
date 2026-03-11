from flask import request, jsonify
from app.api import bp
from app.extensions import db
from app.models import Patient
from flask_jwt_extended import jwt_required
from app.api.decorators import role_required

@bp.route('/patients', methods=['GET'])
@jwt_required()
def get_patients():
    patients = Patient.query.all()
    result = []
    for p in patients:
        result.append({
            'id': p.id,
            'patient_code': p.patient_code,
            'name': p.name,
            'phone': p.phone,
            'gender': p.gender,
            'blood_group': p.blood_group,
            'address': p.address
        })
    return jsonify(result), 200

@bp.route('/patients', methods=['POST'])
@jwt_required()
@role_required('admin', 'receptionist')
def register_patient():
    data = request.get_json()
    
    # Simple code generator
    last_patient = Patient.query.order_by(Patient.id.desc()).first()
    new_id = last_patient.id + 1 if last_patient else 1
    p_code = f"PT-{new_id:04d}"
    
    patient = Patient(
        patient_code=p_code,
        name=data['name'],
        phone=data['phone'],
        gender=data.get('gender'),
        blood_group=data.get('blood_group'),
        address=data.get('address')
    )
    
    db.session.add(patient)
    db.session.commit()
    
    return jsonify({'message': 'Patient registered', 'patient_code': p_code, 'id': patient.id}), 201

@bp.route('/patients/<int:id>', methods=['GET'])
@jwt_required()
def get_patient(id):
    p = Patient.query.get_or_404(id)
    return jsonify({
        'id': p.id,
        'patient_code': p.patient_code,
        'name': p.name,
        'phone': p.phone,
        'gender': p.gender,
        'blood_group': p.blood_group,
        'address': p.address
    }), 200
