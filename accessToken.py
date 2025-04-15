import requests
from requests.auth import HTTPBasicAuth

consumer_key = '6p69uKAB7ddcToUbOk9oI9LjUIR6stADbZdHDPWsMJxy2mvX'
consumer_secret = 'QBRr5lGMdBcKndAGO4dqO1bEWyJTk7VJrob89QsFvzGLfEjLLZ4YmOys0E2Hacrp'
access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

headers = {
    'Content-Type': 'application/json; charset=utf-8'
}

response = requests.get(
    access_token_url,
    headers=headers,
    auth=HTTPBasicAuth(consumer_key, consumer_secret)
)

if response.status_code == 200:
    access_token = response.json().get('access_token')
    print(access_token)
else:
    print(f"Failed to fetch access token. Status code: {response.status_code}")
    print(response.text)
