import re
import time
import requests
import json
import os
import ssl
import xml.etree.ElementTree as ET
from glob import glob
from datetime import datetime
from datetime import date
from bs4 import BeautifulSoup
from requests.utils import quote
from openai import AzureOpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
LOGIN_EURLEX = os.getenv("client_id_legifrance")
MOT_DE_PASSE_EURLEX = os.getenv("client_secret_legifrance")

def get_value_if_cellar(root):
    """
    Trouve une Url cellar dans un element xml URI
    :param root: elem xmltree URI
    :return: la valeur du champs value si l'url est de type cellar, "" sinon
    """
    dico = {}
    for elem in root:
        dico[elem.tag] = elem.text
    try:
        if dico['{http://eur-lex.europa.eu/search}TYPE'] == 'cellar':
            return dico['{http://eur-lex.europa.eu/search}VALUE']
        else:
            return ""
    except Exception as e:
        return ""


def get_date(root):
    """
    Trouve une date dans le xml et la convertit au format date yyyy-mm-dd
    :param root: elem xmltree contenant la date à convertir
    :return: la date sous le bon format
    """
    for elem in root:
        if elem.tag == '{http://eur-lex.europa.eu/search}VALUE':
            date_doc = datetime.strptime(elem.text, '%Y-%m-%d').date()
            return date_doc


def getinfos(root, dico, ans):
    """
    Parcourt récusrivement un xml pour trouver les c et les WORK_DATE_DOCUMENT de l'xml retourné par le web service
    :param root: elem xmltree contenant les informations du ne=oeud actif du xml
    :param dico: dictionnaire contenant les couples WORK_DATE_DOCUMENT:URI
    :param ans: Dernière URI trouvée (pour l'associer à la prochaine date que l'on trouve
    :return: dict et ans
    """
    if not list(root):
        return dico, ans
    else:
        if root.tag == '{http://eur-lex.europa.eu/search}URI':
            ans = get_value_if_cellar(root)
        elif root.tag == '{http://eur-lex.europa.eu/search}WORK_DATE_DOCUMENT':
            try:
                dico[get_date(root)] = ans
            except Exception as e:
                pass
        else:
            for elem in root:
                dico, ans = getinfos(elem, dico, ans)
    return dico, ans


def get_url_api_from_xmlstring(xmlstring):
    """
    Cherche et retourne l'url cellar correspondant a la date la plus récente d'un fichier xml envoyé par le webservice
    :param xmlstring: le xml en format str
    :return: l'url cellar pour l'appel à l'api
    """
    tree = ET.ElementTree(ET.fromstring(xmlstring))
    root = tree.getroot()
    dico, ans = getinfos(root, {}, "")
    for elem in sorted(dico.keys(), reverse=True):
        if dico[elem]:
            return dico[elem]


def check_if_error(xmlstring):
    """
    Vérifie si le fichier xml envoyé par le webservice est un message d'erreur
    :param xmlstring: le xml en format str
    :return: "" s'il n'y a pas d'erreur, le message d'erreur sinon
    """
    tree = ET.ElementTree(ET.fromstring(xmlstring))
    root = tree.getroot()
    tags = [i.tag for i in root.iter()]
    if '{http://www.w3.org/2003/05/soap-envelope}Fault' in tags:
        for elem in root.iter('{http://www.w3.org/2003/05/soap-envelope}Reason'):
            text = elem.find('{http://www.w3.org/2003/05/soap-envelope}Text').text
            return text
    else:
        return ""


def get_celex_id(url):
    """
    Obtient l'id celex a partir d'une url eurlex
    :param url: url d'où extraire le celex
    :return: l'id celex
    """
    celex_id = url.split("/")[7].replace('%', ':').split(':')[1].split('&')[0].split('-')[0]
    celex_id = celex_id.split('(')[0] + '*' if '(' in celex_id else celex_id
    return celex_id


def get_url_cellar(celex_id):
    """
    obtient deux json pour un celex donné, un résultat en Anglais un résultat en Français
    :param celex_id: id_celex pour l'appel au web service
    :return: une liste contenant deux json avec l'url cellar, l'html donné par l'api et le langage de la réponse
    """
    url_web_service = "https://eur-lex.europa.eu/EURLexWebService?wsdl"


    # headers
    headers = {'Content-Type': 'application/soap+xml; charset=utf-8'}
    ssl._create_default_https_context = ssl._create_unverified_context

    body = f"""
            <soap:Envelope xmlns:sear="http://eur-lex.europa.eu/search"
            xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
            <soap:Header>
            <wsse:Security soap:mustUnderstand="1" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
            <wsse:UsernameToken wsu:Id="UsernameToken-3" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
            <wsse:Username>{LOGIN_EURLEX}</wsse:Username>
            <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{MOT_DE_PASSE_EURLEX}</wsse:Password>
            </wsse:UsernameToken>
            </wsse:Security>
            </soap:Header>
            <soap:Body>
            <sear:searchRequest>
            <sear:expertQuery>SELECT CELLAR_ID
                                WHERE DN ~ {celex_id}
                </sear:expertQuery>
                <sear:page>1</sear:page>
            <sear:pageSize>2</sear:pageSize>
            <sear:searchLanguage>fr</sear:searchLanguage>
            </sear:searchRequest>
            </soap:Body>
            </soap:Envelope>
            """

    response = requests.post(url_web_service, data=body, headers=headers, verify=False)

    erreur = check_if_error(response.text)
    if erreur == 'Service temporarily not available':
        time.sleep(1)
        response = requests.post(url_web_service, data=body, headers=headers, verify=False)

    return get_url_api_from_xmlstring(response.text)


