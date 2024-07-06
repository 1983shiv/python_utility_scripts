import requests

client_id = "21af32a9-aa6c-4685-b6a7-8de5ac22dfa2"
client_pass = ""
client_pin = ""
auth_code = "4OWcKB"
api_key = "21af32a9-aa6c-4685-b6a7-8de5ac22dfa2"
api_secret = "y5jc8u1x7p"

redirect_uri = "http://localhost:3000"

login_url = "https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={}&redirect_uri={}".format(api_key, redirect_uri)

url = "https://api.upstox.com/v2/login/authorization/token"

headers = {
    'accept' : 'application/json',
    'Api-Version': '2.0',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# request data

data = {
    'code': auth_code,
    'client_id' : client_id,
    'client_secret': api_secret,
    'redirect_uri': redirect_uri,
    'grant_type': 'authorization_code'
}

response = requests.post(url, headers=headers, data=data)

if response.status_code == 200:
    print("Access Token", response.json().get('access_token'))
else:
    print("Error: ", response.status_code, response.text)