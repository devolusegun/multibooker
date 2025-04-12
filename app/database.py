from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

# DATABASE_URL format: "postgresql://user:password@localhost/dbname"
DATABASE_URL = os.getenv("postgresql://native:SUOMTHu6QPgwdeyfaz49oSyoSmG6AZZG@dpg-cvt9b9re5dus73a4s540-a.oregon-postgres.render.com/multibookdb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
