# main.py

from fastapi import FastAPI
from api.routes import router
from database import connect_to_mongo

app = FastAPI()


@app.on_event("startup")
def startup():
    connect_to_mongo()


app.include_router(router)
