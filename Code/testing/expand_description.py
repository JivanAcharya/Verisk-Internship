import pandas as pd
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
import os
# Set up Groq API
groq_api_key = os.environ("GROQ_API_KEY")
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)

# Load CSV file
df = pd.read_csv("notebook/uni_with_description.csv")  # Ensure your CSV is correctly formatted
counter = 1

def expand_description(row):
    """Uses Groq LLM via LangChain to generate a detailed university description."""
    prompt = f"""
    Provide a detailed description for {row['name']} located in {row['Location']}.
    This university is ranked {row['rank']} globally.

    Key information:
    - Citations Score: {row['scores_citations']}
    - Research Score: {row['scores_research']}
    - Teaching Score: {row['scores_teaching']}
    - Student Population: {row['stats_number_students']}
    - International Students: {row['stats_pc_intl_students']}
    - Subjects Offered: {row['subjects_offered']}

    Write the response in a **formal and informative tone**, focusing on academic excellence, campus life, global reputation, and research impact.
    """
    print("Processing:")
    x  = list(row)
    response = llm.invoke([SystemMessage(content="You are an expert education consultant."), HumanMessage(content=prompt)])
    x.append(response.content)  

    return x

columns =list(df.columns)
columns.append("Expanded Description")
new_df = pd.DataFrame(columns=columns)
for i in range(len(df)):
    x = expand_description(df.iloc[i,:])
    new_df.loc[len(new_df)] = x


# Save enriched CSV
df.to_csv("universities_enriched.csv", index=False)

print("Expanded descriptions generated successfully!")
