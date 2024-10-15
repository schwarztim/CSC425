import logging
import os
from flask import Flask, jsonify, request, render_template
import requests  # Use requests to interact with the backend
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Ensure BACKEND_URL is set for communication with the backend
backend_url = os.getenv('BACKEND_URL', 'http://backend:5000')
if not backend_url:
    logging.error("BACKEND_URL is not set.")
    raise EnvironmentError("BACKEND_URL is not set in the environment variables.")

# Route to serve the frontend template
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/times', methods=['GET'])
def get_times():
    try:
        # Forward request to backend
        response = requests.get(f"{backend_url}/times")
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching times from backend: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/book', methods=['POST'])
def book_time():
    time_slot = request.json.get("time")
    name = request.json.get("name")
    phone_number = request.json.get("phone_number")

    if not time_slot or not name or not phone_number:
        return jsonify({"error": "Time slot, name, and phone number are required."}), 400

    try:
        # Forward booking request to the backend
        response = requests.post(f"{backend_url}/book", json={
            "time": time_slot,
            "name": name,
            "phone_number": phone_number
        })
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"Error booking time with backend: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
