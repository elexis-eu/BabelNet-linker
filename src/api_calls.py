import requests
import json

map_pos = {'v': 'verb', 'n': 'noun', 'aj':'adj', 'av':'adv'}
# url = "https://lexonomy.elex.is/dictionaries"
# r = requests.get(url, headers={"X-API-Key": "GXCQJ6S2FZUATM5Z2S0MGZ7XOMXKUFNP"})
# print(r.content)
# dict_lists = json.loads(r.content)["dictionaries"]
BN_KEY = "4407db6d-bf70-43ef-974c-a4f451988197"
def get_info(id: str, api_key: str = "GXCQJ6S2FZUATM5Z2S0MGZ7XOMXKUFNP"):
    url = f"https://lexonomy.elex.is/about/{id}"
    r = requests.get(url, headers={"X-API-Key": api_key})
    return json.loads(r.content)

# print(get_info(dict_lists[-1]))
# for dict_id in dict_lists:
#     print(dict_id, get_info(dict_id))

def get_lemma(id: str, term: str, api_key: str = "GXCQJ6S2FZUATM5Z2S0MGZ7XOMXKUFNP"):
    url = f"https://lexonomy.elex.is/lemma/{id}/{term}"
    r = requests.get(url, headers={"X-API-Key": api_key})
    return json.loads(r.content)

def get_senses(id: str, term_id: str, api_key: str = "GXCQJ6S2FZUATM5Z2S0MGZ7XOMXKUFNP"):
    url = f"https://lexonomy.elex.is/json/{id}/{term_id}"
    r = requests.get(url, headers={"X-API-Key": api_key})
    return json.loads(r.content)

def get_words(id: str, api_key: str = "GXCQJ6S2FZUATM5Z2S0MGZ7XOMXKUFNP"):
    url = f"https://lexonomy.elex.is/list/{id}"
    r = None
    while r is None:
        r = requests.get(url, headers={"X-API-Key": api_key}, timeout=480)
    # print(r.content)
    return json.loads(r.content)

def get_lemma_id(lemma: str, dict: str, api_key: str = "GXCQJ6S2FZUATM5Z2S0MGZ7XOMXKUFNP"):
    url = f"https://lexonomy.elex.is/lemma/{dict}/{lemma}"
    print(url)
    r = requests.get(url, headers={"X-API-Key": api_key})
    return json.loads(r.content)

def get_senses_from_lemma(id: str, term: str):
    post_tag = term.split('-')[-1]
    lemma_terms = get_lemma_id(id, term)
    lemma_id = None
    for lemma_term in lemma_terms:
        if lemma_terms["partOfSpeech"][0] == map_pos[post_tag]:
            lemma_id = lemma_term["id"]
    return get_senses(id, lemma_id)

def get_bn_synsets(lemma: str, lan: str, pos: str):
    # 4407db6d-bf70-43ef-974c-a4f451988197
    url = f"https://babelnet.io/v6/getSynsetIds?lemma={lemma}&searchLang={lan}&pos={pos}&key={BN_KEY}"
    r = requests.get(url)
    return json.loads(r.content)
