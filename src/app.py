from flask import Flask, jsonify
from pydantic import ValidationError
from src.config import Config
from src.routes.users import users_bp
from src.routes.vehicles import vehicles_bp
from src.routes.bookings import bookings_bp
from src.routes.reports import reports_bp

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(users_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(reports_bp)
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        error_details = []
        for err in error.errors():
            error_details.append({
                'field': err.get('loc', ['unknown'])[0] if err.get('loc') else 'unknown',
                'message': err.get('msg', 'Validation error'),
                'type': err.get('type', 'validation_error')
            })
        return jsonify({'error': 'Validation error', 'details': error_details}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/', methods=['GET'])
    def health_check():
        return jsonify({
            'message': 'Vehicle Rental API is running',
            'status': 'healthy',
            'endpoints': {
                'users': '/users',
                'availability': '/vehicles/availability',
                'bookings': '/bookings',
                'reports': '/reports/daily'
            }
        }), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)