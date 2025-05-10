from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from app.core.config import settings


# an Engine, which the Session will use for connection
# resources
print(settings.database_url)
engine = create_engine(settings.database_url,
                    #    pool_size=30,
                    #    max_overflow=10,
                       )

