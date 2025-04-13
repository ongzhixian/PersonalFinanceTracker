from typing import Union

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

description = """

This FastAPI is intend to quickly prototyping APIs to test feasibility and gaps in design. 🚀

## Notes

You can **read items**.

## Related Links

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

tags_metadata = [
    {
        "name": "explore",
        "description": "Utilitarian function for exploring AWS Lambda input event and context.",
    },
    {
        "name": "telegram-bot",
        "description": "Telegram webhooks for bots.",
    },
    # {
    #     "name": "users",
    #     "description": "Operations with users. The **login** logic is also here.",
    # },
    # {
    #     "name": "items",
    #     "description": "Manage items. So _fancy_ they have their own docs.",
    #     "externalDocs": {
    #         "description": "Items external docs",
    #         "url": "https://fastapi.tiangolo.com/",
    #     },
    # },
]


app = FastAPI(
    title="FastAPI Local Dev",
    openapi_tags=tags_metadata,
    description=description,
    version="0.0.1",
    summary="API used for local development environment.",
    terms_of_service="/terms-of-service.html",
    contact={
        "name": "Ong Zhi Xian",
        "url": "http://localhost/contact.html",
        "email": "zhixian@hotmail.com",
    },
    license_info={
        "name": "GNU Affero General Public License 3.0",
        "url": "https://www.gnu.org/licenses/agpl-3.0.en.html",
    },
    # openapi_url="/openapi.json",
    servers=[
        {"url": "https://stag.example.com", "description": "Staging environment"},
        {"url": "https://prod.example.com", "description": "Production environment"},
    ],
    root_path="/api", # NEEDED FOR CADDY REVERSE PROXY to get openapi_url properly
)

app.mount("/www", StaticFiles(directory="www"), name="static")

@app.get("/")
def read_root():
    return {"Hello": "World22"}


# @app.get("/")
# async def read_index():
#     return FileResponse('index.html')


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

from fastapi_explore import explore_dump_event_context

from fastapi_telegram_bot import telegram_plato_dev_bot

# This is only needed if we want to run using python.exe
# FastAPI seems to recommend running using its own executable fastapi.exe, id est:
# fastapi.exe dev fastapi_main.py --port 10020 --app app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10020)