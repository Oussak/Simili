import getpass
import os
import tiktoken
import sys
import pandas as pd 
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
load_dotenv()


# LLM definition co
llm = AzureChatOpenAI(
    azure_endpoint= os.getenv("Azure_OpenAI_OB_Endpoint") ,
    openai_api_version="2024-02-15-preview",
    model_name="gpt-4o",
    openai_api_key= os.getenv("Azure_OpenAI_OB_Key"),
    openai_api_type="azure",
    temperature=0,
    deployment_name="gpt-4o-deploy",
    #streaming=True,
)

#Token counter: 
def count_tokens(text, model="gpt-4o"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text) # texte to tokens
    return len(tokens)

# Function to get legal comment from the LLM about the change in each article:   
def llm_legal_change_com_v1(old_version, new_version): 
    prompt = ChatPromptTemplate.from_messages([("system",
            """
            Tu es un avocat et analyste juridique très expérimenté, tu as pour but d'analyser et de commenter les changements 
            réglementaires de chaque article , tu trouveras ici l'ancienne et la nouvelle version de l'article que l on te donne. 
            Tu adopteras un language juridique précis. Tu n'inventeras rien et tu te baseras uniquement sur les données fournies.
            Si tu ne sais pas ou tu ne comprends pas , dis le. 
            Inutile de reciter les textes fournis, tu ne retourneras que ton analyse.
            """),
        ("human", 
            "Voici l'ancienne version de l'article a analyser {old_version} et voici la nouvelle version du meme article {new_version}")])
    
    chain = prompt | llm | StrOutputParser()
    
    llm_output = chain.invoke({
        "old_version": old_version,
        "new_version": new_version})
    
    return llm_output

# Function to get legal comment from the LLM about the change in each article:  
## Inhencing the prompt  
def llm_legal_change_com_v2(old_version, new_version): 
    prompt = ChatPromptTemplate.from_messages([("system",                                  
        """
	Tu es un avocat et analyste juridique très expérimenté. 
    Ta mission consiste à examiner et commenter les évolutions réglementaires d’un article de loi en comparant sa version 
    antérieure avec sa version révisée.

	Consignes :
	1.	Utilise un langage juridique précis.
	2.	Base-toi uniquement sur les informations fournies, sans inventer ni extrapoler.
	3.	Si tu ne comprends pas un point ou si les informations sont insuffisantes, signale-le clairement.
	4.	Ne récite pas le texte en intégralité : concentre-toi sur l’analyse et la comparaison.
    5.  Inclu les références de textes réglementaires. 

	Contenu à analyser :
	•	Ancienne version : {old_version}
	•	Nouvelle version : {new_version}

	Objectif :
    Produis un commentaire juridique concis, en mettant en évidence les principaux changements, leur portée et leurs éventuelles conséquences. N’inclus dans ta réponse que l’analyse finale.

            """)])
    
    chain = prompt | llm | StrOutputParser()
    
    llm_output = chain.invoke({
        "old_version": old_version,
        "new_version": new_version})
    
    return llm_output


# Function to get legal comment from the LLM about the change in each article:  
## Inhencing the prompt  
def llm_legal_change_com_v3(old_version, new_version): 
    prompt = ChatPromptTemplate.from_messages([("system",                                  
        """
	Tu es un avocat et analyste juridique très expérimenté. 
    Ta mission consiste à examiner et commenter les évolutions réglementaires d’un article de loi en comparant sa version 
    antérieure avec sa version révisée.

	Consignes :
	1.	Utilise un langage juridique précis.
	2.	Base-toi uniquement sur les informations fournies, sans inventer ni extrapoler.
	3.	Si tu ne comprends pas un point ou si les informations sont insuffisantes, signale-le clairement.
	4.	Ne récite pas le texte en intégralité : concentre-toi sur l’analyse et la comparaison.
    5.  Inclu les références de textes réglementaires. 

	Contenu à analyser :
	•	Ancienne version : {old_version}
	•	Nouvelle version : {new_version}

	Objectif :
    Produis un commentaire juridique concis, en mettant en évidence les principaux changements, leur portée et leurs éventuelles conséquences. N’inclus dans ta réponse que l’analyse finale.
            """)])
    
    chain = prompt | llm | StrOutputParser()
    
    llm_output = chain.invoke({
        "old_version": old_version,
        "new_version": new_version})
    
    return llm_output

