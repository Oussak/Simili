import requests
import json

## Additionnal calls developed but not being used 
# Call 2.1: Get article by ELI

"""
    Eli - Identifiant Européen de la Législation:
Permet d'identifier de façon unique les documents législatifs et réglementaires au sein de la base de données de Légifrance.
Déclinaison :
/eli : Préfixe indiquant qu'il s'agit d'un identifiant ELI.
/decret : Type de texte (ici un décret) peut aussi être un arrêté, une loi, ou d'autres types d'actes normatifs...
/2021/7/13 : Date de publication ou adoption (13 juillet 2021 dans cet exemple).
/PRMD2117108D : Numéro unique du décret
/jo : Indication que le document a été publié dans le Journal Officiel.
/article_1 : Référence à un article spécifique dans le document (ici l'article 1).
"""
def get_article_byELI(idEliOrAlias):
  headers_2 = {"accept": "application/json","Content-Type": "application/json", 'Authorization': 'Bearer ' + access_token}
  data = {"idEliOrAlias": idEliOrAlias } # exemple: "/eli/decret/2021/7/13/PRMD2117108D/jo/article_1"
  url= "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/getArticleWithIdEliOrAlias"
  response = requests.post(url, headers=headers_2,json=data)
  response_json = response.json()
  return {
        "etat": response_json['article']['textTitles'][1]['etat'],
        "id": response_json['article']['id'],
        "titresTM": response_json['article']['context']['titresTM'],
        "titreLong": response_json['article']['textTitles'][1]["titreLong"],
        "texte": response_json['article']['texte']
    }

# Call 2.X: G
"""Fonction qui test la récupération de la liste des articles par leur identifiant Cid 
en retournant le contenu et le  message status_code
"""

def getArticle_ByCid_allversions_test(article_cid):
  API_URL = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/getArticleByCid'
  headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
  data = { 'cid': article_cid }
  response = requests.post(API_URL, json=data, headers=headers)
  response_json = response.json()
  return {"contenu": response.json(),
          "reponse status code ":response.status_code }
  
  
# Call 2.2: Get the last version of an article by it Cid with these info : Date Debut, Date Fin, Version, Texte
"""Donne date debut date de fin derniere version et texte  
"""

from datetime import datetime

def format_date(timestamp_ms):
    timestamp_s = timestamp_ms // 1000  # Convertir millisecondes en secondes
    return datetime.utcfromtimestamp(timestamp_s).strftime('%Y-%m-%d')

def getArticle_ByCid_last_version(article_cid):
  API_URL = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/getArticleByCid'
  headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
  data = { 'cid': article_cid }
  response = requests.post(API_URL, json=data, headers=headers)
  response_json = response.json()
  return {"Date Debut:" : format_date(response.json()['listArticle'][0]['dateDebut']),
          "Date Fin:": format_date(response.json()['listArticle'][0]['dateFin']),
          "Version:": response.json()['listArticle'][0]['versionArticle'],
          "Texte:": response.json()['listArticle'][0]['texte']
          }

# Call 2.3: get all_versions of an article by cid 

def get_articles_by_cid_all_versions(article_cid):
    API_URL = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/getArticleByCid'
    headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
    data = {'cid': article_cid}
    response = requests.post(API_URL, json=data, headers=headers)
    response_json = response.json()
    # Liste des articles récupérés
    articles = response_json.get('listArticle', [])
    # Résultats formatés
    formatted_articles = []
    for article in articles:
        formatted_articles.append({
            "Date Debut": format_date(article.get('dateDebut')),
            "Date Fin": format_date(article.get('dateFin')),
            "Version": article.get('versionArticle'),
            "Texte": article.get('texte')
        })
    return formatted_articles

# Call 2.4: get all_versions of an article by cid 
    """
Récupère le contenu d'un dossier legislatif par son identifiant.
Input : Identifiant technique du dossier législatif "id": "JORFDOLE000038049286"
    """
    
def dossierLegislatif(id): #JORFDOLE000038049286
	headers = {'accept': 'application/json','Content-Type': 'application/json','Authorization': 'Bearer ' + access_token}
	url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/dossierLegislatif'
	data = {"id":id}
	reponse = requests.post(headers = headers , url= url, json= data)
	reponse_json = reponse.json()
	return reponse_json

# Call 2.5: get all_versions of an article by cid 
"""
Récupère des informations précises sur des articles de loi, des codes ou d'autres textes juridiques 
a partir d'identifiant ("textId") et de sa date de vigueur:ummary_
"""

