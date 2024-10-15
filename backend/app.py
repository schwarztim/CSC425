import logging
import os
from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import pool
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Ensure DATABASE_URL is set
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    logging.error("DATABASE_URL is not set.")
    raise EnvironmentError("DATABASE_URL is not set in the environment variables.")

# Create a connection pool
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20, DATABASE_URL
    )
    logging.info("Database connection pool created.")
except Exception as e:
    logging.error(f"Error creating connection pool: {e}")
    raise Exception("Error creating connection pool: ", e)

# Helper function to validate time slot
def is_valid_time_slot(time_str):
    try:
        time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        if time_obj.weekday() in [0, 1]:  # Monday (0) and Sunday (1) not allowed
            return False
        if time_obj.hour < 10 or time_obj.hour > 18:  # Outside 10 AM to 6 PM
            return False
        return True
    except ValueError:
        return False

# Fetch all booked times
@app.route('/times', methods=['GET'])
def get_times():
    try:
        conn = connection_pool.getconn()
        cur = conn.cursor()
        cur.execute("SELECT time_slot FROM bookings")
        rows = cur.fetchall()
        cur.close()
        connection_pool.putconn(conn)
        return jsonify([row[0] for row in rows])
    except Exception as e:
        logging.error(f"Error fetching times: {e}")
        return jsonify({"error": str(e)}), 500

# Handle booking a time slot
@app.route('/book', methods=['POST'])
def book_time():
    time_slot = request.json.get("time")
    name = request.json.get("name")
    phone_number = request.json.get("phone_number")
    
    if not time_slot or not name or not phone_number:
        return jsonify({"error": "Time slot, name, and phone number are required."}), 400

    # Validate the time slot format and rules
    if not is_valid_time_slot(time_slot):
        return jsonify({"error": "Invalid time slot. Bookings are allowed only between 10 AM to 6 PM, Tuesday through Saturday."}), 400

    try:
        conn = connection_pool.getconn()
        cur = conn.cursor()
        
        # Check if the time slot is already booked
        cur.execute("SELECT COUNT(*) FROM bookings WHERE time_slot = %s", (time_slot,))
        count = cur.fetchone()[0]
        if count > 0:
            return jsonify({"error": "Time slot already booked"}), 400

        # Book the time slot with name and phone number
        cur.execute("INSERT INTO bookings (time_slot, name, phone_number) VALUES (%s, %s, %s)", 
                    (time_slot, name, phone_number))
        conn.commit()
        cur.close()
        connection_pool.putconn(conn)
        return jsonify({"message": "Time slot booked successfully!"})
    except psycopg2.IntegrityError:
        logging.error("Time slot already booked")
        return jsonify({"error": "Time slot already booked"}), 400
    except Exception as e:
        logging.error(f"Error booking time slot: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
