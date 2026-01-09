-- =============================================================================
-- Zava Capacity Planner - Database Schema and Sample Data
-- =============================================================================
-- This script creates the database schema and populates it with realistic
-- sample data for the capacity planning demo.
--
-- Run this script against the PostgreSQL database:
-- psql $POSTGRES_CONNECTION_STRING < seed_database.sql
-- =============================================================================

-- Note: Using gen_random_uuid() which is built into PostgreSQL 13+
-- No extension required for Azure PostgreSQL

-- =============================================================================
-- DROP EXISTING TABLES (for clean re-runs)
-- =============================================================================
DROP TABLE IF EXISTS historical_volumes CASCADE;
DROP TABLE IF EXISTS crew_members CASCADE;
DROP TABLE IF EXISTS routes CASCADE;
DROP TABLE IF EXISTS aircraft CASCADE;
DROP TABLE IF EXISTS shipments CASCADE;

-- =============================================================================
-- SHIPMENTS TABLE
-- =============================================================================
CREATE TABLE shipments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracking_number VARCHAR(50) UNIQUE NOT NULL,
    origin_hub VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    weight_kg DECIMAL(10,2) NOT NULL,
    dimensions_cm JSONB NOT NULL,
    ship_date DATE NOT NULL,
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('Express', 'Priority', 'Standard')),
    status VARCHAR(30) NOT NULL DEFAULT 'Pending',
    customer_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_shipments_date ON shipments(ship_date);
CREATE INDEX idx_shipments_hub ON shipments(origin_hub);
CREATE INDEX idx_shipments_destination ON shipments(destination);

-- =============================================================================
-- AIRCRAFT TABLE
-- =============================================================================
CREATE TABLE aircraft (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tail_number VARCHAR(20) UNIQUE NOT NULL,
    model VARCHAR(50) NOT NULL,
    max_cargo_kg DECIMAL(10,2) NOT NULL,
    max_volume_m3 DECIMAL(10,2) NOT NULL,
    fuel_efficiency_km_per_l DECIMAL(8,2) NOT NULL,
    crew_required INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Available',
    base_hub VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- ROUTES TABLE
-- =============================================================================
CREATE TABLE routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    distance_km INTEGER NOT NULL,
    typical_flight_hours DECIMAL(4,2) NOT NULL,
    is_international BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(origin, destination)
);

-- =============================================================================
-- CREW MEMBERS TABLE
-- =============================================================================
CREATE TABLE crew_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Captain', 'First Officer', 'Flight Engineer')),
    certifications JSONB NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    base_hub VARCHAR(100) NOT NULL,
    monthly_hours_flown DECIMAL(5,1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- HISTORICAL VOLUMES TABLE
-- =============================================================================
CREATE TABLE historical_volumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hub VARCHAR(100) NOT NULL,
    month DATE NOT NULL,
    shipment_count INTEGER NOT NULL,
    total_weight_kg DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(hub, month)
);

-- =============================================================================
-- INSERT AIRCRAFT DATA
-- =============================================================================
INSERT INTO aircraft (tail_number, model, max_cargo_kg, max_volume_m3, fuel_efficiency_km_per_l, crew_required, status, base_hub) VALUES
('N747ZV', 'Boeing 747-400F', 120000.00, 858.00, 12.50, 3, 'Available', 'Seattle'),
('N777ZV', 'Boeing 777F', 102000.00, 653.00, 14.20, 2, 'Available', 'Seattle'),
('N767ZV', 'Boeing 767-300F', 54000.00, 438.00, 16.80, 2, 'Available', 'Seattle'),
('N768ZV', 'Boeing 767-300F', 54000.00, 438.00, 16.80, 2, 'In Maintenance', 'Seattle'),
('N330ZV', 'Airbus A330-200F', 70000.00, 475.00, 15.10, 2, 'Available', 'Seattle'),
('N748ZV', 'Boeing 747-400F', 120000.00, 858.00, 12.50, 3, 'Available', 'Chicago'),
('N779ZV', 'Boeing 777F', 102000.00, 653.00, 14.20, 2, 'Available', 'Los Angeles'),
('N769ZV', 'Boeing 767-300F', 54000.00, 438.00, 16.80, 2, 'Available', 'Miami'),
('N331ZV', 'Airbus A330-200F', 70000.00, 475.00, 15.10, 2, 'Available', 'New York'),
('N332ZV', 'Airbus A330-200F', 70000.00, 475.00, 15.10, 2, 'Available', 'Dallas');

