from flask import request, jsonify
from app.api import bp
from app.extensions import db
from app.models import TestOrder, TestOrderItem, Test, Patient
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.decorators import role_required

@bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    orders = TestOrder.query.all()
    result = []
    for o in orders:
        result.append({
            'id': o.id,
            'patient_id': o.patient_id,
            'patient_name': o.patient.name if o.patient else 'Unknown',
            'order_date': o.order_date.isoformat() if o.order_date else None,
            'status': o.status,
            'created_by': o.created_by,
            'item_count': len(o.items)
        })
    return jsonify(result), 200

@bp.route('/orders', methods=['POST'])
@jwt_required()
@role_required('admin', 'receptionist')
def create_order():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    patient_id = data.get('patient_id')
    test_ids = data.get('test_ids', []) # list of test IDs
    
    if not patient_id or not test_ids:
        return jsonify({'error': 'patient_id and test_ids are required'}), 400
        
    order = TestOrder(
        patient_id=patient_id,
        created_by=current_user_id,
        status='pending'
    )
    db.session.add(order)
    db.session.flush() # To get order ID
    
    total_price = 0
    for test_id in test_ids:
        test = Test.query.get(test_id)
        if test:
            item = TestOrderItem(
                order_id=order.id,
                test_id=test.id,
                price=test.price
            )
            db.session.add(item)
            total_price += test.price
            
    db.session.commit()
    return jsonify({
        'message': 'Order created', 
        'order_id': order.id,
        'total_estimated': total_price
    }), 201
