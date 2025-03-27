from dotenv import load_dotenv, dotenv_values
# from pydantic_settings import BaseSettings

class Settings:
    def __init__(self):
        load_dotenv()
        self.env_vars = dotenv_values()

        self.database_url = self.env_vars.get("DATABASE_URL")
        self.hashing_algorithm = self.env_vars.get("HASHING_ALGORITHM")
        self.secret_key = self.env_vars.get("SECRET_KEY")
        self.access_token_expire_time: int  = 60

#instatiate the class
settings = Settings()
