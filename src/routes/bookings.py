from flask import Blueprint, request, jsonify
from datetime import datetime, date
import uuid
from pydantic import ValidationError
from src.database import DatabaseManager
from src.email_service import EmailService
from src.schemas import BookingCreate, BookingResponse

bookings_bp = Blueprint('bookings', __name__)
db = DatabaseManager()
email_service = EmailService()

@bookings_bp.route('/bookings', methods=['POST'])
def create_booking():
    try:
        # Parse and validate input data
        request_data = request.get_json()
        
        # Convert string dates to date objects for validation
        if 'pickup_date' in request_data:
            request_data['pickup_date'] = datetime.strptime(request_data['pickup_date'], '%Y-%m-%d').date()
        if 'return_date' in request_data:
            request_data['return_date'] = datetime.strptime(request_data['return_date'], '%Y-%m-%d').date()
        
        data = BookingCreate(**request_data)
        
        # Convert back to strings for SQL queries
        pickup_date_str = data.pickup_date.strftime('%Y-%m-%d')
        return_date_str = data.return_date.strftime('%Y-%m-%d')
        
        # Check if user exists
        user_check_query = "SELECT id FROM users WHERE id = %s"
        user_exists = db.execute_query(user_check_query, (data.user_id,), fetch=True)
        if not user_exists:
            return jsonify({'error': 'User not found'}), 404
        
        # Check vehicle availability
        availability_query = """
        SELECT COUNT(*) as conflicts FROM bookings
        WHERE vehicle_id = %s AND status = 'confirmed' AND (
            (pickup_date <= %s AND return_date >= %s) OR
            (pickup_date <= %s AND return_date >= %s) OR
            (pickup_date >= %s AND pickup_date <= %s)
        )
        """
        conflicts = db.execute_query(availability_query,
            (data.vehicle_id, pickup_date_str, pickup_date_str,
             return_date_str, return_date_str, pickup_date_str, return_date_str),
            fetch=True)
        
        if conflicts and conflicts[0]['conflicts'] > 0:
            return jsonify({'error': 'Vehicle not available for selected dates'}), 400
        
        # Get vehicle pricing
        vehicle_query = """
        SELECT v.*, vt.daily_rate
        FROM vehicles v
        JOIN vehicle_types vt ON v.type_id = vt.id
        WHERE v.id = %s
        """
        vehicle = db.execute_query(vehicle_query, (data.vehicle_id,), fetch=True)
        
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        days = (data.return_date - data.pickup_date).days
        total_amount = float(days * vehicle[0]['daily_rate'])
        
        # Create booking
        booking_id = str(uuid.uuid4())
        booking_query = """
        INSERT INTO bookings (id, user_id, vehicle_id, pickup_date, return_date, total_amount, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, 'confirmed', %s)
        """
        
        result = db.execute_query(booking_query,
            (booking_id, data.user_id, data.vehicle_id,
             pickup_date_str, return_date_str, total_amount, datetime.now()))
        
        if result:
            # Get user email for confirmation
            user_query = "SELECT email, name FROM users WHERE id = %s"
            user = db.execute_query(user_query, (data.user_id,), fetch=True)
            
            if user:
                # Send confirmation email
                days_in_advance = (data.pickup_date - date.today()).days
                if days_in_advance > 0:
                    email_service.send_booking_confirmation(
                        user[0]['email'], user[0]['name'], booking_id,
                        vehicle[0]['model'], pickup_date_str, return_date_str, total_amount
                    )
            
            return jsonify({
                'message': 'Booking created successfully',
                'booking_id': booking_id,
                'total_amount': total_amount
            }), 201
        
        return jsonify({'error': 'Failed to create booking'}), 500
        
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
        return jsonify({'error': 'Failed to create booking'}), 500