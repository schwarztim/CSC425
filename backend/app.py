import logging
import os

from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import pool

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


@app.route('/book', methods=['POST'])
def book_time():
    time_slot = request.json.get("time")
    if not time_slot:
        return jsonify({"error": "No time slot provided"}), 400

    try:
        conn = connection_pool.getconn()
        cur = conn.cursor()
        cur.execute("INSERT INTO bookings (time_slot) VALUES (%s)", (time_slot,))
        conn.commit()
        cur.close()
        connection_pool.putconn(conn)
        return jsonify({"message": "Time slot booked successfully"})
    except psycopg2.IntegrityError:
        logging.error("Time slot already booked")
        return jsonify({"error": "Time slot already booked"}), 400
    except Exception as e:
        logging.error(f"Error booking time slot: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
