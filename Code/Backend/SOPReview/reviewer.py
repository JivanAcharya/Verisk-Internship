from .fileparser import parser

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import json

llm = ChatGroq(model = "meta-llama/llama-4-scout-17b-16e-instruct", temperature=0)

system = """You are an expert in reviewing academic Statements of Purpose (SOPs). A student has written an SOP to apply for graduate studies. Your task is to critically review and analyze the SOP based on the following four aspects:

1. **Grammar & Style**
- Check for grammatical errors, sentence structure issues, and academic tone.
- Highlight passive voice, repetition, or verbosity.

2. **Content Structure**
- Evaluate if the SOP follows a logical structure: introduction, academic background, professional experience (if any), research interests, and conclusion.
- Point out missing or disorganized sections.

3. **Clarity & Coherence**
- Determine if the SOP is easy to follow, with smooth transitions and clear ideas.
- Flag vague or ambiguous statements.

4. **Strength of Research Interests**
- Assess how clearly the student states their research goals and how well it aligns with their past experience.
- Comment on whether the SOP mentions professors, labs, or specific projects at the target institution (if applicable).

---

Return your feedback strictly in the following JSON format for easy parsing, no preamble:

{{
  "grammar_and_style": "<your feedback here>",
  "structure": "<your feedback here>",
  "clarity_and_coherence": "<your feedback here>",
  "research_interests_strength": "<your feedback here>",
  "overall_rating": "<Strong / Moderate / Needs Improvement>"
}}

---

"""

review_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",system),
       ("human", "SOP to review :\n\n {sop_text}"),
    ]
)

reviewer = review_prompt | llm


def review_sop(sop_text):
    """
    Review the SOP text and return the feedback in JSON format.
    """
    res = reviewer.invoke(
                {"sop_text": sop_text}
            )

    output = res.content 
    output = output.strip("`").strip()
    output = output.replace("json", "",1)

    # convert to dict
    clean_json = json.loads(output)

    # save to json remove later
    with open("SOPReview/output.json", "w") as f:
       json.dump(clean_json, f, indent=4)
    
    return clean_json