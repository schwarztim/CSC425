CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    time_slot TIMESTAMP UNIQUE NOT NULL,  -- Storing time slots as timestamp
    name VARCHAR(255) NOT NULL,           -- Storing the name of the customer
    phone_number VARCHAR(20) NOT NULL     -- Storing the phone number of the customer
);