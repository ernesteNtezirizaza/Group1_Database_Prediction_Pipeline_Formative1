-- Hotel Booking Database Setup Script
-- This script creates the database, tables, stored procedures, triggers, and indexes

-- Drop database if exists and create new one
-- DROP DATABASE IF EXISTS defaultdb;
-- CREATE DATABASE defaultdb;
USE defaultdb;

-- =====================================================
-- TABLE CREATION
-- =====================================================

-- Table 1: hotels
CREATE TABLE hotels (
    hotel_id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_hotel_name (hotel_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 2: guests
CREATE TABLE guests (
    guest_id INT AUTO_INCREMENT PRIMARY KEY,
    country VARCHAR(3) NOT NULL,
    is_repeated_guest BOOLEAN DEFAULT FALSE,
    customer_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_country (country),
    INDEX idx_customer_type (customer_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 3: bookings
CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id INT NOT NULL,
    guest_id INT NOT NULL,
    lead_time INT NOT NULL,
    arrival_date_year INT NOT NULL,
    arrival_date_month VARCHAR(20) NOT NULL,
    arrival_date_week_number INT NOT NULL,
    arrival_date_day_of_month INT NOT NULL,
    stays_in_weekend_nights INT DEFAULT 0,
    stays_in_week_nights INT DEFAULT 0,
    adults INT NOT NULL,
    children INT DEFAULT 0,
    babies INT DEFAULT 0,
    meal VARCHAR(20) NOT NULL,
    market_segment VARCHAR(50) NOT NULL,
    distribution_channel VARCHAR(50) NOT NULL,
    previous_cancellations INT DEFAULT 0,
    previous_bookings_not_canceled INT DEFAULT 0,
    reserved_room_type VARCHAR(1) NOT NULL,
    assigned_room_type VARCHAR(1) NOT NULL,
    booking_changes INT DEFAULT 0,
    deposit_type VARCHAR(20) NOT NULL,
    agent INT NULL,
    company INT NULL,
    days_in_waiting_list INT DEFAULT 0,
    adr DECIMAL(10, 2) NOT NULL,
    required_car_parking_spaces INT DEFAULT 0,
    total_of_special_requests INT DEFAULT 0,
    is_canceled BOOLEAN DEFAULT FALSE,
    reservation_status VARCHAR(20) NOT NULL,
    reservation_status_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id) ON DELETE CASCADE,
    FOREIGN KEY (guest_id) REFERENCES guests(guest_id) ON DELETE CASCADE,
    INDEX idx_hotel_id (hotel_id),
    INDEX idx_guest_id (guest_id),
    INDEX idx_is_canceled (is_canceled),
    INDEX idx_reservation_status (reservation_status),
    INDEX idx_arrival_date_year (arrival_date_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 4: booking_logs
CREATE TABLE booking_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    action VARCHAR(20) NOT NULL,
    old_status VARCHAR(20) NULL,
    new_status VARCHAR(20) NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE,
    INDEX idx_booking_id (booking_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- STORED PROCEDURES
-- =====================================================

DELIMITER $$

-- Stored Procedure 1: Validate Booking
CREATE PROCEDURE sp_validate_booking(
    IN p_lead_time INT,
    IN p_adults INT,
    IN p_reservation_status VARCHAR(20),
    OUT p_is_valid BOOLEAN,
    OUT p_error_message VARCHAR(255)
)
BEGIN
    DECLARE valid_statuses VARCHAR(255) DEFAULT 'Check-Out,Canceled,No-Show';
    DECLARE v_count INT;
    
    SET p_is_valid = TRUE;
    SET p_error_message = '';
    
    -- Validate lead_time >= 0
    IF p_lead_time < 0 THEN
        SET p_is_valid = FALSE;
        SET p_error_message = 'Lead time must be non-negative';
    END IF;
    
    -- Validate adults > 0
    IF p_adults <= 0 THEN
        SET p_is_valid = FALSE;
        SET p_error_message = CONCAT(p_error_message, '; Adults must be greater than 0');
    END IF;
    
    -- Validate reservation_status
    SELECT COUNT(*) INTO v_count
    FROM bookings b
    WHERE FIND_IN_SET(p_reservation_status, valid_statuses) > 0
    LIMIT 1;
    
    IF p_reservation_status NOT IN ('Check-Out', 'Canceled', 'No-Show') THEN
        SET p_is_valid = FALSE;
        SET p_error_message = CONCAT(p_error_message, '; Invalid reservation status');
    END IF;
END$$

-- Stored Procedure 2: Get Booking Statistics
CREATE PROCEDURE sp_get_booking_statistics(
    OUT p_total_bookings INT,
    OUT p_cancellation_rate DECIMAL(5, 2),
    OUT p_avg_adr DECIMAL(10, 2),
    OUT p_most_common_country VARCHAR(3)
)
BEGIN
    -- Total bookings
    SELECT COUNT(*) INTO p_total_bookings FROM bookings;
    
    -- Cancellation rate
    SELECT 
        CASE 
            WHEN p_total_bookings > 0 THEN (COUNT(*) / p_total_bookings) * 100
            ELSE 0 
        END
    INTO p_cancellation_rate
    FROM bookings
    WHERE is_canceled = TRUE;
    
    -- Average ADR
    SELECT AVG(adr) INTO p_avg_adr FROM bookings;
    
    -- Most common country
    SELECT country INTO p_most_common_country
    FROM guests
    GROUP BY country
    ORDER BY COUNT(*) DESC
    LIMIT 1;
END$$

DELIMITER ;

-- =====================================================
-- TRIGGERS
-- =====================================================

DELIMITER $$

-- Trigger 1: Log booking status changes
CREATE TRIGGER trg_booking_after_update
AFTER UPDATE ON bookings
FOR EACH ROW
BEGIN
    IF OLD.reservation_status != NEW.reservation_status THEN
        INSERT INTO booking_logs (booking_id, action, old_status, new_status)
        VALUES (NEW.booking_id, 'UPDATE', OLD.reservation_status, NEW.reservation_status);
    END IF;
END$$

-- Trigger 2: Log new bookings
CREATE TRIGGER trg_booking_after_insert
AFTER INSERT ON bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_logs (booking_id, action, old_status, new_status)
    VALUES (NEW.booking_id, 'INSERT', NULL, NEW.reservation_status);
END$$

DELIMITER ;

-- =====================================================
-- SAMPLE DATA INSERTION
-- =====================================================

-- Insert sample hotels
-- INSERT INTO hotels (hotel_name) VALUES ('Resort Hotel');
-- INSERT INTO hotels (hotel_name) VALUES ('City Hotel');

-- -- Insert sample guests
-- INSERT INTO guests (country, is_repeated_guest, customer_type) VALUES ('PRT', FALSE, 'Transient');
-- INSERT INTO guests (country, is_repeated_guest, customer_type) VALUES ('GBR', FALSE, 'Transient');
-- INSERT INTO guests (country, is_repeated_guest, customer_type) VALUES ('ESP', TRUE, 'Contract');

-- -- Insert sample booking
-- INSERT INTO bookings (
--     hotel_id, guest_id, lead_time, arrival_date_year, arrival_date_month,
--     arrival_date_week_number, arrival_date_day_of_month, stays_in_weekend_nights,
--     stays_in_week_nights, adults, children, babies, meal, market_segment,
--     distribution_channel, previous_cancellations, previous_bookings_not_canceled,
--     reserved_room_type, assigned_room_type, booking_changes, deposit_type,
--     agent, company, days_in_waiting_list, adr, required_car_parking_spaces,
--     total_of_special_requests, is_canceled, reservation_status, reservation_status_date
-- ) VALUES (
--     1, 1, 342, 2015, 'July', 27, 1, 0, 0, 2, 0, 0, 'BB', 'Direct',
--     'Direct', 0, 0, 'C', 'C', 3, 'No Deposit', NULL, NULL, 0,
--     0.00, 0, 0, FALSE, 'Check-Out', '2015-07-01'
-- );

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check table creation
SHOW TABLES;

-- Check foreign key constraints
SELECT * FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'defaultdb'
AND TABLE_NAME IN ('bookings', 'booking_logs')
AND CONSTRAINT_NAME LIKE 'fk%';

-- Check triggers
SHOW TRIGGERS;

-- Check stored procedures
SHOW PROCEDURE STATUS WHERE db = 'defaultdb';

-- Test stored procedure
CALL sp_validate_booking(50, 2, 'Check-Out', @is_valid, @error_message);
SELECT @is_valid, @error_message;

-- Test statistics
CALL sp_get_booking_statistics(@total, @cancellation_rate, @avg_adr, @country);
SELECT @total, @cancellation_rate, @avg_adr, @country;

-- View all data
SELECT 'Hotels' AS table_name, COUNT(*) AS record_count FROM hotels
UNION ALL
SELECT 'Guests', COUNT(*) FROM guests
UNION ALL
SELECT 'Bookings', COUNT(*) FROM bookings
UNION ALL
SELECT 'Booking Logs', COUNT(*) FROM booking_logs;
