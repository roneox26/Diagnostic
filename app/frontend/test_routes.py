from flask import render_template, redirect, url_for, flash, request
from app.frontend import bp
from app.models import TestCategory, Test
from flask_login import login_required
from app.frontend.decorators import role_required
from app.extensions import db

@bp.route('/tests', methods=['GET'])
@login_required
@role_required('admin')
def tests_list():
    tests = Test.query.all()
    categories = TestCategory.query.all()
    return render_template('tests/list.html', tests=tests, categories=categories)

@bp.route('/tests/add', methods=['POST'])
@login_required
def add_test():
    test_name = request.form.get('test_name')
    category_id = request.form.get('category_id')
    price = request.form.get('price')
    sample_type = request.form.get('sample_type')
    
    if test_name and category_id and price:
        test = Test(
            category_id=category_id,
            test_name=test_name,
            price=float(price),
            sample_type=sample_type
        )
        db.session.add(test)
        db.session.commit()
        flash('New test added successfully', 'success')
    else:
        flash('Please fill all required fields', 'danger')
        
    return redirect(url_for('frontend.tests_list'))

@bp.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name')
    if name:
        category = TestCategory(name=name)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully', 'success')
    return redirect(url_for('frontend.tests_list'))
