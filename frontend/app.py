import logging
import os
from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

backend_url = os.getenv('BACKEND_URL', 'http://backend:5000')
logging.info(f"Backend URL is set to {backend_url}")

@app.route("/")
def index():
    try:
        response = requests.get(f"{backend_url}/times")
        if response.status_code == 200:
            times = response.json()
        else:
            times = []
        logging.info(f"Fetched times: {times}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching times: {e}")
        times = []

    return render_template("index.html", times=times)

@app.route("/book", methods=["POST"])
def book_time():
    time_slot = request.json.get("time")
    try:
        response = requests.post(f"{backend_url}/book", json={"time": time_slot})
        if response.status_code == 200:
            return jsonify({"message": "Time booked successfully!"})
        else:
            return jsonify({"error": response.json().get("error", "Booking failed")}), response.status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"Error booking time: {e}")
        return jsonify({"error": "Error booking time"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
