from flask import render_template, redirect, url_for, flash, request
from app.frontend import bp
from app.models import InventoryItem
from flask_login import login_required
from app.frontend.decorators import role_required
from app.extensions import db
from datetime import datetime

@bp.route('/inventory', methods=['GET'])
@login_required
@role_required('admin', 'lab_tech')
def inventory_list():
    items = InventoryItem.query.order_by(InventoryItem.item_name).all()
    return render_template('inventory/list.html', items=items)

@bp.route('/inventory/add', methods=['POST'])
@login_required
@role_required('admin')
def add_inventory_item():
    item_name = request.form.get('item_name')
    category = request.form.get('category')
    stock_quantity = request.form.get('stock_quantity', type=int)
    unit_price = request.form.get('unit_price', type=float)
    expiry_date_str = request.form.get('expiry_date')
    
    expiry_date = None
    if expiry_date_str:
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
    
    if item_name:
        item = InventoryItem(
            item_name=item_name,
            category=category,
            stock_quantity=stock_quantity or 0,
            unit_price=unit_price or 0.0,
            expiry_date=expiry_date
        )
        db.session.add(item)
        db.session.commit()
        flash('Item added to inventory.', 'success')
    else:
        flash('Item name is required.', 'danger')
        
    return redirect(url_for('frontend.inventory_list'))
    
@bp.route('/inventory/<int:item_id>/update', methods=['POST'])
@login_required
@role_required('admin', 'lab_tech')
def update_stock(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    new_stock = request.form.get('new_stock', type=int)
    
    if new_stock is not None and new_stock >= 0:
        item.stock_quantity = new_stock
        db.session.commit()
        flash(f'Stock updated for {item.item_name}', 'success')
    else:
        flash('Invalid stock quantity.', 'warning')
        
    return redirect(url_for('frontend.inventory_list'))
