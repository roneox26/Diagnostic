@bp.route('/orders/<int:order_id>/collect', methods=['POST'])
@login_required
@role_required('admin', 'receptionist', 'lab_tech')
def collect_sample(order_id):
    order = TestOrder.query.get_or_404(order_id)
    if order.status == 'pending':
        order.status = 'sample_collected'
        db.session.commit()
        flash(f'Sample collected for Order #{order.id}. Sent to Lab!', 'success')
    return redirect(url_for('frontend.orders_list'))
