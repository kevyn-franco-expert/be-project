from flask import Blueprint, request, jsonify
from datetime import datetime, date
from pydantic import ValidationError
from src.database import DatabaseManager
from src.schemas import AvailabilityQuery, VehicleAvailabilityResponse

vehicles_bp = Blueprint('vehicles', __name__)
db = DatabaseManager()

@vehicles_bp.route('/vehicles/availability', methods=['GET'])
def check_availability():
    try:
        # Parse query parameters
        query_params = {
            'pickup_date': request.args.get('pickup_date'),
            'return_date': request.args.get('return_date'),
            'vehicle_type': request.args.get('type'),
            'vehicle_id': request.args.get('vehicle_id')
        }
        
        # Remove None values
        query_params = {k: v for k, v in query_params.items() if v is not None}
        
        # Convert string dates to date objects
        if 'pickup_date' in query_params:
            query_params['pickup_date'] = datetime.strptime(query_params['pickup_date'], '%Y-%m-%d').date()
        if 'return_date' in query_params:
            query_params['return_date'] = datetime.strptime(query_params['return_date'], '%Y-%m-%d').date()
        if 'vehicle_id' in query_params:
            query_params['vehicle_id'] = int(query_params['vehicle_id'])
        
        # Validate using Pydantic
        availability_query = AvailabilityQuery(**query_params)
        
        # Convert back to strings for SQL query
        pickup_date_str = availability_query.pickup_date.strftime('%Y-%m-%d')
        return_date_str = availability_query.return_date.strftime('%Y-%m-%d')
        
        # Build query based on parameters
        if availability_query.vehicle_id:
            query = """
            SELECT v.*, vt.name as type_name, vt.capacity
            FROM vehicles v
            JOIN vehicle_types vt ON v.type_id = vt.id
            WHERE v.id = %s AND v.id NOT IN (
                SELECT vehicle_id FROM bookings
                WHERE status = 'confirmed' AND (
                    (pickup_date <= %s AND return_date >= %s) OR
                    (pickup_date <= %s AND return_date >= %s) OR
                    (pickup_date >= %s AND pickup_date <= %s)
                )
            )
            """
            params = (availability_query.vehicle_id, pickup_date_str, pickup_date_str,
                     return_date_str, return_date_str, pickup_date_str, return_date_str)
        else:
            base_query = """
            SELECT v.*, vt.name as type_name, vt.capacity
            FROM vehicles v
            JOIN vehicle_types vt ON v.type_id = vt.id
            WHERE v.id NOT IN (
                SELECT vehicle_id FROM bookings
                WHERE status = 'confirmed' AND (
                    (pickup_date <= %s AND return_date >= %s) OR
                    (pickup_date <= %s AND return_date >= %s) OR
                    (pickup_date >= %s AND pickup_date <= %s)
                )
            )
            """
            params = [pickup_date_str, pickup_date_str, return_date_str, return_date_str, pickup_date_str, return_date_str]
            
            if availability_query.vehicle_type:
                base_query += " AND vt.name = %s"
                params.append(availability_query.vehicle_type.value)
            
            query = base_query + " ORDER BY vt.name, v.model"
        
        result = db.execute_query(query, params, fetch=True)
        return jsonify(result or []), 200
        
    except ValidationError as e:
        error_details = []
        for error in e.errors():
            error_details.append({
                'field': error.get('loc', ['unknown'])[0] if error.get('loc') else 'unknown',
                'message': error.get('msg', 'Validation error'),
                'type': error.get('type', 'validation_error')
            })
        return jsonify({'error': 'Validation error', 'details': error_details}), 400
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to check availability'}), 500