def legipart(textId, date): # LEGITEXT000006075116 2021-04-15
  url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/legiPart'
  headers = {'accept': 'application/json','Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token}
  data = { #"searchedString":"constitution 1958",
        "date": date,
        "textId":textId }
  response = requests.post(url= url, headers =headers, json= data )
  return response.json()

# Call 2.6: get all_versions of an article by cid 
    """
    Pour trouver et récup JORF ordonnance Exemple: https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000042636234
    """
    
def getJOFR(textCid :str): #JORFTEXT000042636234
  url= 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/jorf'
  headers= {'accept': 'application/json',
		'Content-Type': 'application/json',
		'Authorization': 'Bearer ' + access_token}
  data= {"searchedString":"","textCid":textCid}
  response = requests.post( headers =headers, url= url, json= data )
  response_json = response.json()
  return response_json

# Call 2.7: get all_versions of an article by cid 

def getArticle_metadata(id : str):
  headers= {'accept': 'application/json','Content-Type': 'application/json','Authorization': 'Bearer ' + access_token}
  url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/getArticle'
  data = {"id":id}
  response= requests.post(url=url,  headers=headers, json = data)
  return {"num":  response.json()["article"]['num'],
          "etat": response.json()["article"]['etat'],
         "Text" : response.json()["article"]['texte']}




# Call 2.8: get an article text by it cid and implementation date (version 1)

def get_article_text_by_cid_and_implementDate(article_cid, start_date):
    API_URL = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/getArticleByCid'
    headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
    data = {'cid': article_cid}

    response = requests.post(API_URL, json=data, headers=headers)
    response_json = response.json()

    # Convertir la date en millisecondes depuis l'époque Unix
    start_date_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)

    # Parcourir les articles du tableau pour trouver une correspondance
    articles = response_json.get('listArticle', []) # listArticle output json key de la requete
    for article in articles:
        if article.get('dateDebut') == start_date_timestamp:
            return article.get('texte', "Texte non disponible")

    # Si aucun article ne correspond
    return "Aucun article trouvé pour la date de début donnée."

# Call 2.9: Get old article content by cid and end date (version 1)

def get_article_text_by_cid_and_end_date(article_cid, end_date):
    API_URL = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/getArticleByCid'
    headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
    data = {'cid': article_cid}

    response = requests.post(API_URL, json=data, headers=headers)
    response_json = response.json()

    # Convertir la date en millisecondes depuis l'époque Unix
    end_date_timestamp = int(datetime.strptime(end_date, "%d-%m-%Y").timestamp() * 1000) #(ko: %Y-%m-%d ) (ko:"%d-%m-%Y" )

    # Parcourir les articles pour trouver une correspondance
    articles = response_json.get('listArticle', [])
    for article in articles:
        if article.get('dateFin') == end_date_timestamp:
            return article.get('texte', "Texte non disponible")

    # Si aucun article ne correspond
    return "Aucun article trouvé pour la date de début donnée."

# Call 2.10 : 
    """Permet d'obtenir le contenu complet d'un code juridique
    """
def get_code(textId,sctCid,abrogated, date):
  headers = {"Authorization": "Bearer " + access_token , "Content-Type": "application/json" }
  BASE_URL = "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/code"
  data = {
    "textId": textId,         #"LEGITEXT000006073984",  # Code des assurances
    "sctCid": sctCid,         #"LEGIARTI000048769089",  # ID article
    "abrogated": abrogated,   # False,                # exclure les textes abrogés
    "date":date  #"2024-11-15",              # Date de référence
    }
  response = requests.post(BASE_URL, json=data, headers=headers)
  response_json = response.json()
  return download_json(response_json)

# CAll 2.11: 

    """
    Récupère un extrait (section ou article) d'une version spécifique d'un texte à partir des identifiants du texte (textCid) 
    et de l'extrait section ou article: "elementCid"
    """
def textCidAndElementCid(textCid, elementCid): # text cid: LEGITEXT000006072050 Element Cid LEGIARTI000006901817
  url = "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/chrono/textCidAndElementCid"
  headers = {
      'accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + access_token}
  data = { "textCid": textCid, # code du travail
    "elementCid": elementCid # Article L2262-8
  }
  response = requests.post(url, headers=headers, json= data)
  response_json= response.json()
  return response_json

