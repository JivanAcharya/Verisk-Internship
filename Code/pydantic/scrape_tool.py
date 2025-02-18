from bs4 import BeautifulSoup
import requests
from schemas import ScrapeResult


class ScrapeTool:
    
    def scrape_and_parse(self, url : str) -> ScrapeResult:
        """
        Fetch a webpage and extract its title and content.
        """
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "No title"
        content = " ".join([p.text for p in soup.find_all('p')])
        return ScrapeResult(title=title, content=content)