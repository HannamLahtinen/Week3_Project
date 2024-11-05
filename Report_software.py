import psycopg2
from datetime import datetime, timedelta

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


