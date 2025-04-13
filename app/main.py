# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Bring in your new route modules
from app.routes import uploadbet, auth

# Import your engine, Base from database.py
from app.database import engine, Base

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://multibooker.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This line will auto-create any table that doesn't exist:
Base.metadata.create_all(bind=engine)

# Include each router
app.include_router(uploadbet.router)  # the upload bet endpoint
app.include_router(auth.router)       # your auth endpoints