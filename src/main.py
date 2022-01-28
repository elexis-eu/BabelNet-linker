from typing import List
import json

from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine
from run_async import run_pending
models.Base.metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "submit",
        "description": "Submit a request for linking the senses for a given lemma or definition. Returns the id of the request. Keep it for later use.",
    },
    {
        "name": "result",
        "description": "Retrieve the result of a request by providing its id.",
    },
]

app = FastAPI(
    title="SenseLinking",
    description="An API for linking senses of a given lemma to BabelNet.",
    version="0.1.0",
    openapi_tags=tags_metadata,
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/submit/", tags=["submit"])
async def create_item(item: schemas.RequestCreate, db: Session = Depends(get_db)):
    return crud.create_request(db = db, request = item)

@app.get("/status/", tags=["status"], response_model=schemas.Status, responses={
        404: {"description": "Request not found"},
        200: {
            "description": "Status of the item requested by ID",
            "content": {
                "application/json": {
                    "example": {"id": 42, "state": "COMPLETED"}
                }
            },
        },
    })
async def check_status(request_id: str = Query(None, title="ID of the request to check status of"), db: Session = Depends(get_db)):
    db_request = crud.get_request(db = db, id = request_id)
    if db_request is None:
        return HTTPException(status_code=404, detail="Request not found")
    dict_response = {
        "id": request_id,
        "state": db_request.status,
        # "message": "Still working away"
    }
    return dict_response


@app.get("/result", tags=["result"], responses={
    404: {"description": "Request not found"},
    301: {"description": "Request not completed"},
    200: {"description": "Result of the request",
        "content": {
            "application/json": {
                "example": {
                    "source_entry": "cordel-n", 
                    "target_entry": "cordel-n", 
                    "linking": [{
                        "source_sense": {
                            "definition": "Un tipo de cuerda pequeña o delgada."
                            }, 
                        "target_sense": ["bn:00074682n", "A long, thin and flexible structure made from threads twisted together."], 
                        "type": "exact", 
                        "score": 0.987201452255249
                        }, 
                    {
                        "source_sense": {
                            "definition": "Un tipo de cuerda pequeña o delgada."
                            }, 
                        "target_sense": ["bn:00074685n", "A linear sequence of symbols (characters or words or phrases)."], 
                        "type": "unrelated", 
                        "score": 0.3604495072364807
                        },
                        ]
                    }
                }
            }
        }})
async def retrieve_result(request_id: str = Query(None, title="ID of the request to retrieve"), db: Session = Depends(get_db)):
    db_request = crud.get_request(db = db, id = request_id)
    if db_request is None:
        return HTTPException(status_code=404, detail="Request not found.")
    elif db_request.status != "COMPLETED":
        return HTTPException(status_code=301, detail="Request still has not been processed.")
    with open(f'results/request_{request_id}.json') as f:
        data = json.load(f)
    return data
