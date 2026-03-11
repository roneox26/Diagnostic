from flask import render_template, redirect, url_for, flash, request
from app.frontend import bp
from app.models import Invoice, InvoiceItem, TestOrder
from flask_login import login_required
from app.frontend.decorators import role_required
from app.extensions import db

@bp.route('/billing', methods=['GET'])
@login_required
@role_required('admin', 'receptionist')
def invoices_list():
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    # Find orders that don't have invoices yet
    pending_orders = TestOrder.query.filter(
        ~TestOrder.id.in_(db.session.query(Invoice.order_id))
    ).all()
    return render_template('billing/list.html', invoices=invoices, pending_orders=pending_orders)

@bp.route('/billing/print/<int:invoice_id>')
@login_required
def print_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template('billing/print_invoice.html', invoice=invoice)

@bp.route('/billing/create/<int:order_id>', methods=['POST'])
@login_required
def generate_invoice(order_id):
    order = TestOrder.query.get_or_404(order_id)
    
    # Check if invoice already exists
    if order.invoice:
        flash('Invoice already generated for this order.', 'warning')
        return redirect(url_for('frontend.invoices_list'))
        
    total = sum(item.price for item in order.items)
    
    invoice = Invoice(
        patient_id=order.patient_id,
        order_id=order.id,
        total_amount=total,
        discount=0.0,
        paid_amount=0.0,
        payment_status='unpaid'
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
    flash(f'Invoice #{invoice.id} generated successfully.', 'success')
    return redirect(url_for('frontend.invoices_list'))
