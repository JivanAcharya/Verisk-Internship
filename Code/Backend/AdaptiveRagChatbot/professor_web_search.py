from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel
from typing import List,Optional
from langchain_core.prompts import ChatPromptTemplate

import json
from bs4 import BeautifulSoup
import requests

from .llm_config import llm


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
system = system = """You are an expert in extracting structured information from text. \n
Extract the following details strictly as defined: \n
- **Professor Name**: Extract the full name with proper casing. Do not abbreviate. \n
- **University**: Extract the full university name, avoiding abbreviations. If a location is mentioned, format it as "<University Name> - <Location>". \n
Return only the extracted values without additional text or explanations."""


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
    name: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    office: Optional[str] = None
    research_interests: Optional[str] = None
    bio: Optional[str] = None
    publications: Optional[List] = None
    website: Optional[str] = None

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
     with open("AdaptiveRagChatbot/university_professors.json", "r") as f:
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
            print("\n SCRAPED DATA FROM WEBSITE : ",data)
            print(type(data))
            formatted_data = professor_data_extractor.invoke({"document": data})
            formatted_data_dict = formatted_data.model_dump()
            formatted_data_dict["website"] = professors_website  
            
            final_result = ProfessorSearchResults(**formatted_data_dict)
            print(final_result)
            return final_result
            
    

    else:
        return "not found"