-- =============================================================================
-- INSERT ROUTES DATA
-- =============================================================================
INSERT INTO routes (origin, destination, distance_km, typical_flight_hours, is_international) VALUES
-- Domestic routes from Seattle
('Seattle', 'Los Angeles (LAX)', 1540, 2.50, FALSE),
('Seattle', 'New York (JFK)', 3900, 5.00, FALSE),
('Seattle', 'Chicago (ORD)', 2800, 3.80, FALSE),
('Seattle', 'Dallas (DFW)', 2700, 3.50, FALSE),
('Seattle', 'Miami (MIA)', 4400, 5.50, FALSE),
('Seattle', 'Atlanta (ATL)', 3500, 4.50, FALSE),
('Seattle', 'Denver (DEN)', 1650, 2.30, FALSE),
('Seattle', 'Phoenix (PHX)', 1850, 2.50, FALSE),
-- International routes from Seattle
('Seattle', 'Tokyo (NRT)', 7700, 10.50, TRUE),
('Seattle', 'London (LHR)', 7800, 9.50, TRUE),
('Seattle', 'Frankfurt (FRA)', 8200, 10.00, TRUE),
('Seattle', 'Hong Kong (HKG)', 10100, 13.50, TRUE),
('Seattle', 'Sydney (SYD)', 12500, 16.00, TRUE),
('Seattle', 'Singapore (SIN)', 13000, 17.00, TRUE),
('Seattle', 'Paris (CDG)', 8100, 10.00, TRUE),
('Seattle', 'Amsterdam (AMS)', 7900, 9.50, TRUE);

-- =============================================================================
-- INSERT CREW DATA
-- =============================================================================
INSERT INTO crew_members (employee_id, name, role, certifications, available, base_hub, monthly_hours_flown) VALUES
-- Captains
('ZV-CPT-001', 'Sarah Chen', 'Captain', '["747", "777"]', TRUE, 'Seattle', 28.0),
('ZV-CPT-002', 'Michael Torres', 'Captain', '["747", "777", "767"]', TRUE, 'Seattle', 22.5),
('ZV-CPT-003', 'Jennifer Park', 'Captain', '["777", "767", "A330"]', TRUE, 'Seattle', 18.0),
('ZV-CPT-004', 'David Wilson', 'Captain', '["747", "777"]', TRUE, 'Seattle', 15.0),
('ZV-CPT-005', 'Emily Johnson', 'Captain', '["747", "777", "767", "A330"]', TRUE, 'Seattle', 24.0),
('ZV-CPT-006', 'Robert Lee', 'Captain', '["777", "767"]', FALSE, 'Seattle', 30.0),
-- First Officers
('ZV-FO-001', 'James Liu', 'First Officer', '["777", "767"]', TRUE, 'Seattle', 26.0),
('ZV-FO-002', 'Amanda Foster', 'First Officer', '["747", "777"]', TRUE, 'Seattle', 20.0),
('ZV-FO-003', 'Robert Kim', 'First Officer', '["767", "A330"]', TRUE, 'Seattle', 18.5),
('ZV-FO-004', 'Lisa Martinez', 'First Officer', '["777", "767", "A330"]', TRUE, 'Seattle', 22.0),
('ZV-FO-005', 'Chris Anderson', 'First Officer', '["747", "777", "767", "A330"]', TRUE, 'Seattle', 19.0),
('ZV-FO-006', 'Nicole Brown', 'First Officer', '["747", "777"]', TRUE, 'Seattle', 16.5),
('ZV-FO-007', 'Kevin Davis', 'First Officer', '["767", "A330"]', FALSE, 'Seattle', 28.0),
-- Flight Engineers (for 747)
('ZV-FE-001', 'Thomas Wright', 'Flight Engineer', '["747"]', TRUE, 'Seattle', 12.0),
('ZV-FE-002', 'Maria Garcia', 'Flight Engineer', '["747"]', TRUE, 'Seattle', 14.0);

-- =============================================================================
-- INSERT HISTORICAL VOLUMES DATA (past 12 months)
-- =============================================================================
INSERT INTO historical_volumes (hub, month, shipment_count, total_weight_kg) VALUES
('Seattle', '2025-01-01', 425, 102500.00),
('Seattle', '2025-02-01', 398, 95200.00),
('Seattle', '2025-03-01', 445, 112300.00),
('Seattle', '2025-04-01', 462, 118400.00),
('Seattle', '2025-05-01', 478, 122100.00),
('Seattle', '2025-06-01', 495, 128900.00),
('Seattle', '2025-07-01', 512, 135200.00),
('Seattle', '2025-08-01', 498, 130400.00),
('Seattle', '2025-09-01', 485, 125600.00),
('Seattle', '2025-10-01', 520, 138500.00),
('Seattle', '2025-11-01', 589, 165200.00),
('Seattle', '2025-12-01', 625, 178400.00);

