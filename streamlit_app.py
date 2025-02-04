import streamlit as st
import pandas as pd
import io
import os
from dotenv import load_dotenv
from langchain_community.callbacks.manager import get_openai_callback


load_dotenv()


# Import fonctions
from modules_simili.LegiFR_call_funct import *
from modules_simili.LegiFR_call_prod_funct import *
from modules_simili.dataprep_funct import *
from modules_llm.LLM_Analytic_changes import *
from modules_simili.get_token import *



# Titre centré et stylisé
st.markdown(
    """
    <h1 style='text-align: center; color: navy;'>S i m i l i</h1>
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

# Étape 2 : Intervalle d'années
annee_debut = st.text_input("Entrez la date de début (année ou format JJ-MM-AAAA) :", value="2020")
annee_fin = st.text_input("Entrez la date de fin (année ou format JJ-MM-AAAA) :", value="2021")

# Filtrage sur N° de décret / ordonnance / loi
filtrer_numero = st.radio("Voulez-vous filtrer sur un N° de décret / ordonnance / loi ?", ("Non", "Oui"))

numero_1, numero_2 = None, None
if filtrer_numero == "Oui":
    numero_1 = st.text_input("Entrez le premier numéro de décret / ordonnance / loi :", value="n°2020-115")
    numero_2 = st.text_input("Entrez le deuxième numéro de décret / ordonnance / loi :", value="n°2020-1544")

# Activation brique LLM
Active_LLM = st.radio("Voulez vous avoir une analyse des changements de chaque article suivi d'un résumé des 10 premiers changements ?  ", ("Non", "Oui"))

if Active_LLM == "Oui":
    audience = st.selectbox("Sélectionnez le type d'audience pour l'analyse juridique:", options=["Tout Public", "Professionnel"])
    detail = st.selectbox("Sélectionnez le niveau de détail :", options= ["Succinct", "Détaillé"])

# Bouton exécution
if st.button("Lancer simili"):
    try:
        #access_token = get_token() sandbox API call functions
        access_token_prod = get_token_prod()

        st.success("Étape 0 - Récupération du token réussie")
    except Exception as e:
        st.error(f"Erreur lors de la récupération du token : {e}")

    # Test Ping Pong
    try:
        if ping_pong_test(access_token) == 'pong':
            st.success("Test Ping Pong : connexion réussie")
        else:
            st.error("Test Ping Pong : échec de connexion")
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

    # Formatage  données
    try:
        panda_output = transform_json_to_dataframe(json_output)
        panda_output = panda_output.drop('Est la dernière version', axis=1)
        panda_output.reset_index(drop=True, inplace=True)
        st.success(f"Étape 2 - Formatage des données réussi : {len(panda_output)} lignes créées")
    except Exception as e:
        st.error(f"Étape 2 - Échec : {e}")
        
    #  Filtrage par N° de décret / ordonnance / loi
    try:
        if filtrer_numero == "Oui":
            panda_output = panda_output[
                panda_output["Titre Article Modificateur"].astype(str).str.contains( numero_1, na=False, case=False ) |
                panda_output["Titre Article Modificateur"].astype(str).str.contains( numero_2, na=False, case=False )
            ]
            st.success(f"Étape 3 - Filtrage appliqué : {len(panda_output)} lignes gardées")
        else:
            st.success("Étape 3 - Aucun filtrage sur les numéros appliqué")
    except Exception as e:
        st.error(f"Étape 3 - Erreur lors du filtrage : {e}")
        
    # Ajout l'ancien contenu
    try:
        ajout_col_AV_prod(panda_output)
        st.success("Étape 4 - Ajout de l'ancienne version des articles réussi")
    except Exception as e:
        st.error(f"Étape 4 - Échec : {e}")

    # Ajout nouveau contenu
    try:
        ajout_col_coutenu_NV_prod(panda_output)
        st.success("Étape 5 - Ajout de l'ancienne version des articles réussi")
    except Exception as e:
        st.error(f"Étape 5 - Échec : {e}")

    # Ajout colonne comparative
    try:
        compare_AV_vs_NV(panda_output)
        st.success("Étape 6 - Ajout de la colonne de comparaison réussi")
    except Exception as e:
        st.error(f"Étape 6 - Échec : {e}")
        
    # LLM 
    try:
        if Active_LLM == "Oui":
            st.success("Étape 7 - Lancement de l'analyse des textes juridiques par le LLM (10 premiers changements) ")
            panda_output = llm_apply_row(panda_output.iloc[0:10,:])
            text_variable = panda_output['LLM_Change_Analysis_1'].str.cat()
            summary = wrap_up_multi(text_variable, audience, detail)
            st.success("Étape 7 - Analyse juridique réussie")
            st.write(f""" {summary}""")
        else :  
            st.success("Étape 7 - Absence de comparaison")
        
    except Exception as e:
        st.error(f"Étape 7 - Échec : {e}")

    # Export en mémoire et téléchargement
    try:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            panda_output.to_excel(writer, index=False, sheet_name='Données')
        st.success("Étape 8 - Fichier Excel préparé pour téléchargement")

        #st.write("Aperçu du résumé :")
        #st.text(f"{text_file}")
        st.write(f"Aperçu du tableau des modifications du {selected_code} de {annee_debut} a/au {annee_fin}")
        st.dataframe(panda_output.head(10))
        

        st.download_button(
            label="Télécharger le fichier Excel",
            data=buffer.getvalue(),
            file_name="DB_Legifrance.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"Étape 8 - Échec : {e}")