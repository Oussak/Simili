# imports standards 
import io
from dotenv import load_dotenv

# imports tiers 
import streamlit as st
import pandas as pd

# Import API calls
from modules_call_api.LegiFR_call_funct import *
from modules_call_api.LegiFR_call_prod_funct import *
from modules_call_api.get_token import *
from modules_call_api.Junction_funct_v1 import *
from modules_call_api.Junction_funct_v2 import *

# Import DE funct
from modules_data_eng.dataprep_funct import *

# Import LLM funct
from modules_llm.LLM_Analytic_changes import *

load_dotenv()

# Titre centré et stylisé
st.markdown(
    """
    <h1 style='text-align: center; color: navy;'> S i m i l i (dev) </h1>    
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style='font-size: 15px; color: #333; max-width: 1300; line-height: 1.5;'>
        Une solution pour le suivi des amendements des textes français, d’aide à la transposition
        des textes européens et de génération de rapports de synthèses personnalisables.
    </p>
    """,
    unsafe_allow_html=True
)

# Étape 1 : Sélection du Code Juridique

codes = {
    "Code monétaire et financier": "LEGITEXT000006072026",
    "Code civil": "LEGITEXT000006070721",
    "Code de commerce": "LEGITEXT000005634379",
    "Code des assurances": "LEGITEXT000006073984",
    "Code pénal": "LEGITEXT000006070719",
    "Code du travail": "LEGITEXT000006072050",
    "Code de la consommation": "LEGITEXT000006069565",
    "Code de la sécurité sociale": "LEGITEXT000006073189",
    "Code de procédure civile": "LEGITEXT000006070716",
    "Code de procédure pénale": "LEGITEXT000006071154",
    "Code de l'environnement": "LEGITEXT000006074220",
    "Code général des impôts": "LEGITEXT000006069574"
}


selected_code = st.selectbox("Sélectionnez un code juridique :", options=list(codes.keys()))
textCid = codes[selected_code]


# Étape 2 : input dates 

annee_debut = st.text_input("Entrez la date de début (année ou format JJ-MM-AAAA) :", value="2020")
annee_fin = st.text_input("Entrez la date de fin (année ou format JJ-MM-AAAA) :", value="2021")


# Filtrage sur N° de décret / ordonnance / loi

filtrer_numero = st.radio("Voulez-vous filtrer sur un N° de décret / ordonnance / loi ?", ("Non", "Oui"))

numero_1 = ""

if filtrer_numero == "Oui":
    numero_1 = st.text_input("Entrez un numéro de décret / ordonnance / loi ou mot clé :",
                             value="Ordonnance n°2020-115").strip()


# Activation brique LLM

active_llm = st.radio("Voulez vous avoir une analyse des changements de chaque article suivi d'un résumé global des changements ?  ", ("Non", "Oui"))

if active_llm == "Oui":
    llm_limit = st.selectbox("LLM limite (nbr de lignes):", options=[10, 20, 30])
    audience = st.selectbox("Sélectionnez le type d'audience pour l'analyse juridique:", options=["Tout Public", "Professionnel"])
    detail = st.selectbox("Sélectionnez le niveau de détail :", options= ["Succinct", "Détaillé"])

# Activation brique Europeenne 

ue_data = st.radio("Souhaitez vous enrichir les résultats avec les textes européens ayant servis à la transposition ?  ", ("Non", "Oui"))


# Bouton exécution

