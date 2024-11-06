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

@app.route('/time_tracking', methods=['POST'])
def log_time():
    # Parse JSON data from the request
    data = request.get_json()
    
    # Check if the data is a list or a single dictionary
    if isinstance(data, dict):
        data = [data]  # Wrap the single dictionary in a list
    
    if not isinstance(data, list):
        return jsonify({"error": "Invalid data format. Expected a list or a single entry"}), 400

    # Check each entry for required fields
    required_fields = ['start_time', 'end_time', 'lunch_break', 'consultant_name', 'customer_name']
    for entry in data:
        if not all(field in entry for field in required_fields):
            return jsonify({"error": "Missing required fields in one or more entries"}), 400

    # Insert data into the PostgreSQL database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Loop through each entry and insert it into the database
        for entry in data:
            start_time = entry['start_time']
            end_time = entry['end_time']
            lunch_break = entry['lunch_break']
            consultant_name = entry['consultant_name']
            customer_name = entry['customer_name']

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

    return jsonify({"message": "Time entry(ies) logged successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True)
