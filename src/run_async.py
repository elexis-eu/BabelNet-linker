from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, itertools, json
from database import SessionLocal, engine
import api_calls
import torch
from babelnet_calls import rest_bn

from sentence_transformers import CrossEncoder

def load_model():
    if torch.cuda.is_available():
        model = CrossEncoder('resources/model/', device='cuda')
    else:    
        model = CrossEncoder('resources/model/')
    return model

@torch.no_grad()
def predict(model, texts):
    inputs_a = []
    inputs_b = []
    for i in range(0,len(texts)):
        inputs_a.append(texts[i][0])
        inputs_b.append(texts[i][1])
    # for tensor in encoded_input:
    #     encoded_input[tensor] = encoded_input[tensor].cuda()
    outputs = model.predict(list(zip(inputs_a, inputs_b)), convert_to_tensor=True)
    return outputs.tolist()

def model_call(source_senses, target_senses, model):
    # make sure all source senses have a definition:
    senses_pairs = list(itertools.product(source_senses, target_senses))
    # make sure all source senses have a definition:
    # senses_pairs = [senses_pair for senses_pair in senses_pairs if "definition" in senses_pair[0]]
    senses_definitions = [(pair[0]["definition"], pair[1][1]) for pair in senses_pairs] # list(itertools.product(senses_definitions, senses_definitions))
    preds = predict(model, senses_definitions)#[(senses["senses"][0]["definition"]["en"], senses["senses"][1]["definition"]["en"])])
    outputs = list(zip(senses_pairs, preds))
    mappings = []
    # if len(senses_pairs) == 1:
    #     pred_sense = {
    #         "source_sense": source_senses[0],
    #         "target_sense": target_senses[0],
    #         "type": "exact",
    #         "score": 1
    #     }
    #     mappings.append(pred_sense)
    # else:
    for sense in source_senses:
        sense_preds = sorted([pred for pred in outputs if pred[0][0]['definition']==sense['definition']], key=lambda tup: tup[1], reverse=True)
        for pred in sense_preds:
            # if pred[1] > 0.5:
            # if greater than 0.7 type is exact, if 0.5 type is related, if 0.2 type is unrelated
            pred_sense = {
                "source_sense": pred[0][0],
                "target_sense": pred[0][1],
                "type": "exact" if pred[1] > 0.7 else "related" if pred[1] > 0.5 else "unrelated",
                "score": pred[1]
            }
            mappings.append(pred_sense)
    return mappings

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_pending(db: Session = Depends(get_db)):
    model = load_model()
    while db_request := crud.get_pending_request(db):
        try:
            if db_request.source:
                dict_info = api_calls.get_info(db_request.source.id_dict, db_request.source.apiKey)
                if 'title' not in dict_info:
                    raise HTTPException(status_code=404, detail="Dictionary not found")
                if len(db_request.entries) == 0:
                    words = api_calls.get_words(db_request.source.id_dict, db_request.source.apiKey)
                    full_run = True
                    inv_map = {v: k for k, v in api_calls.map_pos.items()}
                else:
                    words = db_request.entries
                    full_run = False
            else:
                words = db_request.definitions
                dict_info = {"sourceLanguage": words[0].lan}
                full_run = False
            results_elements = []
            results_file = open(f"results/request_{db_request.id}.json", "w")
            for idx, entry in enumerate(words):
                if full_run:
                    if ("partOfSpeech" not in entry) or (entry["partOfSpeech"][0] not in inv_map):
                        continue
                    entry_id = entry["id"]
                    entry_term = entry["lemma"] + "-" + inv_map[entry["partOfSpeech"][0]]
                    pos_tag = entry["partOfSpeech"][0]
                    results_source = api_calls.get_senses(db_request.source.id_dict, entry_id, db_request.source.apiKey)
                elif db_request.source:
                    entry_id = entry.term_id
                    entry_term = entry.term
                    if entry.term.split('-')[-1] not in api_calls.map_pos:
                        continue
                    pos_tag = api_calls.map_pos[entry.term.split('-')[-1]]
                    results_source = api_calls.get_senses(db_request.source.id_dict, entry_id, db_request.source.apiKey)
                else:
                    entry_term = entry.lemma
                    pos_tag = api_calls.map_pos[entry.lemma.split('-')[-1]]
                    results_source = {"senses": [{"definition": entry.definition}]}
                language = dict_info["sourceLanguage"]
                term_json = {"source_entry": entry_term, "target_entry": entry_term}
                results_source["senses"] = [sense for sense in results_source["senses"] if "definition" in sense and sense["definition"]]
                if len(results_source["senses"]) == 0:
                    term_json["linking"] = 'Linking unsuccessful due to no definitions in source dictionary'
                    results_elements.append(term_json)
                    continue
                results_target = rest_bn(''.join(entry_term.split('-')[:-1]), pos_tag, language)
                if len(results_target) == 0:
                    term_json["linking"] = 'Linking unsuccessful due to no matching lemma in Babelnet'
                    results_elements.append(term_json)
                    continue
                # check all have "definition":
                results = model_call(results_source["senses"], results_target, model)
                term_json["linking"] = results
                results_elements.append(term_json)
                if (idx+1) % 500 == 0:
                    print(f'Processed {idx+1} lemmas')
                    # break
            json.dump(results_elements, results_file)
            crud.update_request(db=db, db_request=db_request)
        except HTTPException as e:
            print(e)
            crud.update_request(db=db, db_request=db_request)
    return

if __name__ == "__main__":
    run_pending(next(get_db()))
