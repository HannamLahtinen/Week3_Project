# Flask server for fetching working time entries from Postman.

from flask import Flask, request, jsonify
import psycopg2
from config import config
from datetime import datetime

app = Flask(__name__)




# 1. Database connection function
def get_db_connection():
    try:
        # Read connection parameters from database fetching secrets from key vault.
        params = config()
        conn = psycopg2.connect(**params)
        return conn
    except Exception as e:
        print("Error connecting to the database:", e)
        raise




# 2. Route to fetch working time entries inserted via Postman.
@app.route('/time_tracking', methods=['POST'])
def log_time():
    data = request.get_json()
    
    # 2.1. Check if the data is a list or a single dictionary and if yes wrap them into dictionary.
    if isinstance(data, dict):
        data = [data]  
    if not isinstance(data, list):
        return jsonify({"error": "Invalid data format. Expected a list or a single entry"}), 400

    required_fields = ['start_time', 'end_time', 'lunch_break', 'consultant_name', 'customer_name']
    for entry in data:
        if not all(field in entry for field in required_fields):
            return jsonify({"error": "Missing required fields in one or more entries"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for entry in data:
            cursor.execute(
                "INSERT INTO time_tracking (start_time, end_time, lunch_break, consultant_name, customer_name) VALUES (%s, %s, %s, %s, %s)",
                (entry['start_time'], entry['end_time'], entry['lunch_break'], entry['consultant_name'], entry['customer_name'])
            )
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error logging time entry:", e)
        return jsonify({"error": "Failed to log time entry"}), 500

    return jsonify({"message": "Time entry(ies) logged successfully"}), 201



if __name__ == '__main__':
    app.run(debug=False)
