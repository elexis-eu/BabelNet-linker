import json
from typing import List, Tuple

import requests

_HEADERS = {"Content-Type": "application/json;charset=UTF-8"}

def rest_bn(
    lemma: str, pos: str, lan: str, url="http://192.168.1.91:9878"
) -> List[Tuple[str, str]]:
    r = requests.post(url, json.dumps({"lemma": lemma, "pos": pos, "lan": lan}), headers=_HEADERS)
    json_response = r.json()

    return json_response["senses"]

# def rest_bn_synsets(
#     synset_ids: List[str], url="http://192.168.1.91:9878/synset"
# ) -> List[Tuple[str, str]]:
#     r = requests.post(url, json.dumps({"synset_ids": synset_ids}), headers=_HEADERS)
#     print(r)
#     json_response = r.json()

#     return json_response["senses"]

# def rest_bn_lemmas(
#     synset_ids: List[str], language: str, url="http://192.168.1.91:9878/lemmas"
# ) -> List[Tuple[str, str]]:
#     r = requests.post(url, json.dumps({"synset_ids": synset_ids, "lan": language}), headers=_HEADERS)
#     print(r)
#     json_response = r.json()

#     return json_response["senses"]

# def rest_bn_mainsenses(
#     synset_ids: List[str], language: str, url="http://192.168.1.91:9878/main_senses"
# ) -> List[Tuple[str, str]]:
#     r = requests.post(url, json.dumps({"synset_ids": synset_ids, "lan": language}), headers=_HEADERS)
#     print(r)
#     json_response = r.json()

#     return json_response["senses"]

# def rest_bn_examples(
#     synset_ids: List[str], language: str, url="http://192.168.1.91:9878/examples"
# ) -> List[Tuple[str, str]]:
#     r = requests.post(url, json.dumps({"synset_ids": synset_ids, "lan": language}), headers=_HEADERS)
#     print(r)
#     json_response = r.json()

#     return json_response["senses"]

# def rest_bn_senses(
#     lemma: List[str], pos: List[str], lan: str, url="http://192.168.1.91:9878/senses"
# ) -> List[List[Tuple[str, str]]]:
#     r = requests.post(url, json.dumps({"lemma": lemma, "pos": pos, "lan": lan}), headers=_HEADERS)
#     print(r)
#     json_response = r.json()

#     return json_response["senses"]

# def rest_bn_lemma_sense(
#     lemma: List[str], pos: List[str], url="http://192.168.1.91:9878/get_synsets"
# ) -> List[List[Tuple[str, str]]]:
#     r = requests.post(url, json.dumps({"lemma": lemma, "pos": pos}), headers=_HEADERS)
#     json_response = r.json()

#     return json_response["senses"]
