from fastapi import FastAPI
from api.routes import router
from database import connect_to_mongo, close_mongo_connection

app = FastAPI(title="Skeleton Service", version="1.0.0")

app.include_router(router)


@app.on_event("startup")
def startup_event():
    connect_to_mongo()


@app.on_event("shutdown")
def shutdown_event():
    close_mongo_connection()
