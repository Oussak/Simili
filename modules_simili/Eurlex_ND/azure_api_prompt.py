import os
from openai import AzureOpenAI
from dotenv import load_dotenv, find_dotenv

# Ne pas toucher aux deux lignes suivantes.
load_dotenv(find_dotenv())

# Le modèle à utiliser pour vos requêtes. Modèle recommandé : "gpt-35-turbo"
# Ces modèles alternatifs ne sont à utiliser que de façon parcimonieuse.
def html_json(html):
    os.environ["AZURE_OPENAI_DeploymentId"] = "gpt-4o-mini"
    client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
        api_key=os.getenv("AZURE_OPENAI_KEY"),  
        api_version="2024-03-01-preview",

    )
    exemple_output = '''
    {
        "Article": "2",
        "paragraphe": [
        {
            "numero": "1",
            "contenu": "La présente directive s'applique aux entités assujetties suivantes:",
            "sous_paragraphe": [
            {
                "numero": "1",
                "contenu": "les personnes physiques ou morales suivantes, agissant dans l'exercice de leur activité professionnelle:",
                "sous_paragraphe": [
                {
                    "lettre": "a",
                    "contenu": "les notaires et autres membres de professions juridiques indépendantes, lorsqu'ils participent, au nom de leur client et pour le compte de celui-ci, à toute transaction financière ou immobilière ou lorsqu'ils assistent leur client dans la préparation ou l'exécution de transactions portant sur:",
                    "sous_paragraphe": [
                    {
                        "numero": "i",
                        "contenu": "l'achat et la vente de biens immeubles ou d'entreprises commerciales;"
                    },
                    
                ]
            }
            ]
        }
        ]
    }
    ]
    }'''
    response = client.chat.completions.create(
      model=os.getenv("AZURE_OPENAI_DeploymentId"), # model = "deployment_name".
      response_format={ "type": "json_object" },
      messages=[
          {"role": "system", "content": f'''Tu es un extracteur de texte juridique en json, tu ne dois vraiment renvoyer que le json et seulement l'intérieur comme cet exemple: {exemple_output}
          Tu dois inclure l'ensemble des points, sous paragraphes et sous-sous paragraphe si ils existent tu ne dois rien oublier de ce que l'on t'envoie'''},
          {"role": "user", "content": f"Peux tu me ressortir le json avec comme information le numéro de l'article, les numeros de paragraphe les sous paragraphe et le contenu de ce texte : {html}"},
      ],
      temperature = 0
    )    
    return response.choices[0].message.content

def html_json_tcd(html,label_ligne):
    os.environ["AZURE_OPENAI_DeploymentId"] = "gpt4o"
    client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
        api_key=os.getenv("AZURE_OPENAI_KEY"),  
        api_version="2024-03-01-preview",

    )
    exemple_output = '''
    {
        "Extraction": "Article 1er, paragraphe 3",
        "contenu": les personnes physiques ou morales suivantes, agissant dans l'exercice de leur activité professionnelle." 
    }
    '''
    response = client.chat.completions.create(
      model=os.getenv("AZURE_OPENAI_DeploymentId"), # model = "deployment_name".
      response_format={ "type": "json_object" },
      messages=[
          {"role": "system", "content": f'''Tu es un extracteur de texte juridique en json, tu ne dois vraiment renvoyer que le json et seulement l'intérieur comme cet exemple: {exemple_output}
           Si on te demande un article entier, tu dois alors mettre la totalité de l'article dans le contenu, cependant si on te demande un point spécifique d'un article alors tu devra mettre dans le contenu seulement le sous point de l'article concerné
           Pour t'aider, voici la définition non exhaustive des différents éléments que l'on risque de te donner : 
            -   Paragraphe : 
                    -   Symbole : 1., 2. ...
                    -   Observations : Sous-ensemble autonome d'un article
            -   Alinéa :
                    -   Symbole : Néant 
                    -   Observation : Element non autonome d'un article ou paragraphe complexe
            -   Point :
                    -   Symbole : a), b), 1), 2), i), ii)..
                    -   Observation : Généralement précédés d'un "chapeau"'''},
          {"role": "user", "content": f"Peux tu me ressortir {label_ligne} de ce texte : {html}"},
      ],
      temperature = 0
    )    
    return response.choices[0].message.content