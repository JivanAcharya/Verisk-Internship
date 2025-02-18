from pydantic import BaseModel

class ScrapeResult(BaseModel):
    title:str
    content:str