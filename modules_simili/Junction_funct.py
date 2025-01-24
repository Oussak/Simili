import os
import json
import requests
from dotenv import load_dotenv
from modules_simili.get_token import get_token
from modules_simili.get_token import get_token_prod
from requests_oauthlib import OAuth2Session
from SPARQLWrapper import SPARQLWrapper, JSON
from firecrawl import FirecrawlApp
from credentials import *

access_token = get_token()
acess_token_prod = get_token_prod()

## Script to get from Article modificateur (article d'ordonnance) to Celex (in Eurlex) 

# Step 1 : get_doss_legi --  Sandbow version 
def get_doss_legi_id(textId, date):
    url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/legiPart'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'}
    data = {"date": date,"textId": textId }
    try:
        response = requests.post(url=url, headers=headers, json=data)
        response.raise_for_status()  # Vérifie les erreurs HTTP (4xx ou 5xx)
        return response.json()["dossiersLegislatifs"][0]['id']
    except requests.RequestException as e:
        print(f"Erreur de requête : {e} pour textId={textId} et date={date}.")
        return None
    except (KeyError, IndexError):
        print(f"L'identifiant n'a pas pu être récupéré pour textId={textId} et date={date}.")
        return None
    
# Step 1 : get_doss_legi --  Production version 
def get_doss_legi_id_prod(textId, date):
    url = 'https://api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/legiPart'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {acess_token_prod}'}
    data = {"date": date,"textId": textId }
    try:
        response = requests.post(url=url, headers=headers, json=data)
        response.raise_for_status()  # Vérifie les erreurs HTTP (4xx ou 5xx)
        return response.json()["dossiersLegislatifs"][0]['id']
    except requests.RequestException as e:
        print(f"Erreur de requête : {e} pour textId={textId} et date={date}.")
        return None
    except (KeyError, IndexError):
        print(f"L'identifiant n'a pas pu être récupéré pour textId={textId} et date={date}.")
        return None
    
    
# Step 3 : get_doss_titre --  Sandbox version 
def get_doss_legi_titre(textId, date):
    url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/legiPart'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'}
    data = {"date": date,"textId": textId }
    try:
        response = requests.post(url=url, headers=headers, json=data)
        response.raise_for_status()  # Vérifie les erreurs HTTP (4xx ou 5xx)
        return response.json()["dossiersLegislatifs"][0]['titre']
    except requests.RequestException as e:
        print(f"Erreur de requête : {e} pour textId={textId} et date={date}.")
        return None
    except (KeyError, IndexError):
        print(f"L'identifiant n'a pas pu être récupéré pour textId={textId} et date={date}.")
        return None

# Step 3 : get_doss_titre --  Prod version 
def get_doss_legi_titre_prod(textId, date):
    url = 'https://api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/legiPart'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {acess_token_prod}'}
    data = {"date": date,"textId": textId }
    try:
        response = requests.post(url=url, headers=headers, json=data)
        response.raise_for_status()  # Vérifie les erreurs HTTP (4xx ou 5xx)
        return response.json()["dossiersLegislatifs"][0]['titre']
    except requests.RequestException as e:
        print(f"Erreur de requête : {e} pour textId={textId} et date={date}.")
        return None
    except (KeyError, IndexError):
        print(f"L'identifiant n'a pas pu être récupéré pour textId={textId} et date={date}.")
        return None

# Step 4: get dossier legislatif - Sandox version 
def get_directives_list(textId): 
  url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/dossierLegislatif'
  headers = {'accept': 'application/json','Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token}
  data = { "textId":textId }
  response = requests.post(url= url, headers =headers, json= data )
  reponse_json = response.json()
  return reponse_json

# Step 4: get dossier legislatif - prod version 
def get_directives_list_vprod(id):
    url = 'https://api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/dossierLegislatif'  # URL de production
    headers = {'accept': 'application/json','Content-Type': 'application/json','Authorization': 'Bearer ' + acess_token_prod  }
    data = {"id":id}
    response = requests.post(url=url, headers=headers, json=data)
    response_json = response.json()
    if response_json.get('status') == 'Internal Server Error':
        return "" 
    else:
        return response_json['dossierLegislatif']['dossiers']


 # Step 2: get list of directives
# De dossier législatif aux numéros de directives
def get_directive_id(textes):
    for item in textes:
        # Vérification insensible à la casse
        if 'directive' in item['libelleTexte'].lower():
            return item['idTexte']
    return None

def get_directive_id_v2(textes):
    directive_ids = []

    for item in textes:
        # Vérification insensible à la casse pour le mot 'directive'
        if 'directive' in item['libelleTexte'].lower():
            directive_ids.append(item['idTexte'])  # Ajouter l'idTexte à la liste

    return directive_ids  # Retourne la liste, vide si aucune directive n'est trouvée

import pandas as pd

def duplicate_rows_with_multiple_ids(df, column):
    df[column] = df[column].apply(lambda x: x if isinstance(x, list) else [x])  # S'assurer que les valeurs sont des listes
    return df.explode(column, ignore_index=True)

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

def get_celex_v2(textCid: str):
    url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/jorf'
    headers = { 'accept': 'application/json','Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token}
    data = {"searchedString": "", "textCid": textCid}
    try:
        # Effectuer la requête POST
        response = requests.post(url=url, headers=headers, json=data)
        response.raise_for_status()  # Vérifie si une erreur HTTP a eu lieu
        # Tenter de parser la réponse en JSON
        response_json = response.json()
        # Vérifie si la clé 'nor' est présente dans la réponse
        if 'nor' not in response_json:
            raise KeyError("La clé 'nor' est absente de la réponse.")
        return response_json['nor']

    except requests.exceptions.RequestException as e:
        # Gestion des erreurs liées à la requête HTTP
        return f"Erreur HTTP lors de l'accès à l'API : {e}"

    except ValueError as e:
        # Gestion des erreurs de parsing JSON
        return f"Erreur de parsing JSON : {e}"

    except KeyError as e:
        # Gestion des erreurs de clé manquante dans la réponse
        return f"Erreur : {e}"
      
# Step 4: get text from Eurlex with Sparql in Cellar database 
def celextourl_data(endpoint_url, celex_id):
    # Préparer la requête SPARQL
    query = f"""
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?property ?value
    WHERE {{
      ?acte cdm:resource_legal_id_celex "{celex_id}"^^xsd:string ;
            ?property ?value .
    }}
    """
    # Initialiser le wrapper SPARQL
    sparql = SPARQLWrapper(endpoint_url) #inject url endpoint
    sparql.setQuery(query)               # inject query
    sparql.setReturnFormat(JSON)          # set in json format
    results = sparql.query().convert()   # run
    return results

# Step 5: extract celex from Cellar output 
def extract_celex_link(data):
    return next(
        (item['value']['value'] for item in data['results']['bindings']
         if 'value' in item and 'value' in item['value'] and 'http://publications.europa.eu/resource/celex/' in item['value']['value']),
        None
    )

#Step 6: Scrape a website: with firecraw
def scrape_w_firecraw(lien_directive): 
    app = FirecrawlApp(api_key=api_key_firecraw)
    scrape_result= app.scrape_url(lien_directive, params={'formats': ['markdown']})
    return scrape_result

## Step 7: Combine all functions to get celex from article modificateur (art ordonnance )
