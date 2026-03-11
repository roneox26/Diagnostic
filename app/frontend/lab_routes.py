from flask import render_template, redirect, url_for, flash, request
from app.frontend import bp
from app.models import TestOrder, TestOrderItem, TestResult, TestReagentConsumption
from flask_login import login_required, current_user
from app.services.lis_service import LISService
from app.frontend.decorators import role_required
from app.extensions import db

@bp.route('/lab/pending', methods=['GET'])
@login_required
@role_required('admin', 'lab_tech')
def pending_lab_work():
    # Get orders where samples are collected but not all results entered
    orders = TestOrder.query.filter(TestOrder.status.in_(['sample_collected', 'processing'])).all()
    return render_template('lab/pending.html', orders=orders)

@bp.route('/lab/enter-result/<int:item_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'lab_tech')
def enter_result(item_id):
    item = TestOrderItem.query.get_or_404(item_id)
    
    if request.method == 'POST':
        result_text = request.form.get('result_text')
        
        if not item.result:
            result = TestResult(
                order_item_id=item.id,
                result_text=result_text,
                technician_id=current_user.id
            )
            db.session.add(result)
            
            # Deduct reagents for this test
            for consumption in item.test.reagent_requirements:
                if consumption.item.stock_quantity >= consumption.quantity_consumed:
                    consumption.item.stock_quantity -= int(consumption.quantity_consumed)
                else:
                    flash(f"Warning: Low stock for {consumption.item.item_name}!", "warning")
        else:
            item.result.result_text = result_text
            item.result.technician_id = current_user.id
            
        db.session.commit()
        
        # Check if all items in the order have results to mark order as completed
        order = item.order
        all_completed = all(order_item.result is not None for order_item in order.items)
        if all_completed:
            order.status = 'completed'
            db.session.commit()
            
        flash(f'Result saved for {item.test.test_name}', 'success')
        return redirect(url_for('frontend.pending_lab_work'))
        
    return render_template('lab/enter_result.html', item=item)

@bp.route('/lab/lis-import', methods=['POST'])
@login_required
@role_required('admin', 'lab_tech')
def trigger_lis_import():
    count = LISService.process_machine_files()
    flash(f'LIS Import completed. {count} files processed.', 'success')
    return redirect(url_for('frontend.pending_lab_work'))
