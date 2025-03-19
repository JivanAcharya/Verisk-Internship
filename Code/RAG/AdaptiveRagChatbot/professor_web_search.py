from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel
from typing import List,Optional
from langchain_core.prompts import ChatPromptTemplate

import json
from bs4 import BeautifulSoup
import requests

from llm_config import llm


## Initialize web search tool for general searches
web_search_tool = TavilySearchResults(k=3)

##Extracting keywords like professor name and university from query
class ExtractKeywords(BaseModel):
    """
    Extract professor name and university from the query
    """
    professor_name: Optional[str] = None
    university: Optional[str] = None

structured_extract_keywords = llm.with_structured_output(ExtractKeywords)

#Grader Prompt
system = """You are an expert at extracting information from the given query. \n
    You are to extract the following information if available: \n
    - Professor Name \n
    - University 
    Make sure that the professors name is in proper casing and give the full university name, not in the abbreviated form\n
    If univeristy location is mentioned then return as this form :: <University Name> - <Location> \n For eg: University of California - Santa Cruz
    """

extract_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",system),
         ("human", "User question: {question}"),
    ]
)

keywords_extractor = extract_prompt | structured_extract_keywords



## for Json specific professor search
class ProfessorSearchResults(BaseModel):
    """
    Represents the results of a professor search
    """
    name: str
    title: str
    department: str
    email: str
    phone: str
    office: str
    website: str
    research_interests: str
    bio: str
    publications: str
structured_professor_search = llm.with_structured_output(ProfessorSearchResults)

#Grader Prompt 
system = """You are an expert at extracting information form the given extracted professors webpage. \n
    You are to extract the following information: \n
    - Name \n
    - Title \n
    - Department \n
    - Email \n
    - Phone \n
    - Office \n
    - Website \n
    - Research Interests \n
    - Bio \n
    - Publications \n
    """

extract_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",system),
       ("human", "Retrieved document: \n\n {document}"),
    ]
)

professor_data_extractor = extract_prompt | structured_professor_search

def get_professors_website(professor_name: str, university: str):
     with open("university_professors.json", "r") as f:
        data = json.load(f)
        
        # if university present
        if university:
            if university in data:
                for prof in data[university]:
                    if prof[0] == professor_name:
                        return prof[1]
            return None  

        # If only professor_name is given, search across all universities
        elif professor_name:
            for uni, professors in data.items():
                for prof in professors:
                    if prof[0] == professor_name:
                        return prof[1] 
        
        return None 

def scrape_website_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except requests.RequestException as e:
        return f"Error fetching website content: {e}"

def professor_search_json(question: str):
    """
    Search for professors in the json data with re-phrased question.
    
    Args:
        query (str): The query to search for professors
    
    Returns:
        ProfessorSearchResults: The results of the search
    """
    print("\n Professor Search by extracting website from json")
    resp =  keywords_extractor.invoke({"question": question})
    print(resp.professor_name, resp.university)
    professor_name = resp.professor_name
    university = resp.university
    
    if professor_name or university:
        professors_website = get_professors_website(professor_name, university)
        print("\n WEBSITE : ",professors_website)
        if professors_website:
            data = scrape_website_content(professors_website)
            formatted_data = professor_data_extractor.invoke({"document": data})
            print(formatted_data)
            return formatted_data
            
    

    else:
        return "\nProfessor name or university not found in the query"