def get_api_result(url_api):
    """
    Obtient deux json pour une adresse cellar donnée,un résultat en Anglais un résultat en Français
    :param url_api: url cellar pour l'appel API
    :return:une liste de dictionnaires conenant l'url, le contenu et la langue des résultats
    """

    

    api_result = []
    for lang in ['fra']:
        headers_api = {'Accept': 'application/xhtml+xml;',
                       'Accept-Language': lang}

        response_api = requests.get(url_api, headers=headers_api, verify=False)

        api_result.append({'url': response_api.url, 'content': response_api.text, 'lang': lang})
    return api_result


def get_doc_name(soup):
    """
    Obtient le nom du document à partir d'un html
    :param soup: Beautiful soup du html traité
    :return: le nom recomposé du document
    """
    text_names = soup.find_all(True, {'class': ["title-doc-first", "doc-ti", "oj-doc-ti"]})
    name_list = [str(i.text) for i in text_names[:3]]
    text_name = ' '.join(name_list)
    text_name = text_name.replace('\n', '').replace(u"\u00a0", " ")
    text_name = text_name.split(re.findall('\d+',text_name)[0],1)[1] if '\u25ba' in text_name else text_name
    return text_name.strip().capitalize()


def get_content_from_html(soup):
    """
    Obtient le texte d'un html
    :param soup: Beautiful soup du html traité
    :return: le texte
    """
    for match in soup.findAll("span"):
        match.unwrap()
    tags = soup.find_all(True, {'class': ["norm", "stitle-article-norm", "boldface", "normal", "oj-normal", "note",
                                          "tbl-txt", "tbl-hdr", "tbl-norm", "norm inline-element", "title-doc-first"]})
    text_liste = [str(i.text) for i in tags]
    text = ' '.join(text_liste).replace(u"\u00a0", " ").replace('\n', '')
    return text


def traitement_eurlex(logger):
    """
    Traite tous les json contenus dans le dossier all_json de eurlex
    :param logger: un logger
    :return:
    """
    file_source = "sources/Eurlex/all_json"
    result = (y for x in os.walk(file_source) for y in glob(os.path.join(x[0], '*.json')))

    for path in result:
        try:
            dict_json = jso.get_json_infos(path)
            url_fich_metier = dict_json['url']
        except Exception as e:
            logger.error(f"Problème extraction données json: {path} erreur: {e}")
            continue

        try:
            celex_id = get_celex_id(url_fich_metier)
            url_api = get_url_cellar(celex_id)
        except Exception as e:
            logger.error(f"Problème web service: {url_fich_metier}")
            logger.info(f"url : {url_fich_metier}, erreur : Problème pendant la requête au web service:{e}")
            continue

        try:
            api_result = get_api_result(url_api)
        except Exception as e:
            logger.error(f"Problème api: {url_fich_metier}")
            logger.info(f"url : {url_fich_metier}, erreur : Problème pendant la requête à l'api:{e}")
            continue

        for elem in api_result:
            try:
                output_file = os.path.splitext(path)[0].split('/')[-1] + '_' + elem['lang']
                with open(f"sources/Eurlex/data/{output_file}.html", "w") as f:
                    f.write(elem['content'])
                soup = BeautifulSoup(elem['content'], 'html.parser')
                text = get_content_from_html(soup)
                dict_json['text_name'] = get_doc_name(soup)
                dict_json = jso.clean_content(text, dict_json)
                dict_json['url'] = elem['url']
                dict_json['extension'] = '.html'
                jdoc = jso.creation_jdoc(dict_json)
                jdoc['url_fich_metier'] = url_fich_metier
                date_collect = str(date.today())
                output = f"sources/Eurlex/final_json/{date_collect}_{output_file}.json"
                with open(output, 'w') as fp:
                    json.dump(jdoc, fp, indent=4)

            except Exception as e:
                logger.error(f"Problème traitement réponse api: {url_fich_metier}")
                logger.info(f"url : {url_fich_metier}, erreur : {e}")
