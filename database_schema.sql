-- Vehicle Rental Database Schema
-- This schema implements a vehicle rental system with proper constraints and indexes

-- Create database
CREATE DATABASE IF NOT EXISTS vehicle_rental;
USE vehicle_rental;

-- Vehicle Types Table
CREATE TABLE IF NOT EXISTS vehicle_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    capacity INT NOT NULL,
    daily_rate DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_capacity CHECK (capacity > 0),
    CONSTRAINT chk_daily_rate CHECK (daily_rate > 0),
    CONSTRAINT chk_vehicle_type_name CHECK (name IN ('small_car', 'suv', 'van'))
);

-- Vehicles Table
CREATE TABLE IF NOT EXISTS vehicles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type_id INT NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    license_plate VARCHAR(20) NOT NULL UNIQUE,
    color VARCHAR(30),
    status ENUM('available', 'rented', 'maintenance') DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Foreign Keys
    FOREIGN KEY (type_id) REFERENCES vehicle_types(id) ON DELETE RESTRICT ON UPDATE CASCADE,

    -- Constraints
    CONSTRAINT chk_year CHECK (year >= 1990 AND year <= 2030),
    CONSTRAINT chk_license_plate CHECK (LENGTH(license_plate) >= 3)
);

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_email CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_phone CHECK (LENGTH(phone) >= 10),
    CONSTRAINT chk_name CHECK (LENGTH(name) >= 2)
);

-- Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    id VARCHAR(36) PRIMARY KEY,
    user_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    pickup_date DATE NOT NULL,
    return_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status ENUM('confirmed', 'completed', 'cancelled') DEFAULT 'confirmed',
    payment_status ENUM('pending', 'paid', 'refunded') DEFAULT 'paid',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE RESTRICT ON UPDATE CASCADE,

    -- Constraints
    CONSTRAINT chk_dates CHECK (return_date > pickup_date),
    CONSTRAINT chk_total_amount CHECK (total_amount > 0)
);

-- Invoices Table
CREATE TABLE IF NOT EXISTS invoices (
    id VARCHAR(36) PRIMARY KEY,
    booking_id VARCHAR(36) NOT NULL UNIQUE,
    invoice_number VARCHAR(20) NOT NULL UNIQUE,
    amount DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    issued_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE RESTRICT ON UPDATE CASCADE,

    -- Constraints
    CONSTRAINT chk_invoice_amount CHECK (amount > 0),
    CONSTRAINT chk_invoice_tax CHECK (tax_amount >= 0),
    CONSTRAINT chk_invoice_total CHECK (total_amount >= amount)
);

-- Create Indexes for Performance
-- Note: If indexes already exist, you can safely ignore duplicate key errors
-- Users table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Vehicles table indexes
CREATE INDEX idx_vehicles_type_id ON vehicles(type_id);
CREATE INDEX idx_vehicles_status ON vehicles(status);
CREATE INDEX idx_vehicles_license_plate ON vehicles(license_plate);

-- Bookings table indexes
CREATE INDEX idx_bookings_user_id ON bookings(user_id);
CREATE INDEX idx_bookings_vehicle_id ON bookings(vehicle_id);
CREATE INDEX idx_bookings_pickup_date ON bookings(pickup_date);
CREATE INDEX idx_bookings_return_date ON bookings(return_date);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_dates_range ON bookings(pickup_date, return_date);
CREATE INDEX idx_bookings_created_at ON bookings(created_at);

-- Composite index for availability checks
CREATE INDEX idx_bookings_availability ON bookings(vehicle_id, status, pickup_date, return_date);

-- Invoices table indexes
CREATE INDEX idx_invoices_booking_id ON invoices(booking_id);
CREATE INDEX idx_invoices_issued_date ON invoices(issued_date);
CREATE INDEX idx_invoices_invoice_number ON invoices(invoice_number);

-- Insert initial vehicle types
INSERT IGNORE INTO vehicle_types (name, capacity, daily_rate) VALUES
('small_car', 4, 50.00),
('suv', 7, 80.00),
('van', 8, 100.00);

-- Insert sample vehicles
INSERT IGNORE INTO vehicles (type_id, model, year, license_plate, color) VALUES
-- Small cars
(1, 'Toyota Corolla', 2022, 'ABC123', 'White'),
(1, 'Honda Civic', 2021, 'DEF456', 'Blue'),
(1, 'Nissan Sentra', 2023, 'GHI789', 'Silver'),
(1, 'Hyundai Elantra', 2022, 'JKL012', 'Black'),

-- SUVs
(2, 'Toyota RAV4', 2023, 'MNO345', 'Red'),
(2, 'Honda CR-V', 2022, 'PQR678', 'White'),
(2, 'Nissan Rogue', 2021, 'STU901', 'Gray'),
(2, 'Mazda CX-5', 2023, 'VWX234', 'Blue'),

