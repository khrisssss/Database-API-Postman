from fastapi import FastAPI
from routers.person import router as router_person
from routers.firstname import router as router_firstname
from routers.lastname import router as router_lastname
from routers.relationship import router as router_relationship

app = FastAPI()

app.include_router(router_person)
app.include_router(router_firstname)
app.include_router(router_lastname)
app.include_router(router_relationship)