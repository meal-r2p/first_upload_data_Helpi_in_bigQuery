import os
import json
from google.cloud import bigquery

# Налаштування коннекту до API Helpi
url = "https://helpi-prod.azurewebsites.net/api/feeddataset/105"
api_key_helpi = os.getenv("X_API_KEY_TO_HELPI")
headers = {
    "X-API-KEY": api_key_helpi
}

# Налаштування коннекту до КОБО
form_uid = 'aDnRtwPJGviJz555vK8G8L'
api_token = os.getenv("KOBO_API_TOKEN")

# Завантаження secret_json_file
client = bigquery.Client.from_service_account_info(
    json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON_KEY"))
)
