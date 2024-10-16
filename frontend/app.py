import logging
import os
from flask import Flask, jsonify, request, render_template
import requests
from flask_cors import CORS
from datetime import datetime, timedelta
from flask_limiter import Limiter

# Initialize Flask application
app = Flask(__name__, static_folder='static', template_folder='templates')

# Apply CORS to allow cross-origin requests
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Constants and Configurations
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:5000')
RATE_LIMIT = "5 per minute"

if not BACKEND_URL:
    logging.error("BACKEND_URL is not set.")
    raise EnvironmentError("BACKEND_URL is not set in the environment variables.")

# Initialize rate limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)

# Utility function to handle backend requests
def make_backend_request(method, endpoint, **kwargs):
    url = f"{BACKEND_URL}/{endpoint}"
    logging.debug(f"Making {method.upper()} request to {url} with args: {kwargs}")
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error making {method.upper()} request to {url}: {e}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "UP"}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/times', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def get_times():
    date = request.args.get('date')
    if not date:
        logging.error("Date parameter is required.")
        return jsonify({"error": "Date parameter is required"}), 400

    try:
        response = make_backend_request('get', 'times', params={"date": date})
        times = response.json()
        logging.debug(f"Received times data: {times}")
        return jsonify(times)
    except Exception as e:
        logging.error(f"Error fetching times: {e}")
        return jsonify({"error": str(e)}), 500

def get_booked_slots(date_str):
    try:
        response = make_backend_request('get', 'available-slots', params={"date": date_str})
        return [slot["time"] for slot in response.json() if slot.get("booked")]
    except Exception as e:
        logging.error(f"Error fetching booked slots: {e}")
        raise

@app.route('/available-slots', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def available_slots():
    date_str = request.args.get('date')
    if not date_str:
        logging.error("No date received in the request.")
        return jsonify({"error": "Date parameter is required"}), 400
    
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        logging.error("Invalid date format. Expected YYYY-MM-DD.")
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    try:
        # Generate all possible time slots in half-hour increments
        all_slots = []
        start_time = datetime.strptime(f"{date_str} 10:00", "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(f"{date_str} 17:30", "%Y-%m-%d %H:%M")
        current_time = start_time

        while current_time <= end_time:
            all_slots.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=30)

        booked_slots = get_booked_slots(date_str)
        available_slots = [
            {'time': slot, 'booked': slot in booked_slots} for slot in all_slots
        ]

        logging.debug(f"Available slots for {date_str}: {available_slots}")
        return jsonify(available_slots)
    except Exception as e:
        logging.error(f"Error processing available slots: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/book', methods=['POST'])
@limiter.limit(RATE_LIMIT)
def book_time():
    try:
        data = request.get_json()
        logging.debug(f"Received booking data: {data}")
        time_slot = data.get("time")
        name = data.get("name")
        phone_number = data.get("phone_number")
    except Exception as e:
        logging.error(f"Error parsing request JSON: {e}")
        return jsonify({"error": "Invalid JSON body."}), 400

    if not time_slot or not name or not phone_number:
        logging.error("Time slot, name, and phone number are required.")
        return jsonify({"error": "Time slot, name, and phone number are required."}), 400

    try:
        # Validate the time format
        datetime.strptime(time_slot, '%H:%M')
    except ValueError:
        logging.error("Invalid time format for time slot: %s", time_slot)
        return jsonify({"error": "Invalid time format. Expected HH:MM."}), 400

    try:
        logging.debug(
            f"Booking time slot: {time_slot} for name: {name} and phone number: {phone_number}"
        )
        payload = {
            "time": time_slot,
            "name": name,
            "phone_number": phone_number
        }
        logging.debug(f"Booking payload: {payload}")
        response = make_backend_request('post', 'book', json=payload)
        booking_response = response.json()
        logging.debug(f"Received booking response: {booking_response}")
        return jsonify(booking_response), response.status_code
    except Exception as e:
        logging.error(f"Error booking time: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
