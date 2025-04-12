from fastapi import FastAPI
from app.routes import uploadbet, auth # Import your routers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://multibooker.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your routers
app.include_router(uploadbet.router)
app.include_router(auth.router)