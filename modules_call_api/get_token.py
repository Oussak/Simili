import requests
from IPython.display import display
from credentials import *

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

def get_token_prod():
    token_url = 'https://oauth.piste.gouv.fr/api/oauth/token'  # URL de production
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id_pro,
        'client_secret': client_secret_pro,
        'scope': 'openid'
    }
    response = requests.post(token_url, data=token_data)
    response.raise_for_status()  # Vérifie les erreurs
    token_info = response.json()
    access_token = token_info['access_token']
    return access_token