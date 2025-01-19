from modules_simili.get_token import get_token
from modules_simili.api_call_functions import *
from modules_simili.dataprep_functions import *
from credentials import client_id, client_secret
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session
import os
import requests
import json


#Step 1: get dossier legislatif
def get_doss_legi(textId, date): # LEGITEXT000006075116 2021-04-15
  url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/legiPart'
  headers = {'accept': 'application/json','Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token}
  data = { #"searchedString":"constitution 1958",
        "date": date,
        "textId":textId }
  response = requests.post(url= url, headers =headers, json= data )
  return response.json()["dossiersLegislatifs"][0]['id']

#Step 2: get list of directives

#Step 3: get Celex of directive from JORF

#Step 4: get text from Eurlex with Sparql in Cellar database 

#Step 5: clean with Firecrawl

