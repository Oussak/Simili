from modules_call_api.Junction_funct_v1 import *
from modules_call_api.get_token import *
import pandas as pd 
import requests

access_token = get_token()
acess_token_prod = get_token_prod()

# Step 1: Import Legifrance database
database_FR = pd.read_excel("~/Desktop/Simili_2/data_output/Output.xlsx")
print("Step 1 : Importing Database ")

# Construction de la base de données junction 
# Step 2: Filtrer les lignes où 'Titre Article Modificateur' commence par "ordonnance"
Junction_DB = (
    database_FR[
        database_FR['Titre Article Modificateur'].str.startswith('Ordonnance', na=False)
    ][['ID Article Modificateur', 'Titre Article Modificateur', 'Version du']]
    .drop_duplicates(subset=['ID Article Modificateur']))
print("Step 2 : Filtring")

# Step 3: add dossier_legislatif id list 
Junction_DB['N° dossier legislatif'] = Junction_DB.apply(
    lambda row: get_doss_legi_id_prod(row['ID Article Modificateur'], row['Version du']),
    axis=1)
print("Step 3 : add dossier legislatif")

# Step 4: add dossier_legislatif content  
Junction_DB['Titre Dossier legislatif'] = Junction_DB.apply(
    lambda row: get_doss_legi_titre_prod(row['ID Article Modificateur'], row['Version du']),
    axis=1)
print("Step 4 : add Titre Dossier legislatif")

# Step 5: unique
Junction_DB = Junction_DB.drop_duplicates(subset='Titre Dossier legislatif')
print("Step 5 : Unique Value")

# Step 6: add liste directives
Junction_DB['Liste directives'] = Junction_DB.apply(
    lambda row: get_directives_list_vprod(row['N° dossier legislatif'] ),
    axis=1)
print("Step 6 : add liste directives")

# Step 7: data prep col liste directives
Junction_DB['ID directive'] = Junction_DB.apply(
    lambda row: get_directive_id_v2(row['Liste directives'] ),
    axis=1)
print("Step 7 : data prep col")

# Step 8: data prep col liste directives
Junction_DB= duplicate_rows_with_multiple_ids(Junction_DB, "ID directive")
print("Step 7 : explode col")

# Step 9: supp  


# Step 10: add celex 
Junction_DB['Celex'] = Junction_DB.apply(lambda row: get_celex_v2(row['ID directive']), axis=1)
print("Step 7 : add Celex")

# Step 9: Export database Junction_DB
Junction_DB.to_excel("data_output/Junction_DB.xlsx")
print("Finished")
