from service_principal import get_secret

def config():
   
    database = {}
    try:
       
        database['host'] = get_secret("database-host")
        database['database'] = get_secret("database-name")
        database['user'] = get_secret("database-user")
        database['password'] = get_secret("database-password")
        database['port'] = get_secret("database-port")
        database['sslmode'] = get_secret("database-sslmode")
    except Exception as e:
        raise Exception(f"Failed to retrieve secrets from the key vault: {e}")
    
    return database
