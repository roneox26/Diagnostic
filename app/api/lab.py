from flask import request, jsonify
from app.api import bp
from app.extensions import db
from app.models import Sample, TestOrder, TestOrderItem, TestResult
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.decorators import role_required

@bp.route('/samples', methods=['POST'])
@jwt_required()
@role_required('admin', 'receptionist', 'lab_tech')
def collect_sample():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    order = TestOrder.query.get_or_404(data['order_id'])
    
    sample = Sample(
        order_id=order.id,
        sample_type=data['sample_type'],
        collector_id=current_user_id,
        status='collected'
    )
    
    order.status = 'sample_collected'
    db.session.add(sample)
    db.session.commit()
    
    return jsonify({'message': 'Sample collected', 'sample_id': sample.id}), 201

@bp.route('/results', methods=['POST'])
@jwt_required()
@role_required('admin', 'lab_tech')
def enter_result():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    item = TestOrderItem.query.get_or_404(data['order_item_id'])
    
    result = TestResult(
        order_item_id=item.id,
        result_text=data['result_text'],
        technician_id=current_user_id
    )
    
    db.session.add(result)
    
    # Check if all items in order have results, then update order status
    order = item.order
    # Simple check, can be improved
    order.status = 'processing'
    
    db.session.commit()
    
    return jsonify({'message': 'Result entered', 'result_id': result.id}), 201

@bp.route('/reports/<int:order_id>', methods=['GET'])
@jwt_required()
def get_report(order_id):
    # This endpoint would typically generate or return a link to the PDF
    order = TestOrder.query.get_or_404(order_id)
    
    report_data = {
        'order_id': order.id,
        'patient_name': order.patient.name,
        'status': order.status,
        'results': []
    }
    
    for item in order.items:
        if item.result:
            report_data['results'].append({
                'test_name': item.test.test_name,
                'result_text': item.result.result_text,
                'technician': item.result.technician_id # can map to name
            })
            
    return jsonify(report_data), 200
