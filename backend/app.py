import logging
import os
from flask import Flask, jsonify, request
from flask_cors import CORS  # Add this import
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from datetime import datetime, timedelta

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Configure logging with detailed format
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Ensure DATABASE_URL is set
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    logging.error("DATABASE_URL is not set.")
    raise EnvironmentError("DATABASE_URL is not set in the environment variables.")

try:
    # Create a connection pool
    connection_pool = psycopg2.pool.SimpleConnectionPool(1, 20, DATABASE_URL)
    logging.info("Database connection pool created.")
except Exception as e:
    logging.error(f"Error creating connection pool: {e}")
    raise Exception("Error creating connection pool: ", e)

def get_db_connection():
    try:
        conn = connection_pool.getconn()
        return conn
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise

def is_valid_time_slot(time_str):
    try:
        time_obj = datetime.strptime(time_str, "%H:%M").time()
        # Check if the hour is within 10 AM to 6 PM
        if time_obj < datetime.strptime("10:00", "%H:%M").time() or time_obj >= datetime.strptime("18:00", "%H:%M").time():
            logging.debug("The requested time slot is outside of business hours (10 AM to 6 PM).")
            return False
        return True
    except ValueError:
        logging.debug("The requested time slot format is invalid.")
        return False

def get_booked_slots(date):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT time_slot FROM bookings WHERE time_slot::date = %s::date", (date,))
        rows = cursor.fetchall()
        cursor.close()
        connection_pool.putconn(conn)
        return [row["time_slot"].strftime("%H:%M") for row in rows]
    except Exception as e:
        logging.error(f"Error fetching booked slots: {e}")
        if conn:
            connection_pool.putconn(conn, close=True)
        raise

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "UP"}), 200

@app.route('/times', methods=['GET'])
def get_times():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT time_slot FROM bookings")
        rows = cursor.fetchall()
        cursor.close()
        connection_pool.putconn(conn)
        return jsonify([row["time_slot"] for row in rows])
    except Exception as e:
        logging.error(f"Error fetching times: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/available-slots', methods=['GET'])
def available_slots():
    date_str = request.args.get('date')
    if not date_str:
        logging.error("Date parameter is required")
        return jsonify({"error": "Date parameter is required"}), 400

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        logging.error("Invalid date format. Use YYYY-MM-DD.")
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # Generate all possible time slots in half-hour increments
    all_slots = []
    start_time = datetime.strptime(f"{date_str} 10:00", "%Y-%m-%d %H:%M")
    end_time = datetime.strptime(f"{date_str} 17:30", "%Y-%m-%d %H:%M")
    current_time = start_time

    while current_time <= end_time:
        all_slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=30)
    
    logging.debug(f"All possible slots: {all_slots}")

    try:
        booked_slots = get_booked_slots(date_str)
        available_slots = [{'time': slot, 'booked': slot in booked_slots} for slot in all_slots]
        
        logging.debug(f"Booked slots: {booked_slots}")
        logging.debug(f"Final available slots: {available_slots}")

        return jsonify(available_slots)
    except Exception as e:
        logging.error(f"Error fetching available slots: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/book', methods=['POST'])
def book_time():
    try:
        # Log received data
        data = request.get_json()
        logging.debug(f"Received booking data: {data}")

        # Extract fields
        time_slot = data.get("time")
        date_str = data.get("date")
        name = data.get("name")
        phone_number = data.get("phone_number")

        # Log extracted fields
        logging.debug(f"Extracted fields - time: {time_slot}, date: {date_str}, name: {name}, phone_number: {phone_number}")

        # Check if all required fields are present
        if not time_slot or not date_str or not name or not phone_number:
            logging.error("Missing required booking data.")
            return jsonify({"error": "Date, time slot, name, and phone number are required."}), 400

        # Validate the time part (HH:MM)
        logging.debug("Validating time slot")
        if not is_valid_time_slot(time_slot):
            error_msg = "Invalid time slot. Bookings are allowed only between 10 AM to 6 PM, Tuesday through Saturday."
            logging.error(error_msg)
            return jsonify({"error": error_msg}), 400

        # Combine date and time into a full datetime object
        full_time_slot = f"{date_str} {time_slot}"

        try:
            # Convert to datetime for database insertion
            time_slot_dt = datetime.strptime(full_time_slot, "%Y-%m-%d %H:%M")
        except ValueError:
            error_msg = "Invalid time slot format."
            logging.error(error_msg)
            return jsonify({"error": error_msg}), 400

        # Proceed with database insertion
        logging.debug("Attempting to connect to the database")
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        logging.debug("Executing SELECT COUNT query to check existing bookings")
        cursor.execute("SELECT COUNT(*) FROM bookings WHERE time_slot = %s", (time_slot_dt,))
        count = cursor.fetchone()["count"]
        if count > 0:
            error_msg = "Time slot already booked"
            logging.error(error_msg)
            return jsonify({"error": error_msg}), 400

        logging.debug("Executing INSERT query to book the time slot")
        cursor.execute("INSERT INTO bookings (time_slot, name, phone_number) VALUES (%s, %s, %s)",
                       (time_slot_dt, name, phone_number))
        conn.commit()
        cursor.close()
        connection_pool.putconn(conn)
        logging.debug("Time slot booked successfully!")
        return jsonify({"message": "Time slot booked successfully!"}), 201
    except Exception as e:
        logging.error(f"Error booking time slot: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
