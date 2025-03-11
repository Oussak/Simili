
import os
import requests
import json

from requests_oauthlib import OAuth2Session
from SPARQLWrapper import SPARQLWrapper, JSON
from get_token import get_token_prod


acess_token_prod = get_token_prod()

# Step 1: get dossier legislatif - from LegiFr 
def get_doss_legi(textId:str, date:str):
    """LegiFrance Call API pour passer de l'article modificateur d'une ordonnance a un dossier légis
     

    Args:
        textId (str):nunéro id de l'article modificateur. Exemple: LEGITEXT000006075116
        date (str): Date de mise en oeuvre/ rentrée en vigueur. Exemple: 2021-04-15

    Returns:
        Num: référence de dossier législatif
    """
  
    url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/legiPart'
    headers = {'accept': 'application/json','Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token}
    data = { #"searchedString":"constitution 1958",
        "date": date,
        "textId":textId }
    response = requests.post(url= url, headers =headers, json= data )
    return response.json()["dossiersLegislatifs"][0]


# Step 2: get list of directives - from LegiFr 

def get_directives_list(id:str):
    """LegiFrance Call API pour aller de dossier législatif aux numéros de directives

    Args:
        id (str): Input N°ID du dossier législatif .Exemple: JORFDOLE000038049286

    Returns:
        list: liste de numéros de directive européeenne 
    """
    
    headers = {'accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + get_token_prod}
    url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/dossierLegislatif'
    data = {"id":id}
    reponse = requests.post(headers = headers , url= url, json= data)
    liste = reponse.json()['dossierLegislatif']['dossiers']
    id_textes = [item['idTexte'] for item in liste]
    return id_textes


# Step 3: get celex from directive (JORF) - from LegiFr 

def get_directives_list(textId):
    """LegiFrance Call API pour obtenir le numéro celex à partir de numéro de directive européenne

    Args:
        textId (numéro): de directive européenne

    Returns:
        numéro: celex 
    """
    url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/legiPart'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_token_prod}'
    }
    data = { "textId": textId}
    try:
        response = requests.post(url=url, headers=headers, json=data)
        response.raise_for_status()  # Vérifie les erreurs HTTP
        liste = response.json()['dossierLegislatif']['dossiers']
        #id_textes = [item['idTexte'] for item in liste]
        return response
        #return response.json()["dossiersLegislatifs"][0]['id'] 
    except requests.RequestException as e:
        print(f"Erreur de requête : {e} pour textId={textId} .")
        return None
    except KeyError:
        print(f"L'identifiant n'a pas pu être récupéré pour textId={textId} .")
        return None

# Step 4: get url of the directive - from LegiFr 
def get_celex_full(textCid :str):
    """Function LegiFr from num de directive au numéro Celex

    Args:
        textCid (str): input the reference of a dossier legislatif. Exemple : JORFTEXT000042636234

    Returns:
        Numéro: Celex 
    """
    url= 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/jorf'
    headers= {'accept': 'application/json',
		'Content-Type': 'application/json',
		'Authorization': 'Bearer ' + get_token_prod}
    data= {"searchedString":"","textCid":textCid}
    response = requests.post( headers =headers, url= url, json= data )
    response_json = response.json()
    return response_json


# Step 5: get url from celex - From Eurlex
def celextourl_data(celex_id):
    """
    Function Eurlex from Celex to url 
    """

    query = f"""
    PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?property ?value
    WHERE {{
      ?acte cdm:resource_legal_id_celex "{celex_id}"^^xsd:string ;
            ?property ?value .
    }}
    """
    sparql = SPARQLWrapper("https://publications.europa.eu/webapi/rdf/sparql")
    sparql.setQuery(query)            
    sparql.setReturnFormat(JSON)         
    results = sparql.query().convert()   
    return results
