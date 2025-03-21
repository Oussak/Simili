
import requests
from modules_call_api.get_token import get_token, get_token_prod

access_token = get_token()
access_token_prod = get_token_prod()

# Call 1 - ping pong test
def ping_pong_test_prod(): 
    headers_1 = {'accept': 'text/plain', 'Authorization': 'Bearer ' + access_token_prod}
    output = requests.get("https://api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/ping", headers=headers_1).text
    return output

# Call 2 - API call to build the main table: 
# Récupère une version (plage de dates) d'un texte (textCid) et version en vigueur (date) 

def get_text_modif_byDateslot_textCid_extract_content_prod(access_token, textCid, startYear, endYear): 
	#LEGITEXT000006073984 code des assurances
  headers = { 'accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token_prod}
  data = {  "endYear": endYear,  #"dateConsult": "2021-04-15",
  "startYear": startYear,
  "textCid": textCid  }
  url = 'https://api.piste.gouv.fr/dila/legifrance/lf-engine-app/chrono/textCid'
  response = requests.post(url, headers=headers, json=data)
  response_json= response.json()
  return  response_json


# Call 3 : Get content of previous version of an article (version 2)

def getArticle_prev_vers_prod(id: str):
    headers = {'accept': 'application/json','Content-Type': 'application/json','Authorization': 'Bearer ' + access_token_prod}
    url = 'https://api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/getArticle'

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
    
# Call 4 - Get content new version of an article (version 2)
def getArticle_prod(id: str):
    headers = {'accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token_prod}
    url = 'https://api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/getArticle'
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

# Call 4 - Building the column Contenu_Nouv_Vers_Article for the NEW content of an article 
def ajout_col_coutenu_NV_prod(df):
    df['Contenu_Nouv_Vers_Article'] = df.apply( lambda x: getArticle_prod( x['ID Article Cible']), axis=1)

    
# Call 5 - Building the column Contenu_Ancien_Article for the OLD content of an article
def ajout_col_AV_prod(df):
    df['Contenu_Ancien_Article'] = df.apply( lambda x: getArticle_prev_vers_prod(x['ID Article Cible']), axis=1)

    

  