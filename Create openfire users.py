import requests
import base64

# Replace with your Openfire server details
OPENFIRE_API_URL = "http://127.0.0.1:9090/plugins/restapi/v1.10.1"
secret_key = "s3cretKey"

def create_user(username, password):
    # Encode the secret key in base64

    url = f"{OPENFIRE_API_URL}/users"
    headers = {
        "Authorization": f'Bearer {secret_key}',
        "Content-Type": "application/json"
    }
    data = {
        "username": username,
        "password": password,
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"User {username} created successfully.")
    else:
        print(f"Failed to create user. Status code: {response.status_code}, Response: {response.text}")
        print(f"Response Headers: {response.headers}")

# Replace with your desired user details
create_user('investor8', '1234')
