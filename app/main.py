from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Multibooker API")

app.include_router(router)