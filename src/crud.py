from sqlalchemy.orm import Session
import api_calls
from fastapi import HTTPException
import models, schemas

def get_dictionary(db: Session, id: int):
    return db.query(models.Dictionary).filter(models.Dictionary.id == id).first()

def get_dictionary_by_identifier(db: Session, dict_id: str):
    return db.query(models.Dictionary).filter(models.Dictionary.id_dict == dict_id).first()

def create_dictionary(db: Session, dict: schemas.DictionaryCreate):
    db_dict = models.Dictionary(id_dict=dict.id, apiKey=dict.apiKey)#, endpoint=dict.endpoint, 
    db.add(db_dict)
    db.commit()
    db.refresh(db_dict)
    return db_dict

def get_request(db: Session, id: int):
    return db.query(models.Request).filter(models.Request.id == id).first()

def get_pending_request(db: Session):
    return db.query(models.Request).filter(models.Request.status == "PROCESSING").first()

def create_entry_request(db: Session, entry: schemas.EntryCreate):
    db_entry = models.Entry(term=entry.term, term_id=entry.term_id, request_id=entry.request_id)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def create_request(db: Session, request: schemas.RequestCreate):
    source_dict = get_dictionary_by_identifier(db = db, dict_id = request.source.id)
    if source_dict is None:
        source_dict = create_dictionary(db, request.source)
    # target_dict = get_dictionary_by_identifier(db = db, dict_id = request.target.id) # add hardcoded Babelnet id.
    # if target_dict is None:
    #     target_dict = create_dictionary(db, request.target)
    db_request = models.Request(source=source_dict)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)  
    request_id = db_request.id
    entries = []
    if request.entries is None:
        return db_request.id
    for term in request.entries:
        entry = models.Entry(term=term, request_id=request_id)
        pos_tag = entry.term.split('-')[-1]
        term_text = ''.join(entry.term.split('-')[:-1])
        lemma_terms = api_calls.get_lemma_id(term_text, source_dict.id_dict, source_dict.apiKey)
        lemma_id = None
        if pos_tag not in api_calls.map_pos:
            db.delete(db_request)
            db.commit()
            # db.refresh(db_request)
            return HTTPException(status_code=404, detail=f"The pos tag {pos_tag} is not accepted. Please use n (NOUN), v (VERB), aj (ADJ) or av (ADV).")
        for lemma_term in lemma_terms:
            if lemma_term["partOfSpeech"][0] == api_calls.map_pos[pos_tag]:
                lemma_id = lemma_term["id"]
        if lemma_id is None:
            db.delete(db_request)
            db.commit()
            # db.refresh(db_request)
            return HTTPException(status_code=404, detail=f"The term {term_text} does not appear in the dictionary as {api_calls.map_pos[pos_tag]}")
        else:
            entry.term_id = lemma_id
        entries.append(create_entry_request(db, entry))
    db_request.entries = entries
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request.id

def create_def_request(db: Session, request: schemas.RequestDefCreate):
    # target_dict = get_dictionary_by_identifier(db = db, dict_id = request.target.id) # add hardcoded Babelnet id.
    # if target_dict is None:
    #     target_dict = create_dictionary(db, request.target)
    db_request = models.Request() 
    db.add(db_request)
    db.commit()
    db.refresh(db_request)  
    request_id = db_request.id
    definitions = []
    definition = models.Definition(definition=request.definition, request_id=request_id, lemma=request.lemma, lan=request.lan)
    
    pos_tag = definition.lemma.split('-')[-1]
    # term_text = ''.join(definition.lemma.split('-')[:-1])
    # lemma_terms = api_calls.get_lemma_id(term_text, source_dict.id_dict)
    # lemma_id = None
    if pos_tag not in api_calls.map_pos:
        db.delete(db_request)
        db.commit()
        # db.refresh(db_request)
        return HTTPException(status_code=404, detail=f"The pos tag {pos_tag} is not accepted. Please use n (Noun), v (Verb), aj (Adj) or av (Adv).")

    definitions.append(definition)
    db_request.definitions = definitions
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request.id

def update_request(db: Session, db_request: models.Request):
    db_request.status = "COMPLETED"
    db.add(db_request)
    db.commit()
    db.refresh(db_request)  
    return
