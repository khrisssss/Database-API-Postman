from fastapi import FastAPI
from routers.person import router as router_person
from routers.firstname import router as router_firstname
from routers.lastname import router as router_lastname
from routers.relationship import router as router_relationship

app = FastAPI(
    title="Bob Family Tree API",
    description="Open /docs to test everything!",
    version="1.0.0",

openapi_tags=[
        {
            "name": "Person",
            "description": "Work with persons in the family tree."
        },
        {
            "name": "Names",
            "description": "Add, rename or delete firstnames and lastnames."
        },
        {
            "name": "Relationships",
            "description": "Manage parent and child links between persons."
        },
        {
        "name": "FirstName",
        "description": "Add, rename or delete firstnames of a person."
        },
        {
            "name": "LastName",
            "description": "Add, rename or delete lastnames of a person."
        },
        {
            "name": "Relationships",
            "description": "Manage parent and child links between persons."
        }
    ]
)
app.include_router(router_person)
app.include_router(router_firstname)
app.include_router(router_lastname)
app.include_router(router_relationship)