from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL =  os.getenv("DATABASE_URL")

# an Engine, which the Session will use for connection
# resources
engine = create_engine(DATABASE_URL)

