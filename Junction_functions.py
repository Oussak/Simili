import os
from dotenv import load_dotenv
import json
from modules_simili.get_token import get_token
import requests
from requests_oauthlib import OAuth2Session
from SPARQLWrapper import SPARQLWrapper, JSON



access_token = get_token()

# Step 1: get dossier legislatif
# Article modificateur d'un article d'ordonnance vers dossier législatif (via ordonnance):
def get_doss_legi(textId, date): 
  url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/legiPart'
  headers = {'accept': 'application/json','Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token}
  data = { #"searchedString":"constitution 1958",
        "date": date,
        "textId":textId }
  response = requests.post(url= url, headers =headers, json= data )
  return response.json()["dossiersLegislatifs"][0]['id']

# Step 2: get list of directives
# De dossier législatif aux numéros de directives
def dossierLegislatif(id): 
	headers = {'accept': 'application/json','Content-Type': 'application/json','Authorization': 'Bearer ' + access_token}
	url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/dossierLegislatif'
	data = {"id":id}
	reponse = requests.post(headers = headers , url= url, json= data)
	reponse_json = reponse.json()
	return reponse_json['dossierLegislatif']['dossiers']

# Step 3: get Celex of directive from JORF
# De numéros de directives a Celex de directives

def get_celex(textCid :str): #JORFTEXT000042636234
  url= 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/jorf'
  headers= {'accept': 'application/json',
		'Content-Type': 'application/json',
		'Authorization': 'Bearer ' + access_token}
  data= {"searchedString":"","textCid":textCid}
  response = requests.post( headers =headers, url= url, json= data )
  response_json = response.json()
  return response_json['nor']

# Step 4: get text from Eurlex with Sparql in Cellar database 
