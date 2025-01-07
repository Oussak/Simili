
import requests


# Call 1.1: ping pong test
def ping_pong_test(access_token): 
    headers_1 = {'accept': 'text/plain', 'Authorization': 'Bearer ' + access_token}
    output = requests.get("https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/ping", headers=headers_1).text
    return output
    
## Call bellow to full fill the table with additional content :
# Call 1.2 : Get content of previous version of an article (version 2)

def getArticle_prev_vers(id: str):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
    url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/getArticle'

    try:
        # Requête initiale pour obtenir les versions de l'article
        data = {"id": id}
        response = requests.post(url=url, headers=headers, json=data)

        # Vérification du code de statut HTTP
        if response.status_code != 200:
            return "KO status_code"

        # Extraction des données de l'article
        article = response.json().get("article", {})
        article_versions = article.get("articleVersions", [])

        # Vérification de l'existence d'une version précédente
        if len(article_versions) < 2:
            return "KO version précédente"

        # Récupération de l'ID de la version précédente
        nouvel_id = article_versions[-2].get("id")
        if not nouvel_id:
            return "KO absence ID de la version précédente "

        # Requête pour la version précédente
        nouveau_data = {"id": nouvel_id}
        response_nouvelle = requests.post(url=url, headers=headers, json=nouveau_data)

        # Vérification du code de statut HTTP pour la seconde requête
        if response_nouvelle.status_code != 200:
            return "KO status_code HTTP seconde requête"

        # Extraction des données de la version précédente
        response_json = response_nouvelle.json()
        texte = response_json.get("article", {}).get("texte")

        # Vérification si le texte de l'article existe
        return texte if texte else "KO"

    except Exception as e:
        # Gestion des exceptions (problème de connexion, JSON invalide, etc.)
        print(f"Erreur : {e}")
        return "KO"
    
# Call 1.3 : Get content new version of an article (version 2)
def getArticle(id: str):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
    url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/getArticle'
    data = {"id": id}

    try:
        response = requests.post(url=url, headers=headers, json=data)
        # Vérification du statut HTTP
        if response.status_code != 200:
            return "KO Status Code"

        # Extraction des données
        article = response.json().get("article", {})

        # Vérification si le texte de l'article est présent
        if "texte" in article:
            return article["texte"]
        else:
            return "KO article pas trouvé"

    except Exception as e:
        # Gestion des exceptions (erreur de connexion, JSON invalide, etc.)
        print(f"Erreur : {e}")
        return "KO autre"

# Bellow API call to build the main table: 
# Call 1.4 : Récupère une version (plage de dates) d'un texte (textCid) et version en vigueur (date) 

def get_text_modif_byDateslot_textCid_extract_content(access_token, textCid, startYear, endYear): #LEGITEXT000006073984 code des assurances
  headers = { 'accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token}
  data = {  "endYear": endYear,  #"dateConsult": "2021-04-15",
  "startYear": startYear,
  "textCid": textCid  }
  url = 'https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/chrono/textCid'
  response = requests.post(url, headers=headers, json=data)
  response_json= response.json()
  return  response_json

  