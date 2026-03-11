from flask import request, jsonify
from app.api import bp
from app.extensions import db
from app.models import TestCategory, Test
from flask_jwt_extended import jwt_required
from app.api.decorators import role_required

@bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    categories = TestCategory.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories]), 200

@bp.route('/categories', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_category():
    data = request.get_json()
    category = TestCategory(name=data['name'])
    db.session.add(category)
    db.session.commit()
    return jsonify({'message': 'Category created', 'id': category.id}), 201

@bp.route('/tests', methods=['GET'])
@jwt_required()
def get_tests():
    tests = Test.query.all()
    result = []
    for t in tests:
        result.append({
            'id': t.id,
            'category_id': t.category_id,
            'category_name': t.category.name if t.category else None,
            'test_name': t.test_name,
            'price': t.price,
            'sample_type': t.sample_type,
            'description': t.description
        })
    return jsonify(result), 200

@bp.route('/tests', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_test():
    data = request.get_json()
    test = Test(
        category_id=data['category_id'],
        test_name=data['test_name'],
        price=data['price'],
        sample_type=data.get('sample_type'),
        description=data.get('description')
    )
    db.session.add(test)
    db.session.commit()
    return jsonify({'message': 'Test created', 'id': test.id}), 201
