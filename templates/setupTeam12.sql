-- Create team12_customers table
CREATE TABLE team12_customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100)
);

-- Create team12_flowers table
CREATE TABLE team12_flowers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    last_watered DATE,
    water_level INT,
    min_water_required INT,
    image_url TEXT
);

-- Create team12_orders table
CREATE TABLE team12_orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES team12_customers(id),
    flower_id INT REFERENCES team12_flowers(id),
    order_date DATE
);

-- Insert 100,000 fake customers
INSERT INTO team12_customers (name, email)
SELECT
    'Customer_' || i,
    'customer' || i || '@example.com'
FROM generate_series(1, 100000) AS s(i);

-- Insert 5 flowers (optional sample from your SQLite)
INSERT INTO team12_flowers (name, last_watered, water_level, min_water_required, image_url) VALUES
('Rose', '2024-03-22', 15, 5, '/static/images/rose.jpg'),
('Tulip', '2024-02-08', 10, 7, '/static/images/tulip.jpg'),
('Lily', '2024-02-05', 3, 5, '/static/images/dry_lily.jpg'),
('Daisy', '2024-04-20', 8, 5, '/static/images/daisy.jpg'),
('Daisy', '2024-03-21', 12, 5, '/static/images/daisy.jpg');

-- Insert 500,000 fake orders
INSERT INTO team12_orders (customer_id, flower_id, order_date)
SELECT
    FLOOR(random() * 100000 + 1)::int,
    FLOOR(random() * 5 + 1)::int,
    NOW() - (random() * 365 * interval '1 day')
FROM generate_series(1, 500000);

-- Optional: Add indexes for optimization
CREATE INDEX idx_customer_id ON team12_orders(customer_id);
CREATE INDEX idx_flower_id ON team12_orders(flower_id);

-- Optional: Enable pgcrypto for encryption in slow-query
CREATE EXTENSION IF NOT EXISTS pgcrypto;
