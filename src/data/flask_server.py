from flask import Flask, request, jsonify
import psycopg2
from config import config

app = Flask(__name__)

# Database connection function
def get_db_connection():
    try:
        # Read connection parameters from database.ini
        params = config()
        conn = psycopg2.connect(**params)
        return conn
    except Exception as e:
        print("Error connecting to the database:", e)
        raise

@app.route('/log_time', methods=['POST'])
def log_time():
    # Parse JSON data from the request
    data = request.get_json()
    required_fields = ['start_time', 'end_time', 'lunch_break', 'consultant_name', 'customer_name']

    # Check if all required fields are provided
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    start_time = data['start_time']
    end_time = data['end_time']
    lunch_break = data['lunch_break']
    consultant_name = data['consultant_name']
    customer_name = data['customer_name']

    # Insert data into the PostgreSQL database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO time_tracking (start_time, end_time, lunch_break, consultant_name, customer_name) VALUES (%s, %s, %s, %s, %s)",
            (start_time, end_time, lunch_break, consultant_name, customer_name)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error logging time entry:", e)
        return jsonify({"error": "Failed to log time entry"}), 500

    return jsonify({"message": "Time entry logged successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True)
