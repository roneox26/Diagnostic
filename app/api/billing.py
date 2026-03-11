from flask import request, jsonify
from app.api import bp
from app.extensions import db
from app.models import Invoice, InvoiceItem, TestOrder
from flask_jwt_extended import jwt_required
from app.api.decorators import role_required

@bp.route('/invoices', methods=['GET'])
@jwt_required()
@role_required('admin', 'receptionist')
def get_invoices():
    invoices = Invoice.query.all()
    result = []
    for inv in invoices:
        result.append({
            'id': inv.id,
            'patient_id': inv.patient_id,
            'total_amount': inv.total_amount,
            'paid_amount': inv.paid_amount,
            'payment_status': inv.payment_status
        })
    return jsonify(result), 200

@bp.route('/invoices', methods=['POST'])
@jwt_required()
@role_required('admin', 'receptionist')
def create_invoice():
    data = request.get_json()
    order = TestOrder.query.get_or_404(data['order_id'])
    
    total = sum(item.price for item in order.items)
    discount = data.get('discount', 0.0)
    paid = data.get('paid_amount', 0.0)
    
    status = 'paid' if paid >= (total - discount) else 'partial' if paid > 0 else 'unpaid'
    
    invoice = Invoice(
        patient_id=order.patient_id,
        order_id=order.id,
        total_amount=total,
        discount=discount,
        paid_amount=paid,
        payment_status=status
    )
    
    db.session.add(invoice)
    db.session.flush()
    
    for item in order.items:
        inv_item = InvoiceItem(
            invoice_id=invoice.id,
            test_name=item.test.test_name,
            price=item.price
        )
        db.session.add(inv_item)
        
    db.session.commit()
    return jsonify({'message': 'Invoice created', 'invoice_id': invoice.id}), 201
