from modules_simili.get_token import get_token
from credentials import client_id, client_secret
from modules_simili.api_call_functions import *
from modules_simili.dataprep_functions import *

access_token = get_token()

# Test co
if ping_pong_test(access_token) == 'pong':
    print("Successful ping pong test")

# Step 1: Retreiving data from Léfifrance  
try: 
    json_output =  get_text_modif_byDateslot_textCid_extract_content(access_token, "LEGITEXT000006073984", "2019", "2020")
    print("Etape 1: Requête API LégiFrance")
except Exception as e:
    print("Échec : Une erreur est survenue lors du Call. Détails : {e}")

# Step 2: Formating data
try: 
    panda_output= transform_json_to_dataframe(json_output)
    print("Etape 2: Formatage des données récupérées...")
except Exception as e:
    print("Etape 2: Échec : Une erreur est survenue lors du formatage des données. Détails : {e}")


#Step 3: Exporting
try:
    panda_output.to_excel("data_output/Output.xlsx")
    print("Etape 3: Fichier Excel a été exporté avec succès !")
except Exception as e:
    print(f"Etape 3: Échec : Une erreur est survenue lors de l'enregistrement. Détails : {e}")
    