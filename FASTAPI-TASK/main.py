from fastapi import FastAPI
from app.task import router
from app.database import Base, engine
from app.custom_middleware import TokenAuthMiddleware
app = FastAPI()


app.include_router(router)
app.add_middleware(TokenAuthMiddleware)
