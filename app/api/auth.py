from flask import request, jsonify
from app.api import bp
from app.extensions import db, bcrypt
from app.models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

@bp.route('/auth/register', methods=['POST'])
def register_admin():
    # Helper to register first admin. Should be disabled in production or secured.
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
        
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password,
        role=data.get('role', 'admin'),
        name=data.get('name')
    )
    
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and bcrypt.check_password_hash(user.password_hash, data.get('password')):
        if not user.is_active:
            return jsonify({'error': 'Account suspended'}), 403
            
        access_token = create_access_token(
            identity=str(user.id), 
            additional_claims={'role': user.role, 'username': user.username}
        )
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'name': user.name
            }
        }), 200
        
    return jsonify({'error': 'Invalid username or password'}), 401

@bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'name': user.name,
        'phone': user.phone
    }), 200
