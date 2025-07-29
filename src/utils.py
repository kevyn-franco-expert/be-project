from flask import request, jsonify
from functools import wraps

def validate_json(*required_fields):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator