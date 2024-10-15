import logging
import os
from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

backend_url = os.getenv('BACKEND_URL', 'http://backend:5000')
logging.info(f"Backend URL is set to {backend_url}")

# Helper function to check if the date is between Tuesday (2) and Saturday (6)
def is_valid_booking_day(date):
    return 2 <= date.weekday() <= 6

# Helper function to get available time slots (10 AM to 6 PM)
def get_available_times():
    times = []
    for hour in range(10, 19):  # Times from 10 AM to 6 PM
        times.append(f"{str(hour).zfill(2)}:00")
    return times

# Fetch booked times from the backend and disable them on the frontend
@app.route("/")
def index():
    today = datetime.now().strftime('%Y-%m-%d')  # Get today's date
    available_times = get_available_times()  # Get available timeslots

    try:
        response = requests.get(f"{backend_url}/times")
        if response.status_code == 200:
            booked_times = response.json()  # Fetch booked times from backend
            logging.info(f"Fetched booked times: {booked_times}")
        else:
            booked_times = []
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching booked times: {e}")
        booked_times = []

    return render_template("index.html", times=available_times, booked_times=booked_times, today=today)

# Handle booking requests
@app.route("/book", methods=["POST"])
def book_time():
    time_slot = request.json.get("time")
    name = request.json.get("name")  # Capture the name from the request
    phone_number = request.json.get("phone_number")  # Capture the phone number from the request

    if not time_slot or not name or not phone_number:
        return jsonify({"error": "Time slot, name, and phone number are required."}), 400

    # Validate the date part of the time_slot
    try:
        booking_time = datetime.strptime(time_slot, "%Y-%m-%d %H:%M")
        if not is_valid_booking_day(booking_time):
            return jsonify({"error": "Booking is only allowed Tuesday through Saturday."}), 400
    except ValueError:
        return jsonify({"error": "Invalid date or time format."}), 400

    try:
        # Send time, name, and phone number to the backend
        response = requests.post(f"{backend_url}/book", json={
            "time": time_slot,
            "name": name,
            "phone_number": phone_number
        })
        if response.status_code == 200:
            return jsonify({"message": "Time booked successfully!"})
        else:
            return jsonify({"error": response.json().get("error", "Booking failed")}), response.status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"Error booking time: {e}")
        return jsonify({"error": "Error booking time"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)