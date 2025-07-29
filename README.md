# Vehicle Rental Backend API

A Flask-based microservice for managing vehicle rentals with MySQL database integration. This application provides REST API endpoints for managing users, vehicles, bookings, and generating reports.

## Features

- **Vehicle Management**: Support for small cars (4 capacity), SUVs (7 capacity), and vans (8+ capacity)
- **User Management**: Complete CRUD operations for customer management
- **Booking System**: Vehicle rental booking with business rule validation
- **Availability Checking**: Real-time vehicle availability queries
- **Daily Reports**: Comprehensive booking reports with filtering options
- **Email Notifications**: Automated confirmation and invoice emails
- **Business Rules**: Enforced rental period limits and advance booking constraints

## Business Rules

1. Maximum rental period: 7 days
2. Maximum advance booking: 7 days
3. Payment required at time of booking
4. Automatic invoice generation and email delivery
5. Confirmation emails for advance bookings

## Project Structure

```
vehicle-rental-backend/
├── src/
│   ├── __init__.py
│   ├── app.py              # Flask application factory
│   ├── config.py           # Configuration management
│   ├── database.py         # Database connection manager
│   ├── email_service.py    # Email functionality
│   ├── utils.py            # Utility functions
│   └── routes/
│       ├── __init__.py
│       ├── users.py        # User CRUD endpoints
│       ├── vehicles.py     # Vehicle availability endpoints
│       ├── bookings.py     # Booking management
│       └── reports.py      # Reporting endpoints
├── run.py                  # Application entry point
├── database_schema.sql     # Complete MySQL schema
├── ERD_diagram.md         # Entity Relationship Diagram
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── test_api.py           # API testing script
├── README.md             # This file
└── AI_prompt_history.md  # AI interaction history
```

## Database Schema

The application uses a MySQL database with the following main entities:

- **vehicle_types**: Categories of vehicles with capacity and pricing
- **vehicles**: Individual vehicle records
- **users**: Customer information
- **bookings**: Rental transactions
- **invoices**: Invoice records for bookings

See [https://shorturl.at/bjqxk](https://shorturl.at/bjqxk) for detailed schema documentation.

## Installation

1. **Clone the repository**
   ```bash
   cd vehicle-rental-backend
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL database**
   ```bash
   mysql -u root -p < database_schema.sql
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database and email credentials
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:5000`

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Database Configuration
DB_HOST=localhost
DB_NAME=vehicle_rental
DB_USER=root
DB_PASSWORD=your_password
DB_PORT=3306

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

## Email Functionality

The application automatically sends:
- **Confirmation emails**: For advance bookings
- **Invoice emails**: For all completed bookings

Email templates include:
- Booking details
- Vehicle information
- Pricing breakdown
- Booking reference numbers


## Security Considerations

- SQL injection prevention through parameterized queries
- Input validation and sanitization
- Email format validation
- Business rule enforcement at database level
- Error message sanitization
