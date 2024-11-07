from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def config(vault_url='https://{key_vault_name}.vault.azure.net/'):
    if not vault_url:
        raise ValueError("url must be specified")
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)


    database = {}
    try:
        database['host'] = client.get_secret("database-host").value
        database['database'] = client.get_secret("database-name").value
        database['user'] = client.get_secret("database-user").value
        database['password'] = client.get_secret("database-password").value
        database['port'] = client.get_secret("database-port").value
        database['sslmode'] = client.get_secret("database-sslmode").value
    except Exception as e:
        raise Exception(f"Failed to retrieve secrets from the key vault: {e}")
    
    return database