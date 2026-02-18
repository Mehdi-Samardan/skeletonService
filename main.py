from fastapi import FastAPI
from utils.logger import logger
from api.routes import router
from database import connect_to_mongo, close_mongo_connection
from repositories.skeleton_repository import SkeletonRepository


app = FastAPI(title="Skeleton Service", version="1.0.0")

app.include_router(router)


@app.on_event("startup")
def startup_event():
    connect_to_mongo()


@app.on_event("shutdown")
def shutdown_event():
    close_mongo_connection()


# For testing database connection on startup
# @app.on_event("startup")
# def startup_event():
#     connect_to_mongo()
#     repo = SkeletonRepository()
#     logger.info(f"Collection name: {repo.collection.name}")


#  For testing get_by_hash method on startup
# @app.on_event("startup")
# def startup_event():
#     connect_to_mongo()
#     repo = SkeletonRepository()
#     test_hash = "test_hash_123"
#     result = repo.get_by_hash(test_hash)

#     logger.info(f"Test get_by_hash result: {result}")
