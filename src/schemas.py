from typing import List, Optional

from pydantic import BaseModel, Field

class Status(BaseModel):
    id: int
    state: str

class Message(BaseModel):
    message: str

class EntryBase(BaseModel):
    term: str

class EntryCreate(EntryBase):
    term_id = str
    pass

class Entry(EntryBase):
    id: int
    request_id: int
    class Config:
        orm_mode = True

class DictionaryBase(BaseModel):
    # endpoint: Optional[str] = None
    id_dict: str
    apiKey: Optional[str] = None

class DictionaryCreate(BaseModel):
    # endpoint: Optional[str] = None
    id: str = Field(..., title="The identifier of the source dictionary to be linked, as it is specified by the source endpoint.")
    apiKey: Optional[str] = Field(None, title="A key to be used to access the dictionary, to be passed as an X-API-KEY header, currently not implemented.")

class Dictionary(DictionaryBase):
    id: int

    class Config:
        orm_mode = True

class RequestBase(BaseModel):
    source_id: int
    target_id: int

class RequestCreate(BaseModel):
    entries: Optional[List[str]] = Field(None, title="The list of source entries to link by their ID in the endpoint. If empty all entries are linked")
    source: DictionaryCreate = Field(..., title="The source dictionary")
    # target: DictionaryCreate
    configuration: Optional[dict] = Field(None, title="An implementation specific configuration object. Currently not implemented.")
    class Config:
        schema_extra = {
            "example": {
                "entries": ["plane-n", "dog-v", "nice-a"],
                "source": {"id": "Dictionary ID", "apiKey": "Api key to access the dictionary"},
            }
        }
class RequestDefCreate(BaseModel):
    definition: str = Field(..., title="Definition to be linked")
    lan: str = Field(..., title="Language of the definition")
    lemma: str = Field(..., title="Lemma to be linked")
    configuration: Optional[dict] = Field(None, title="An implementation specific configuration object. Currently not implemented.")
    class Config:
        schema_extra = {
            "example": {
                "definition": "A plane is a flat, two-dimensional, rigid body that is capable of moving in the direction of its motion.",
                "lemma": "plane-n",
                "lan": "en",
            }
        }
class Request(RequestBase):
    id: int
    entries: Optional[List[Entry]] = []

    class Config:
        orm_mode = True
