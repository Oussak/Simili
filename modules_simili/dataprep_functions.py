
# Data pipeline 1: Convertit un timestamp en millisecondes

from datetime import datetime, timezone

def convert_timestamp(timestamp):
    dt_aware = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
    return dt_aware.strftime('%Y-%m-%d')

# Data pipeline 2: json To pandas DataFrame

import pandas as pd
def transform_json_to_dataframe(data):
    """
    Transforme le JSON en DataFrame structuré avec les colonnes demandées.
    """
    rows = []

    for regroupement in data["regroupements"]:
        year = regroupement["title"]
        for version, version_data in regroupement["versions"].items():
            date_debut_version = convert_timestamp(version_data.get("dateDebut"))
            is_last_version = version_data.get("isEndVersion", False)
            articles_modificateurs = version_data.get("articlesModificateurs", {})

            for article_id, article_data in articles_modificateurs.items():
                title_article = article_data.get("title")
                nature_article = article_data.get("nature")
                date_debut_cible_article = convert_timestamp(article_data.get("dateDebutCible"))
                actions = article_data.get("actions", {})

                for action_type, action_data in actions.items():
                    parents = action_data.get("parents", {})
                    for parent_id, parent_data in parents.items():
                        parent_name = parent_data.get("name")
                        parent_cid = parent_data.get("cid")
                        articles_cibles = parent_data.get("articlesCibles", {})

                        for article_cible_id, article_cible_data in articles_cibles.items():
                            article_cible_name = article_cible_data.get("name")
                            article_cible_date_debut = convert_timestamp(article_cible_data.get("dateDebut"))
                            article_cible_date_fin = convert_timestamp(article_cible_data.get("dateFin"))

                            # Ajouter une ligne au tableau
                            rows.append({
                                "Année": year,
                                "Version du": version,
                                "Date de début cible d'entrée en vigueur": date_debut_version,
                                "Est la dernière version": is_last_version,
                                "ID Article Modificateur": article_id,
                                "Titre Article Modificateur": title_article,
                                "Nature Article Modificateur": nature_article,
                                "Date de début cible Article Modificateur": date_debut_cible_article,
                                "Action Article Modificateur": action_type,
                                "ID Parent": parent_id,
                                "Nom Parent": parent_name,
                                "CID Parent": parent_cid,
                                "ID Article Cible": article_cible_id,
                                "Titre Article Cible": article_cible_name,
                                "Date de début (Article Cible)": article_cible_date_debut,
                                "Date de fin (Article Cible)": article_cible_date_fin
                            })

    return pd.DataFrame(rows)


# Data pipeline 3: add new column correspond to the content of the new version of the article 
def add_column_with_articles_new_content(df):
    """
    Ajoute une colonne "Contenu_Nouv_Vers_Article" à un DataFrame en appliquant une fonction à une autre colonne.
    """
    df['Contenu_Nouv_Vers_Article'] = df.apply(
        lambda x: getArticle(x['ID Article Cible']), axis=1)
    return df

# Data pipeline 4: add new column correspond to the content of the old version of the article 
def add_column_with_articles_new_content(df):
    """
    Ajoute une colonne "Contenu_Ancien_Article" à un DataFrame en appliquant une fonction à l ID artcile.
    """
    df['Contenu_Ancien_Article'] = df.apply(
        lambda x: getArticle_prev_vers(x['ID Article Cible']), axis=1)
    return df 

# Data pipline 5 : 
