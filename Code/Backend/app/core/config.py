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
        self.refresh_token_expire_time: int = 60 * 24 * 7

        self.SMTP_TLS: bool = self.env_vars.get("SMTP_TLS", "False").lower() == "true"
        self.SMTP_SSL: bool = self.env_vars.get("SMTP_SSL", "False").lower() == "false"
        self.SMTP_PORT: int = int(self.env_vars.get("SMTP_PORT", 587))
        self.SMTP_HOST: str | None = self.env_vars.get("SMTP_HOST")
        self.SMTP_USER: str | None = self.env_vars.get("SMTP_USER")
        self.SMTP_PASSWORD: str | None = self.env_vars.get("SMTP_PASSWORD")
        self.EMAILS_FROM_EMAIL: str | None = self.env_vars.get("EMAILS_FROM_EMAIL")
        self.EMAILS_FROM_NAME: str | None = self.env_vars.get("EMAILS_FROM_NAME")

        self.PROJECT_NAME:str = "UniBro"

#instatiate the class
settings = Settings()
