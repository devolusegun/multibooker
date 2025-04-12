# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Bring in your new route modules
from app.routes import uploadbet, auth

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://multibooker.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include each router
app.include_router(uploadbet.router)  # the upload bet endpoint
app.include_router(auth.router)       # your auth endpoints