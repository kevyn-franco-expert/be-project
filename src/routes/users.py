from flask import Blueprint, request, jsonify
from datetime import datetime
from pydantic import ValidationError
from src.database import DatabaseManager
from src.schemas import UserCreate, UserUpdate, UserResponse

users_bp = Blueprint('users', __name__)
db = DatabaseManager()

@users_bp.route('/users', methods=['POST'])
def create_user():
    try:
        data = UserCreate(**request.get_json())
        
        # Check if email already exists
        check_query = "SELECT id FROM users WHERE email = %s"
        existing_user = db.execute_query(check_query, (data.email,), fetch=True)
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400
        
        query = """
        INSERT INTO users (name, email, phone, created_at)
        VALUES (%s, %s, %s, %s)
        """
        params = (data.name, data.email, data.phone, datetime.now())
        
        result = db.execute_query(query, params)
        if result:
            # Get the created user
            user_query = "SELECT * FROM users WHERE email = %s"
            user_data = db.execute_query(user_query, (data.email,), fetch=True)
            if user_data:
                response = UserResponse(**user_data[0])
                return jsonify(response.dict()), 201
        
        return jsonify({'error': 'Failed to create user'}), 500
        
    except ValidationError as e:
        error_details = []
        for error in e.errors():
            error_details.append({
                'field': error.get('loc', ['unknown'])[0] if error.get('loc') else 'unknown',
                'message': error.get('msg', 'Validation error'),
                'type': error.get('type', 'validation_error')
            })
        return jsonify({'error': 'Validation error', 'details': error_details}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to create user'}), 500

@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    result = db.execute_query(query, (user_id,), fetch=True)
    
    if result:
        response = UserResponse(**result[0])
        return jsonify(response.dict()), 200
    return jsonify({'error': 'User not found'}), 404

@users_bp.route('/users', methods=['GET'])
def get_all_users():
    query = "SELECT * FROM users ORDER BY created_at DESC"
    result = db.execute_query(query, fetch=True)
    
    if result:
        response = [UserResponse(**user).dict() for user in result]
        return jsonify(response), 200
    return jsonify([]), 200

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = UserUpdate(**request.get_json())
        
        # Check if user exists
        check_query = "SELECT id FROM users WHERE id = %s"
        user_exists = db.execute_query(check_query, (user_id,), fetch=True)
        if not user_exists:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if email already exists for another user
        email_query = "SELECT id FROM users WHERE email = %s AND id != %s"
        existing_email = db.execute_query(email_query, (data.email, user_id), fetch=True)
        if existing_email:
            return jsonify({'error': 'Email already exists'}), 400
        
        query = """
        UPDATE users
        SET name = %s, email = %s, phone = %s, updated_at = %s
        WHERE id = %s
        """
        params = (data.name, data.email, data.phone, datetime.now(), user_id)
        
        result = db.execute_query(query, params)
        if result:
            # Get the updated user
            user_query = "SELECT * FROM users WHERE id = %s"
            user_data = db.execute_query(user_query, (user_id,), fetch=True)
            if user_data:
                response = UserResponse(**user_data[0])
                return jsonify(response.dict()), 200
        
        return jsonify({'error': 'Failed to update user'}), 500
        
    except ValidationError as e:
        error_details = []
        for error in e.errors():
            error_details.append({
                'field': error.get('loc', ['unknown'])[0] if error.get('loc') else 'unknown',
                'message': error.get('msg', 'Validation error'),
                'type': error.get('type', 'validation_error')
            })
        return jsonify({'error': 'Validation error', 'details': error_details}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to update user'}), 500

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        # Check if user exists
        check_query = "SELECT id FROM users WHERE id = %s"
        user_exists = db.execute_query(check_query, (user_id,), fetch=True)
        if not user_exists:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user has active bookings
        booking_query = "SELECT COUNT(*) as count FROM bookings WHERE user_id = %s AND status = 'confirmed'"
        active_bookings = db.execute_query(booking_query, (user_id,), fetch=True)
        if active_bookings and active_bookings[0]['count'] > 0:
            return jsonify({'error': 'Cannot delete user with active bookings'}), 400
        
        query = "DELETE FROM users WHERE id = %s"
        result = db.execute_query(query, (user_id,))
        
        if result:
            return jsonify({'message': 'User deleted successfully'}), 200
        return jsonify({'error': 'Failed to delete user'}), 500
        
    except Exception as e:
        return jsonify({'error': 'Failed to delete user'}), 500