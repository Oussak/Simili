import os
import json
import requests
from dotenv import load_dotenv
from modules_simili.get_token import get_token
from requests_oauthlib import OAuth2Session
from SPARQLWrapper import SPARQLWrapper, JSON
from firecrawl import FirecrawlApp
from credentials import api_key_firecraw

access_token = get_token()

## Script to get from Article modificateur (article d'ordonnance) to Celex (in Eurlex) 

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

def get_celex_v2(textCid: str):
    url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/jorf'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
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
def get_doss_legi_v2(textId, date):
    try:
        url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/legiPart'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }
        data = {"date": date, "textId": textId}

        response = requests.post(url=url, headers=headers, json=data)
        response.raise_for_status()  # Vérifiez les erreurs HTTP

        # Vérifiez si la réponse contient "dossiersLegislatifs"
        dossiers = response.json().get("dossiersLegislatifs", [])
        if dossiers:
            return dossiers[0]['id']
        else:
            print(f"Aucun dossier trouvé pour textId={textId}, date={date}")
            return None
    except requests.RequestException as e:
        print(f"Erreur de requête : {e} pour textId={textId}, date={date}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Erreur JSON : {e} pour textId={textId}, date={date}")
        return None
