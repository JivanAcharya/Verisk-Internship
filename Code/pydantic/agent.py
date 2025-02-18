import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
from pydantic_ai import Agent, RunContext
from scrape_tool import ScrapeTool
from schemas import ScrapeResult

class AgentDependencies:
    def __init__(self, scrape_tool : ScrapeTool):
        self.scrape_tool = scrape_tool

dependencies = AgentDependencies(ScrapeTool())
agent = Agent(  
    'google-gla:gemini-1.5-flash',
    deps_type=dependencies,
    system_prompt=('Your job is to scrape a webpage and extract its title and content.'
                    "You should use the `scrape` tool to fetch and parse the webpage."  
                    "the present the content is a nicely formated and summarized manner"
                    )
)

@agent.tool
async def scrape(ctx:RunContext[AgentDependencies], url:str)-> ScrapeResult:
     """Use the scrape tool to fetch and parse a webpage."""
     return ctx.scrape_tool.scrape_and_parse(url)


async def main():
    # async with AsyncClient() as client:
       
        deps ="https://python-helpers.readthedocs.io/en/latest/helpers/asyncx/privex.helpers.asyncx.run_sync.html"
        
        result = await agent.run(
            'What is the content of the website', deps=deps
        )
        # debug(result)
        print('Response:', result.data)
        # print(f"Title: {result.title}")
        # print(f"Content: {result.content}")



if __name__ == '__main__':
    asyncio.run(main())

# result = scrape(dependencies, )
# print(f"Title: {result.title}")
# print(f"Content: {result.content}")
