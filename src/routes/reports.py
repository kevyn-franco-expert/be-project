from flask import Blueprint, request, jsonify
from datetime import datetime
from pydantic import ValidationError
from src.database import DatabaseManager
from src.schemas import DailyReportQuery, DailyReportResponse

reports_bp = Blueprint('reports', __name__)
db = DatabaseManager()

@reports_bp.route('/reports/daily', methods=['GET'])
def daily_report():
    try:
        # Parse query parameters
        query_params = {
            'date': request.args.get('date'),
            'vehicle_type': request.args.get('vehicle_type')
        }
        
        # Remove None values
        query_params = {k: v for k, v in query_params.items() if v is not None}
        
        # Convert string date to date object
        if 'date' in query_params:
            query_params['date'] = datetime.strptime(query_params['date'], '%Y-%m-%d').date()
        
        # Validate using Pydantic
        report_query = DailyReportQuery(**query_params)
        
        # Convert back to string for SQL query
        date_str = report_query.date.strftime('%Y-%m-%d')
        
        base_query = """
        SELECT
            b.id as booking_id,
            b.pickup_date,
            b.return_date,
            b.total_amount,
            b.status,
            u.name as customer_name,
            u.email as customer_email,
            v.model as vehicle_model,
            v.license_plate,
            vt.name as vehicle_type,
            vt.capacity
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN vehicles v ON b.vehicle_id = v.id
        JOIN vehicle_types vt ON v.type_id = vt.id
        WHERE DATE(b.pickup_date) = %s OR DATE(b.return_date) = %s
        """
        params = [date_str, date_str]
        
        if report_query.vehicle_type:
            base_query += " AND vt.name = %s"
            params.append(report_query.vehicle_type.value)
        
        base_query += " ORDER BY b.pickup_date"
        
        result = db.execute_query(base_query, params, fetch=True)
        
        # Convert result to Pydantic models for validation
        if result:
            validated_results = []
            for row in result:
                try:
                    validated_row = DailyReportResponse(**row)
                    validated_results.append(validated_row.dict())
                except ValidationError:
                    # If validation fails, return raw data
                    validated_results.append(row)
            return jsonify(validated_results), 200
        
        return jsonify([]), 200
        
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
        return jsonify({'error': 'Failed to generate report'}), 500