import os
import psycopg2
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


def connect_to_postgresql():
    conn = psycopg2.connect(
        host="week3projectpostgresql.postgres.database.azure.com", 
        database="postgres", 
        user="Week3_Project", 
        password="postgres666!"
    )
    return conn


def fetch_time_tracking_data(conn, start_date, end_date):
    cursor = conn.cursor()
    
    query = """
    SELECT consultant_name, customer_name,
       SUM(
           EXTRACT(HOUR FROM (end_time - start_time - lunch_break)) 
           + EXTRACT(MINUTE FROM (end_time - start_time - lunch_break)) / 60.0
       ) AS total_hours
    FROM time_tracking
    WHERE start_time BETWEEN %s AND %s
    GROUP BY consultant_name, customer_name;
    """
    
    cursor.execute(query, (start_date, end_date))
    records = cursor.fetchall()
    
    cursor.close()
    return records


def generate_report(records, start_date, end_date):
    filename = f"Time_Tracking_Report_{start_date}_to_{end_date}.txt"
    
    report_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report_files')
    os.makedirs(report_directory, exist_ok=True)  
    
    file_path = os.path.join(report_directory, filename)
    
    with open(file_path, 'w') as file:
        file.write(f"{'='*50}\n")
        file.write(f"          Time Tracking Report\n")
        file.write(f"{'='*50}\n\n")
        file.write(f"Report for the period: {start_date} to {end_date}\n\n")
        file.write(f"{'Consultant Name':<25} {'Customer Name':<25} {'Total Hours Worked':>20}\n")
        file.write(f"{'-'*50}\n")  
        
        for record in records:
            consultant_name, customer_name, total_hours = record
            file.write(f"{consultant_name:<25} {customer_name:<25} {total_hours:>20.2f} hours\n")
        
        file.write(f"\n{'='*50}\n")
        file.write(f"End of Report\n")
        file.write(f"{'='*50}\n")
    
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





