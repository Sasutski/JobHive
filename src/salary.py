import requests
import time


auth_url = 'https://accounts.payscale.com'
jobalyzer_url = 'https://jobalyzer.payscale.com'
education_url = f'{jobalyzer_url}/jobalyzer/v1/impact/education'
get_token_url = f'{auth_url}/connect/token'
client_id = '<your-client-id>'
client_secret = '<your-client-secret>'

# get oauth token using given clientId and clientSecret
payload = {
  'grant_type': 'client_credentials',
  'scope': 'jobalyzer',
  'client_id': client_id,
  'client_secret': client_secret
}
token_response = requests.post(get_token_url, data=payload)
token = None
if token_response.status_code == 200:
    token = token_response.json()['access_token']
else:
    print(f'failed to get token: {token_response.text}')

job_title = 'Software Developer'
request_url = f'{education_url}?customerId={client_id}&user={client_id}&jobTitle={job_title}&autoResolveJobTitle=True'

# get the synchronous Education Impact using a get request with the Authorization Token
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(request_url, headers=headers)
print(response.json())