from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fastapi.responses import FileResponse
import uvicorn

description = """
Testing API ðŸš€
"""

tags_metadata = [
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
    version="1.0.1",
    summary="API used for local development environment.",
    contact={
        "name": "Ong Zhi Xian",
        "email": "zhixian@hotmail.com"
    },
    license_info={
        "name": "GNU Affero General Public License 3.0",
        "url": "https://www.gnu.org/licenses/agpl-3.0.en.html",
    },
    # openapi_url="/openapi.json",
    # servers=[
    #     {"url": "https://stag.example.com", "description": "Staging environment"},
    #     {"url": "https://prod.example.com", "description": "Production environment"},
    # ],
    root_path="/api", # NEEDED FOR CADDY REVERSE PROXY to get openapi_url properly
)


origins = [
    "http://localhost",
    "http://localhost:9200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models

class SeatingPlanDefinition(BaseModel):
    title: str
    numberOfRows: int
    seatsPerRow: int

class BookingRequest(BaseModel):
    title: str
    numberOfSeatsToBook: int
    startSeat: Union[str, None] = None

# Endpoints
from seating_planner import SeatingPlanner
seatingPlanStore = {}

@app.post("/seating-plan")
def create_seating_plan(seatingPlanDefinition: SeatingPlanDefinition):
    print('In POST /seating-plan')
    seating_planner = SeatingPlanner(
        seatingPlanDefinition.title,
        seatingPlanDefinition.numberOfRows,
        seatingPlanDefinition.seatsPerRow)
    seatingPlanStore[seatingPlanDefinition.title] = seating_planner
    return {
        "status": "ok",
        "statusText": f"Store seating plan for {seatingPlanDefinition.title}"
    }

@app.get("/seating-plan/{title}")
def get_seating_plan(title: str):
    if title in seatingPlanStore:
        return {
            "status": "ok",
            "statusText": f"Seating plan for {title}",
            "data": seatingPlanStore[title].get_seating_plan()
        }

    return {
        "status": "notFound",
        "statusText": f"Seating plan for {title} not found"
    }

@app.patch("/seating-plan/{title}")
def book_seats(title:str, bookingRequest: BookingRequest):
    print('In PATCH /seating-plan')
    print(title)
    print(bookingRequest)
    if title not in seatingPlanStore:
        return {
            "status": "notFound",
            "statusText": f"Seating plan for {title} not found"
        }
    booking_id = seatingPlanStore[title].book_seats(bookingRequest.numberOfSeatsToBook)
    return {
        "status": "ok",
        "statusText": f"Updated seating plan.",
        "data": {
            "booking_id": booking_id
        }
    }

@app.delete("/seating-plan/{title}/{booking_id}")
def read_item(title: str, booking_id: str):
    print('In DELETE /seating-plan')
    if title not in seatingPlanStore:
        return {
            "status": "notFound",
            "statusText": f"Seating plan for {title} not found"
        }

    seatingPlanStore[title].unbook_seats(booking_id)
    return {
        "status": "ok",
        "statusText": f"Booking id {booking_id} remove. Seating plan updated."
    }

# @app.get("/seating-plan/{title}/{booking_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}
#
# @app.delete("/seating-plan/{title}/{booking_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}







# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


# This is only needed if we want to run using python.exe
# FastAPI seems to recommend running using its own executable fastapi.exe, id est:
# fastapi.exe dev fastapi_main.py --port 9201 --app app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9201)