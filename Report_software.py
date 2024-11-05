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




