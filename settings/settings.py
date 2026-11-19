import os
# Налаштування коннекту до API Helpi
url = "https://helpi-prod.azurewebsites.net/api/feeddataset/105"
headers = os.getenv("X_API_KEY_TO_HELPI")

# Налаштування коннекту до КОБО
form_uid = 'aDnRtwPJGviJz555vK8G8L'
api_token = os.getenv("KOBO_API_TOKEN")

key_json = os.getenv("GOOGLE_CREDENTIALS_JSON_KEY")
