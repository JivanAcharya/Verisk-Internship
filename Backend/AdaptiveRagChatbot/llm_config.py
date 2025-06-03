from langchain_groq import ChatGroq
llm = ChatGroq(model = "meta-llama/llama-4-scout-17b-16e-instruct", temperature=0, )

# from langchain_google_genai import ChatGoogleGenerativeAI

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
#     temperature=0)