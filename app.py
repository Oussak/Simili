import streamlit as st
import pandas as pd
import io

# Import de vos fonctions et variables
from modules_simili.get_token import get_token
from credentials import client_id, client_secret
from modules_simili.LegiFR_call_funct import *
from modules_simili.dataprep_funct import *


def main():
    st.title("Simili")

    st.write(
        """
        Module 1: récupération et de transformation des données depuis LégiFrance.
        """
    )

    # Zone pour saisir le Cid et l'intervalle d'années
    textCid = st.text_input(
        "Entrez le Cid du texte (exemple : 'LEGITEXT000006072026' pour le Code monétaire et financier) :",
        value="LEGITEXT000006072026"
    )
    annee_debut = st.text_input("Entrez date de début (année ou date foramt JJ-MM-AAAA) :", value="2020")
    annee_fin = st.text_input("Entrez date de fin (année ou date foramt JJ-MM-AAAA):", value="2021")

    # Bouton d'exécution
    if st.button("Lancer le processus"):
        # 1) Récupération du token
        try:
            access_token = get_token()
            st.success("Étape 0 - Récupération du token réussie")
        except Exception as e:
            st.error(f"Erreur lors de la récupération du token : {e}")
            return  # on arrête l'exécution si échec

        # 2) Test de connexion Ping Pong
        try:
            if ping_pong_test(access_token) == 'pong':
                st.success("Test Ping Pong : connexion réussie")
            else:
                st.error("Test Ping Pong : échec de connexion")
                return
        except Exception as e:
            st.error(f"Erreur lors du test Ping Pong : {e}")
            return

        # 3) Récupération des données
        try:
            json_output = get_text_modif_byDateslot_textCid_extract_content(
                access_token, textCid, annee_debut, annee_fin
            )
            st.success("Étape 1 - Requête API LégiFrance effectuée avec succès")
        except Exception as e:
            st.error(f"Étape 1 - Échec : {e}")
            return

        # 4) Formatage des données
        try:
            panda_output = transform_json_to_dataframe(json_output)
            st.success("Étape 2 - Formatage des données réussi")
        except Exception as e:
            st.error(f"Étape 2 - Échec : {e}")
            return

        # 5) Ajout de l'ancien contenu
        try:
            ajout_col_AV(panda_output)
            st.success("Étape 3 - Ajout de l'ancien contenu (AV) réussi")
        except Exception as e:
            st.error(f"Étape 3 - Échec : {e}")
            return

        # 6) Ajout du nouveau contenu
        try:
            ajout_col_coutenu_NV(panda_output)
            st.success("Étape 4 - Ajout du nouveau contenu (NV) réussi")
        except Exception as e:
            st.error(f"Étape 4 - Échec : {e}")
            return

        # 7) Ajout de la colonne comparative
        try:
            compare_AV_vs_NV(panda_output)
            st.success("Étape 5 - Ajout de la colonne de comparaison réussi")
        except Exception as e:
            st.error(f"Étape 5 - Échec : {e}")
            return

        # 8) Export en mémoire et bouton de téléchargement
        try:
            # On convertit la base pandas_output en Excel dans un buffer
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                panda_output.to_excel(writer, index=False, sheet_name='Données')
            st.success("Étape 6 - Fichier Excel préparé pour téléchargement")

            st.write("Aperçu des données :")
            st.dataframe(panda_output.head(10))  # On montre les 10 premières lignes

            st.download_button(
                label="Télécharger le fichier Excel",
                data=buffer.getvalue(),
                file_name="DB_Legifrance.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Étape 6 - Échec : {e}")
            return


if __name__ == "__main__":
    main()
