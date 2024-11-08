from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Key Vault setup
key_vault_name = "week3projectkeyvault"
kv_uri = f"https://{key_vault_name}.vault.azure.net"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=kv_uri, credential=credential)

def get_secret(secret_name):
    try:
        # Get the secret by name from Azure Key Vault
        retrieved_secret = client.get_secret(secret_name)
        return retrieved_secret.value  # Return the value of the secret
        
    except Exception as e:
        raise Exception(f"Error retrieving secret '{secret_name}': {e}")


