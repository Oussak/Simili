from modules_simili.Junction_funct import *
from modules_simili.get_token import *
import pandas as pd 

access_token = get_token()

# Import Legifrance database
database_FR = pd.read_excel("~/Desktop/Simili_2/data_output/Output.xlsx")

# Filtrer les lignes où 'Titre Article Modificateur' commence par "ordonnance"
Junction_DB = database_FR[
    database_FR['Titre Article Modificateur'].str.startswith('Ordonnance', na=False)][['ID Article Modificateur',
                                                                                       'Titre Article Modificateur', 
                                                                                       'Version du']]

# add dossier_legislatif
Junction_DB['dossier_legislatif'] = Junction_DB.apply(
    lambda row: get_doss_legi_v2(row['ID Article Modificateur'], row['Version du']),
    axis=1)

# add celex 
Junction_DB['Celex'] = Junction_DB.apply(
    lambda row: get_celex_v2(row['dossier_legislatif']), axis=1)

# Export database Junction_DB
Junction_DB.to_excel("data_output/Junction_DB.xlsx")
