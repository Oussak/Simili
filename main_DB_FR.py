from modules_simili.get_token import get_token
from credentials import client_id, client_secret
from modules_simili.LegiFR_call_funct import *
from modules_simili.dataprep_funct import *

access_token = get_token()

# Test connection 
if ping_pong_test(access_token) == 'pong':
    print("Successful ping pong test")

# Step 1: Retreiving data from Léfifrance  
try: 
    json_output =  get_text_modif_byDateslot_textCid_extract_content(access_token, "LEGITEXT000006072026", "2020", "2021")
    print("Etape 1: Requête API LégiFrance")
except Exception as e:
    print("Échec : Une erreur est survenue lors du Call. Détails : {e}")

# Step 2: Formating data
try: 
    panda_output= transform_json_to_dataframe(json_output)
    print("Etape 2: Formatage des données récupérées")
except Exception as e:
    print("Etape 2: Échec : Une erreur est survenue lors du formatage des données. Détails : {e}")

#Step 3:  adding a new colomun content of OLD version 
print("Début de l'étape 3")
print("Etape 3 en cours")

try: 
    ajout_col_AV(panda_output)
    print("Etape 3: Ajout de l'ancien contenu des articles avec succès")
except Exception as e:
    print("Etape 3: Échec, une erreur est survenue lors du Call. Détails : {e}")
    
#Step 4:  adding a new colomun content of new version 
print("Début de l'étape 4")
print("Etape 4 en cours")
try: 
    ajout_col_coutenu_NV(panda_output)
    print("Etape 4: Ajout du nouveau contenu des articles avec succès !")
except Exception as e:
    print("Échec 4: Échec, une erreur est survenue lors du Call. Détails : {e}")

#Step 5: adding a colomun to compare content
try: 
    compare_AV_vs_NV(panda_output)
    print("Etape 5: Ajout de la colonne comparative")
except Exception as e:
    print("Échec 5: Échec, une erreur est survenue lors du Call. Détails : {e}")

#Step 6: Exporting database 1
try:
    panda_output.to_excel("data_output/DB_Legifrance.xlsx")
    print("Etape 6: Fichier Excel a été exporté avec succès !")
except Exception as e:
    print(f"Etape 6: Échec : Une erreur est survenue lors de l'enregistrement. Détails : {e}")