#importing a file : 
def import_xlsx_to_pandas(path :str): #"/Users/oussa/Desktop/Github_perso/Legal_FR_Tracker/data_output/Legifrance_DB_TrackChange.xlsx"
    imported_DB= pd.read_excel(path)
    return imported_DB

#Filter on Titre Article Modificateur - pd
def filter_titre_art_modificat_pd(pd_db_file, terme_filtre_1 :str, terme_filtre_2:str ): 
    #"/Users/oussa/Desktop/Github_perso/Legal_FR_Tracker/data_output/Legifrance_DB_TrackChange.xlsx"
    pd_db_file =  pd_db_file[pd_db_file['Titre Article Modificateur'].str.contains(terme_filtre_1)| pd_db_file['Titre Article Modificateur'].str.contains(terme_filtre_2) ]
    return pd_db_file

#Filter on Titre Article Modificateur - Excel
def filter_titre_art_modificat_xl(xl_file, terme_filtre_1 :str, terme_filtre_2:str ): 
    #"/Users/oussa/Desktop/Github_perso/Legal_FR_Tracker/data_output/Legifrance_DB_TrackChange.xlsx"
    pd_db_file = pd.DataFrame(xl_file)
    pd_db_file =  pd_db_file[pd_db_file['Titre Article Modificateur'].str.contains(terme_filtre_1)| pd_db_file['Titre Article Modificateur'].str.contains(terme_filtre_2) ]
    return pd_db_file

# Applying LLM on each row :
def llm_apply_row(pd_db_file):
    pd_db_file['LLM_Change_Analysis_1'] = pd_db_file.apply(
    lambda row: llm_legal_change_com_v1(row['Contenu_Ancien_Article'], row['Contenu_Nouv_Vers_Article']), 
    axis=1)
    return pd_db_file


# Amélioration prompt avec o1 + intération
def wrap_up_multi(text_to_summarize, audience: str, detail_level:str): 
    # audience: “professionnel” ou “tout public”
    # detail_level: “succinct” ou “détaillé”
    prompt = ChatPromptTemplate.from_messages([("system",                                  
        """
		Prompt amélioré avec niveaux de détail et public cible :
  
		Tu es un avocat et analyste juridique très expérimenté.
		Ta mission consiste à produire un résumé global des analyses réalisées sur les évolutions réglementaires de plusieurs articles de 
  		loi en comparant leurs versions antérieures et révisées.

	Consignes générales :
	1.	Utilise un langage juridique précis et adapté au public cible défini par la variable {audience} :
	•	Si {audience} est “professionnel”, adopte un ton technique et détaillé.
	•	Si {audience} est “tout public”, simplifie les termes juridiques pour les rendre accessibles tout en conservant leur précision.
 
	2.	Ajuste la longueur et le niveau de détail du résumé en fonction de la variable {detail_level} :
	•	Si {detail_level} est “succinct”, concentre-toi uniquement sur les points clés et les impacts majeurs.
	•	Si {detail_level} est “détaillé”, développe davantage les analyses, en incluant des exemples ou des explications supplémentaires lorsque pertinent.
 
	3.	Regroupe et hiérarchise les informations :
	•	Identifie les thématiques ou tendances communes (par exemple : renforcement des obligations, simplification de procédures, etc.).
	•	Mets en évidence les changements les plus significatifs et leur impact global.
	4.	Si certaines analyses révèlent des ambiguïtés ou des manques d’informations, mentionne-les brièvement.
    5.  Inclu les références de textes réglementaires. 


	Variables :
	•	Niveau de détail : {detail_level} (valeurs possibles : “succinct” ou “détaillé”)
	•	Public cible : {audience} (valeurs possibles : “professionnel” ou “tout public”)

	Objectif :
		Fournis un résumé synthétique ou détaillé, selon le niveau demandé, mettant en lumière les évolutions majeures, 
  		les implications globales, et les tendances observées à travers les différents articles. Structure ta réponse de manière organisée 
    	(par exemple : par thématique ou par impact).
    
    Voici le text  : {text_to_summarize}
            """)])
    
    chain = prompt | llm | StrOutputParser()
    
    llm_output = chain.invoke({
        "text_to_summarize": text_to_summarize,
        "audience": audience,
        "detail_level": detail_level})
    
    return llm_output