-- =============================================================================
-- INSERT SAMPLE SHIPMENTS (January 2026 - ~500 shipments)
-- =============================================================================

-- Function to generate shipments
DO $$
DECLARE
    i INTEGER;
    ship_date DATE;
    dest VARCHAR(100);
    dest_options VARCHAR(100)[] := ARRAY[
        'Los Angeles (LAX)', 'New York (JFK)', 'Chicago (ORD)', 'Dallas (DFW)',
        'Miami (MIA)', 'Atlanta (ATL)', 'Denver (DEN)', 'Phoenix (PHX)',
        'Tokyo (NRT)', 'London (LHR)', 'Frankfurt (FRA)', 'Hong Kong (HKG)'
    ];
    priority_options VARCHAR(20)[] := ARRAY['Express', 'Priority', 'Standard'];
    weight DECIMAL(10,2);
    priority VARCHAR(20);
    volume DECIMAL(10,2);
BEGIN
    FOR i IN 1..487 LOOP
        -- Random date in January 2026
        ship_date := '2026-01-01'::DATE + (random() * 30)::INTEGER;

        -- Random destination (weighted towards domestic)
        IF random() < 0.75 THEN
            dest := dest_options[1 + floor(random() * 8)::INTEGER];
        ELSE
            dest := dest_options[9 + floor(random() * 4)::INTEGER];
        END IF;

        -- Random priority (weighted towards Standard)
        IF random() < 0.10 THEN
            priority := 'Express';
        ELSIF random() < 0.40 THEN
            priority := 'Priority';
        ELSE
            priority := 'Standard';
        END IF;

        -- Random weight based on distribution
        IF random() < 0.40 THEN
            weight := 10 + random() * 40;  -- Light
        ELSIF random() < 0.78 THEN
            weight := 50 + random() * 150;  -- Medium
        ELSIF random() < 0.94 THEN
            weight := 200 + random() * 300;  -- Heavy
        ELSE
            weight := 500 + random() * 1500;  -- Extra Heavy
        END IF;

        volume := weight * (0.8 + random() * 0.4);  -- Volume roughly proportional to weight

        INSERT INTO shipments (
            tracking_number,
            origin_hub,
            destination,
            weight_kg,
            dimensions_cm,
            ship_date,
            priority,
            status,
            customer_id
        ) VALUES (
            'ZV' || LPAD(i::TEXT, 8, '0'),
            'Seattle',
            dest,
            ROUND(weight::NUMERIC, 2),
            jsonb_build_object(
                'length', ROUND((30 + random() * 170)::NUMERIC, 0),
                'width', ROUND((30 + random() * 120)::NUMERIC, 0),
                'height', ROUND((20 + random() * 100)::NUMERIC, 0),
                'volume', ROUND(volume::NUMERIC, 2)
            ),
            ship_date,
            priority,
            CASE
                WHEN ship_date < CURRENT_DATE THEN 'Delivered'
                WHEN ship_date = CURRENT_DATE THEN 'In Transit'
                ELSE 'Pending'
            END,
            'CUST-' || LPAD((1 + floor(random() * 100)::INTEGER)::TEXT, 5, '0')
        );
    END LOOP;
END $$;

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Show summary statistics
SELECT 'Shipments' as table_name, COUNT(*) as row_count FROM shipments
UNION ALL
SELECT 'Aircraft', COUNT(*) FROM aircraft
UNION ALL
SELECT 'Routes', COUNT(*) FROM routes
UNION ALL
SELECT 'Crew Members', COUNT(*) FROM crew_members
UNION ALL
SELECT 'Historical Volumes', COUNT(*) FROM historical_volumes;

-- Show shipment summary
SELECT
    COUNT(*) as total_shipments,
    ROUND(SUM(weight_kg)::NUMERIC, 2) as total_weight_kg,
    ROUND(AVG(weight_kg)::NUMERIC, 2) as avg_weight_kg
FROM shipments
WHERE origin_hub = 'Seattle'
AND ship_date BETWEEN '2026-01-01' AND '2026-01-31';

-- Show destination breakdown
SELECT
    destination,
    COUNT(*) as shipment_count,
    ROUND(SUM(weight_kg)::NUMERIC, 2) as total_weight
FROM shipments
WHERE origin_hub = 'Seattle'
AND ship_date BETWEEN '2026-01-01' AND '2026-01-31'
GROUP BY destination
ORDER BY shipment_count DESC
LIMIT 10;

COMMIT;
