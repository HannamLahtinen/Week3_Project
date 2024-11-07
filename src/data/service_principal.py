from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

key_vault_name = "week3projectkeyvault"
kv_uri = f"https://{key_vault_name}.vault.azure.net"

# Authenticate using DefaultAzureCredential
credential = DefaultAzureCredential()
client = SecretClient(vault_url=kv_uri, credential=credential)

secret_name = "connection"
retrieved_secret = client.get_secret(secret_name)
connection_string = retrieved_secret.value

print("Database connection string:", connection_string)
