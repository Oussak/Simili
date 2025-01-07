import requests
from credentials import client_id, client_secret
from IPython.display import display

def get_token():
    token_url = 'https://sandbox-oauth.piste.gouv.fr/api/oauth/token'
    #inject cred 
    token_data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': 'openid'}
    response = requests.post(token_url, data=token_data)
    response.raise_for_status()  # vérif  erreurs
    # récup  jeton
    token_info = response.json()
    access_token = token_info['access_token']
    return access_token

