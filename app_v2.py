import streamlit as st
import pandas as pd
import io

# ----- Import des modules nécessaires -----
from modules_simili.get_token import get_token, get_token_prod
from modules_simili.LegiFR_call_funct import *
from modules_simili.dataprep_funct import *
from modules_simili.Junction_funct import *

# Liste des textes juridiques et leurs CID correspondants
CODES = {
    "Code de commerce": "LEGITEXT000005634379",
    "Code des assurances": "LEGITEXT000006073984",
    "Code monétaire et financier": "LEGITEXT000006072026",
    "Code pénal": "LEGITEXT000006070719",
    "Code de la consommation": "LEGITEXT000006069565",
    "Code de la sécurité sociale": "LEGITEXT000006073189",
    "Code de procédure civile": "LEGITEXT000006070716",
    "Code de procédure pénale": "LEGITEXT000006071154",
    "Code de l'environnement": "LEGITEXT000006074220",
    "Code général des impôts": "LEGITEXT000006069574"
}

# Module 1 : Récupération et transformation depuis LégiFrance

def run_legifrance_module():
    st.header("Module 1 : Récupération et transformation depuis LégiFrance")

    st.write("""
        Cette partie permet de :
        1. Récupérer un token et tester la connexion à l'API.
        2. Extraire les modifications législatives d'un texte juridique.
        3. Transformer les données et ajouter des colonnes comparatives.
        4. Exporter les résultats au format Excel.
    """)

    # Liste déroulante pour sélectionner le texte juridique
    selected_code = st.selectbox(
        "Sélectionnez une source :",
        options=list(CODES.keys())
    )
    textCid = CODES[selected_code]

    # Entrée pour l'année de début et l'année de fin
    annee_debut = st.text_input("Année de début :", value="2020")
    annee_fin = st.text_input("Année de fin :", value="2021")

    # Bouton pour exécuter le module
    if st.button("Exécuter le module LégiFrance"):
        try:
            # Étape 1 : Récupération du token
            access_token = get_token()
            st.success("Token récupéré avec succès.")

            # Étape 2 : Test ping pong
            if ping_pong_test(access_token) == "pong":
                st.success("Connexion à l'API réussie.")
            else:
                st.error("Échec de la connexion à l'API.")
                return

            # Étape 3 : Récupération des données
            json_output = get_text_modif_byDateslot_textCid_extract_content(
                access_token, textCid, annee_debut, annee_fin
            )
            st.success("Données récupérées avec succès.")

            # Étape 4 : Transformation des données
            panda_output = transform_json_to_dataframe(json_output)
            ajout_col_AV(panda_output)
            ajout_col_coutenu_NV(panda_output)
            compare_AV_vs_NV(panda_output)
            st.success("Données transformées avec succès.")

            # Étape 5 : Exportation des résultats
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                panda_output.to_excel(writer, index=False, sheet_name="LegiFrance")
            st.success("Fichier Excel prêt au téléchargement.")

            # Affichage et téléchargement
            st.dataframe(panda_output.head(10))
            st.download_button(
                label="Télécharger le fichier Excel",
                data=buffer.getvalue(),
                file_name="Legifrance_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")

# Module 2 : Construction de la base 'Junction_DB'

def run_junction_module():
    st.header("Module 2 : Junction avec EUR-LEX")

    st.write("""
        Cette partie permet de :
        1. Importer une base de données LégiFrance.
        2. Filtrer et enrichir les données avec des informations supplémentaires (dossiers législatifs, directives, etc.).
        3. Exporter les résultats au format Excel.
    """)

    uploaded_file = st.file_uploader(
        "Chargez un fichier Excel (output de LégiFrance) :", type=["xlsx"]
    )

    if uploaded_file is not None and st.button("Exécuter le module Junction_DB"):
        try:
            database_FR = pd.read_excel(uploaded_file)

            # Étapes de traitement (filtrage, enrichissement, etc.)
            Junction_DB = database_FR[
                database_FR["Titre Article Modificateur"].str.startswith("Ordonnance", na=False)
            ].drop_duplicates(subset=["ID Article Modificateur"])

            st.success("Base de données filtrée avec succès.")

            # Exemple : ajout d'une colonne fictive pour démonstration
            Junction_DB["Exemple Colonne"] = "Valeur ajoutée"
            
            # Export Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                Junction_DB.to_excel(writer, index=False, sheet_name="Junction_DB")
            st.success("Fichier Excel prêt au téléchargement.")

            # Affichage et téléchargement
            st.dataframe(Junction_DB.head(10))
            st.download_button(
                label="Télécharger Junction_DB.xlsx",
                data=buffer.getvalue(),
                file_name="Junction_DB.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")

# Exécution de l'application Streamlit
st.title("Simili (Beta)")

choix = st.sidebar.radio(
    "Sélectionnez le module à exécuter :",
    ["Module LégiFrance", "Module pour jonction FR-UE"]
)

if choix == "Module LégiFrance":
    run_legifrance_module()
else:
    run_junction_module()