if st.button("Lancer le tracker"):
    try:
        access_token_prod = get_token_prod()

        st.success("Étape 0 - Récupération du token réussie")
    except Exception as e:
        st.error(f"Erreur lors de la récupération du token : {e}")

    # Test Ping Pong
    
    try:
        if ping_pong_test_prod() == 'pong':
            st.success("Test Ping Pong : connexion réussie")
        else:
            st.error("Test Ping Pong : échec de connexion")
            st.stop()
    except Exception as e:
        st.error(f"Erreur lors du test Ping Pong : {e}")

    # Récupération des données
    try:
        json_output = get_text_modif_byDateslot_textCid_extract_content_prod(
            access_token_prod, textCid, annee_debut, annee_fin
        )
        st.success("Étape 1 - Requête API LégiFrance effectuée avec succès")
    
    except Exception as e:
        st.error(f"Étape 1 - Échec : {e}")
    
    try:
        # Formatage  données
        panda_output = transform_json_to_dataframe(json_output)
        
        # DataFrame Cleaning & prepare
        panda_output.drop(['Version du',
                           'Année',
                           'Est la dernière version',
                           'Nature Article Modificateur',
                           'ID Parent', 'Nom Parent',
                           'Date de fin (Article Cible)',
                           'Date de début cible Article Modificateur',
                           'CID Parent'
                           ], axis=1, inplace = True)
        panda_output.rename(columns={"Date de début cible d'entrée en vigueur": "Date de début cible",
                                     "Action Article Modificateur":"Action" }, inplace= True)
        panda_output.reset_index(drop=True, inplace=True)
        st.success(f"Étape 2 - Formatage des données réussi : {len(panda_output)} lignes créées")
    
    except Exception as e:
        st.error(f"Étape 2 - Échec : {e}")
        
        
    #  Filtrage par N° de décret / ordonnance / loi

    try:
        if numero_1 :
            panda_output = panda_output[panda_output["Titre Article Modificateur"].astype(str).str.contains(numero_1, na=False, case=False)]
            st.success(f"Filtrage appliqué : {len(panda_output)} lignes gardées")
        else:
            st.success(" Aucun filtrage appliqué, toutes les données sont affichées.")

    except Exception as e:
        st.error(f"Erreur lors du filtrage : {e}")

    # Ajout l'ancien contenu
    
    try:
        ajout_col_AV_prod(panda_output)
        st.success("Étape 4 - Ajout de l'ancienne version des articles réussi")
    
    except Exception as e:
        st.error(f"Étape 4 - Échec : {e}")

    # Ajout nouveau contenu
    
    try:
        ajout_col_coutenu_NV_prod(panda_output)
        st.success("Étape 5 - Ajout de la nouvelle version des articles réussi")
    
    except Exception as e:
        st.error(f"Étape 5 - Échec : {e}")

    # Ajout colonne comparative
    
    try:
        compare_AV_vs_NV(panda_output)
        st.success("Étape 6 - Ajout de la colonne de comparaison réussi")
    
    except Exception as e:
        st.error(f"Étape 6 - Échec : {e}")
    
    
    ## Add Celex     
    if ue_data == "Oui":    
    # Step 1: extraction de l'ID du dossier legistif 
        try:
            panda_output['ID DossLegis'] = panda_output.apply( lambda x: get_doss_legi_id_prod(x["ID Article Modificateur"], 
                                x["Date de début cible"]), axis=1)
            st.success("Ajout données UE - Étape 1: réussie")
        except Exception as e:
            st.error(f"Ajout données UE - Étape 1: Échec : {e}")

        # Step 2: extraction de la liste des directives et autres 
        try: 
            panda_output['Liste directives'] = panda_output.apply(
        lambda row: get_directives_list_vprod(row['ID DossLegis'] ),axis=1)
            st.success("Ajout données UE - Étape 2: réussie")
        
        except Exception as e:
            st.error(f"Ajout données UE - Étape 2: Échec : {e}")

        # Step 3: selection unique des ID des directives 
        try:
            panda_output['ID directives'] = panda_output.apply(
        lambda row: get_directive_id_v2(row['Liste directives'] ),axis=1)
            st.success("Ajout données UE - Étape 3: réussie")
            
        except Exception as e:
            st.error(f"Ajout données UE - Étape 3: Échec : {e}")
        
        # Step 4: explode col des directives

        def explode_directives(df, column_name):
            df["ID directive 1"] = df[column_name].apply(lambda x: x[0] if len(x) > 0 else None)
            df["ID directive 2"] = df[column_name].apply(lambda x: x[1] if len(x) > 1 else None)  
            return df
        
        try:
            panda_output = explode_directives(panda_output, 'ID directives' )
            st.success("Ajout données UE - Étape 4: réussie")
            
        except Exception as e:
            st.error(f"Ajout données UE - Étape 4: Échec : {e}")
            
        # Step 5: get Celex
        
        try:
            panda_output['Celex 1'] = panda_output.apply(lambda row: get_celex_v2(row['ID directive 1']), axis=1)
            panda_output['Celex link 1'] = panda_output.apply(lambda row: 'http://publications.europa.eu/resource/celex/'+ str(row['Celex 1']), axis =1)

            panda_output['Celex 2'] = panda_output.apply(lambda row: get_celex_v2(row['ID directive 2']), axis=1)
            panda_output['Celex link 2'] = panda_output.apply(lambda row: 'http://publications.europa.eu/resource/celex/'+ str(row['Celex 2']), axis =1)
        
            st.success("Ajout données UE - Étape 5: réussie")
            
        except Exception as e:
            st.error(f"Ajout données UE - Étape 5: Échec : {e}") 


        # Step 6: cleaning dataframe
        
        try:
            panda_output.drop(['ID DossLegis', 'Liste directives', 'ID directives',
                            'ID directive 1' ,'ID directive 2'] ,axis =1,
                            inplace= True)
            st.success("Ajout données UE - Étape 6: réussie")
            
        except Exception as e:
            st.error(f"Ajout données UE - Étape 6: Échec : {e}")      
    
    else: st.success("Absence d'ajout de données UE pour la transposition (choix utilisateur)") 
    
    # LLM analysis /com
    
    try:
        if active_llm == "Oui":
            st.success(f"Étape 7 - Lancement de l'analyse des textes juridiques par le LLM ({llm_limit} premiers changements) ")
            
            # Applying LLM function:
            panda_output = llm_apply_row(panda_output.iloc[0:llm_limit,:])
            
            # Concate all LLM commentaries 
            text_variable = panda_output['LLM_Change_Analysis_1'].str.cat()
            
            # WapUp LLM analysis 
            summary = wrap_up_multi(text_variable, audience, detail)
            
            st.success("Étape 7 - Analyse juridique réussie")
            st.write(f""" {summary}""")
        else:  
            st.success("Absence de comparaison (choix utilisateur)")
        
    except Exception as e:
        st.error(f"Étape 7 - Échec : {e}")


    # Export en mémoire et téléchargement
    try:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            panda_output.to_excel(writer, index=False, sheet_name='Données')
        st.success("Étape 8 - Fichier Excel préparé pour téléchargement")

        st.write(f"Aperçu du tableau des modifications du {selected_code} de {annee_debut} a/au {annee_fin}")
        
        st.dataframe(panda_output.head(15))

        st.download_button(
            label="Télécharger le fichier Excel",
            data=buffer.getvalue(),
            file_name="DB_Legifrance.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"Étape 8 - Échec : {e}")