-- Vans
(3, 'Ford Transit', 2022, 'YZA567', 'White'),
(3, 'Chevrolet Express', 2021, 'BCD890', 'Silver'),
(3, 'Mercedes Sprinter', 2023, 'EFG123', 'Black'),
(3, 'Nissan NV200', 2022, 'HIJ456', 'White');

-- Create a view for vehicle availability
CREATE OR REPLACE VIEW vehicle_availability AS
SELECT
    v.id,
    v.model,
    v.year,
    v.license_plate,
    v.color,
    v.status,
    vt.name as vehicle_type,
    vt.capacity,
    vt.daily_rate,
    CASE
        WHEN v.status = 'available' AND v.id NOT IN (
            SELECT vehicle_id FROM bookings
            WHERE status = 'confirmed'
            AND pickup_date <= CURDATE()
            AND return_date >= CURDATE()
        ) THEN 'available'
        ELSE 'unavailable'
    END as current_availability
FROM vehicles v
JOIN vehicle_types vt ON v.type_id = vt.id;

-- Create a stored procedure for checking vehicle availability
DROP PROCEDURE IF EXISTS CheckVehicleAvailability;
DELIMITER //
CREATE PROCEDURE CheckVehicleAvailability(
    IN p_vehicle_id INT,
    IN p_pickup_date DATE,
    IN p_return_date DATE,
    OUT p_available BOOLEAN
)
BEGIN
    DECLARE conflict_count INT DEFAULT 0;

    SELECT COUNT(*) INTO conflict_count
    FROM bookings
    WHERE vehicle_id = p_vehicle_id
    AND status = 'confirmed'
    AND (
        (pickup_date <= p_pickup_date AND return_date >= p_pickup_date) OR
        (pickup_date <= p_return_date AND return_date >= p_return_date) OR
        (pickup_date >= p_pickup_date AND pickup_date <= p_return_date)
    );

    SET p_available = (conflict_count = 0);
END //
DELIMITER ;

-- Create a function to calculate rental cost
DROP FUNCTION IF EXISTS CalculateRentalCost;
DELIMITER //
CREATE FUNCTION CalculateRentalCost(
    p_vehicle_id INT,
    p_pickup_date DATE,
    p_return_date DATE
) RETURNS DECIMAL(10,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE daily_rate DECIMAL(10,2);
    DECLARE rental_days INT;

    SELECT vt.daily_rate INTO daily_rate
    FROM vehicles v
    JOIN vehicle_types vt ON v.type_id = vt.id
    WHERE v.id = p_vehicle_id;

    SET rental_days = DATEDIFF(p_return_date, p_pickup_date);

    RETURN daily_rate * rental_days;
END //
DELIMITER ;

-- Create triggers for business logic
DROP TRIGGER IF EXISTS before_booking_insert;
DELIMITER //
CREATE TRIGGER before_booking_insert
BEFORE INSERT ON bookings
FOR EACH ROW
BEGIN
    -- Check rental period constraint (max 7 days)
    IF DATEDIFF(NEW.return_date, NEW.pickup_date) > 7 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Rental period cannot exceed 7 days';
    END IF;

    -- Check advance booking constraint (max 7 days ahead)
    IF DATEDIFF(NEW.pickup_date, CURDATE()) > 7 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot book more than 7 days in advance';
    END IF;

    -- Check if dates are in the past
    IF NEW.pickup_date < CURDATE() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot book dates in the past';
    END IF;

    -- Check vehicle availability
    IF EXISTS (
        SELECT 1 FROM bookings
        WHERE vehicle_id = NEW.vehicle_id
        AND status = 'confirmed'
        AND (
            (pickup_date <= NEW.pickup_date AND return_date >= NEW.pickup_date) OR
            (pickup_date <= NEW.return_date AND return_date >= NEW.return_date) OR
            (pickup_date >= NEW.pickup_date AND pickup_date <= NEW.return_date)
        )
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Vehicle is not available for the selected dates';
    END IF;
END //
DELIMITER ;

-- Trigger to update vehicle status when booking is created
DROP TRIGGER IF EXISTS after_booking_insert;
DELIMITER //
CREATE TRIGGER after_booking_insert
AFTER INSERT ON bookings
FOR EACH ROW
BEGIN
    IF NEW.pickup_date = CURDATE() AND NEW.status = 'confirmed' THEN
        UPDATE vehicles SET status = 'rented' WHERE id = NEW.vehicle_id;
    END IF;
END //
DELIMITER ;

-- Trigger to update vehicle status when booking is completed
DROP TRIGGER IF EXISTS after_booking_update;
DELIMITER //
CREATE TRIGGER after_booking_update
AFTER UPDATE ON bookings
FOR EACH ROW
BEGIN
    IF NEW.status = 'completed' AND OLD.status <> 'completed' THEN
        UPDATE vehicles SET status = 'available' WHERE id = NEW.vehicle_id;
    ELSEIF NEW.status = 'cancelled' AND OLD.status <> 'cancelled' THEN
        UPDATE vehicles SET status = 'available' WHERE id = NEW.vehicle_id;
    END IF;
END //
DELIMITER ;