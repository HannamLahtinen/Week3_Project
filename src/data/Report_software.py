import os
import psycopg2
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from flask import Flask, request, jsonify
from flask_server import get_db_connection
app = Flask(__name__)

get_db_connection()

def fetch_time_tracking_data(conn, start_date, end_date):
    cursor = conn.cursor()
    
    # start_time as work_date
    query = """
    SELECT consultant_name, customer_name,
       EXTRACT(EPOCH FROM (end_time - start_time - lunch_break)) / 3600 AS total_hours, start_time::DATE AS work_date 
    FROM time_tracking
    WHERE start_time BETWEEN %s AND %s; 
    """
    
    cursor.execute(query, (start_date, end_date))
    records = cursor.fetchall()
    
    cursor.close()
    return records


def generate_report(records, start_date, end_date):
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    filename = f"Time_Tracking_Report_{start_date_str}_to_{end_date_str}.txt"
    
    report_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report_files')
    os.makedirs(report_directory, exist_ok=True)  
    
    file_path = os.path.join(report_directory, filename)
    
    with open(file_path, 'w') as file:
        file.write(f"{'='*100}\n")
        file.write(f"Time Tracking Report\n")
        file.write(f"{'='*100}\n\n")
        file.write(f"Report for the period: {start_date_str} to {end_date_str}\n\n")
        
        # work_date
        file.write(f"{'Consultant Name':<25} {'Customer Name':<25} {'Total Hours Worked':<25} {'Date':>20}\n")
        file.write(f"{'-'*100}\n")  

        for record in records:
            # work_date
            consultant_name, customer_name, total_seconds, work_date = record
            total_minutes = int(total_seconds * 60)  
            hours = total_minutes // 60
            minutes = total_minutes % 60
            
            total_time_str = f"{hours} hours {minutes:02d} minutes"
            
            # work_date
            file.write(f"{consultant_name:<25} {customer_name:<25} {total_time_str:<25} {work_date.strftime('%Y-%m-%d'):>20}\n")
        
        file.write(f"\n{'='*100}\n")
        file.write(f"End of Report\n")
        file.write(f"{'='*100}\n")
    
    return file_path




def upload_to_blob_storage(file_path):
    storage_account_url = "https://week3storageaccount.blob.core.windows.net"  
    container_name = "container" 

    credential = DefaultAzureCredential()

    blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)

    container_client = blob_service_client.get_container_client(container_name)

    blob_name = os.path.basename(file_path)

    try:
        with open(file_path, "rb") as data:
            container_client.upload_blob(name=blob_name, data=data, overwrite=True) 
        print(f"File '{file_path}' uploaded to blob '{blob_name}' successfully.")
    except Exception as e:
        print(f"An error occurred while uploading the file: {e}")


def main():
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")

    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please enter the dates in the format YYYY-MM-DD.")
        return

    conn = get_db_connection()

    try:
        records = fetch_time_tracking_data(conn, start_date, end_date)

        report_path = generate_report(records, start_date, end_date)

        upload_to_blob_storage(report_path)

    finally:
        conn.close()

@app.route('/report', methods=['POST'])
def generate_report_from_trigger():
    data = request.get_json()

    start_date = data.get("start_date")
    end_date = data.get("end_date")
   

    if not start_date or not end_date:
        return jsonify({"error": "Please write start date and end date for the report"}), 400

    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400
    
    conn = get_db_connection()
    try:
        records = fetch_time_tracking_data(conn, start_date, end_date)
        file_path = generate_report(records, start_date, end_date)
        upload_to_blob_storage(file_path)
        return jsonify({"Success": "Report generated and uploaded successfully to Blob Storage."}), 200

    finally:
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)

