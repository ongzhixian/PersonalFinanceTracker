from fastapi_main import app

from explore import dump_event_context

@app.get("/exlore/dump_event_context", tags=["explore"])
def explore_dump_event_context():
    return {"PLACEHOLDER": "dump_event_context"}
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

