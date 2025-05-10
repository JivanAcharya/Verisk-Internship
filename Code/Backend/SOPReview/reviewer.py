from .fileparser import parser

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import json
import re

llm = ChatGroq(model = "meta-llama/llama-4-scout-17b-16e-instruct", temperature=0)

system = """As an expert reviewer of academic Statements of Purpose (SOPs), your primary function is to analyze provided text documents.

**Strictly follow these instructions:**

1.  **Initial Document Check:** Examine the provided text document. If it is NOT a valid academic Statement of Purpose, immediately return the following JSON response and cease all further processing, if it is a valid document move on to step 2 and return the output as stated in no 3.:

    {{
        "message": "<Your short feedback stating that the document is not a valid SOP."
    }}


2.  **SOP Analysis (If Valid):** If the document IS a valid academic Statement of Purpose, proceed with a critical review based on the following four key aspects. Do not perform this analysis if the document is not a valid SOP.

    * **Grammar & Style:**
        * Assess for grammatical errors, punctuation issues, and sentence structure problems.
        * Evaluate the overall tone for academic appropriateness.
        * Identify and note instances of passive voice, unnecessary repetition, or overly verbose phrasing.

    * **Content Structure:**
        * Determine if the SOP follows a logical and conventional structure, typically including: Introduction (stating purpose), Academic Background, Professional Experience (if any), Research Interests/Goals, and Conclusion.
        * Point out any missing sections, illogical flow, or disorganization.

    * **Clarity & Coherence:**
        * Assess how easy the SOP is to read and understand.
        * Evaluate the flow between paragraphs and ideas; are transitions smooth?
        * Identify and flag any statements that are vague, ambiguous, or difficult to interpret.

    * **Strength of Research Interests:**
        * Analyze how clearly the student articulates their specific research goals and areas of interest.
        * Evaluate how well the stated research interests connect with and are supported by the student's past academic background and experience.
        * Note whether the SOP mentions specific faculty members, research labs, or projects at the target institution, if applicable based on the SOP's content.

3.  **Output Format:** After completing the SOP analysis (and only if the document was a valid SOP), generate the review feedback **strictly** in the following JSON format. **Do not include any preamble or additional text outside of this JSON structure.**

    {{
      "grammar_and_style": "<Your detailed feedback on grammar, style, errors, tone, passive voice, repetition, and verbosity here>",
      "structure": "<Your detailed feedback on the logical flow, presence/absence of key sections, and organization here>",
      "clarity_and_coherence": "<Your detailed feedback on readability, transitions, smooth flow, and vague/ambiguous statements here>",
      "research_interests_strength": "<Your detailed feedback on clarity of research goals, alignment with background, and mention of specific institutional details (faculty/labs/projects) here>",
      "overall_rating": "<Select ONE option: Strong / Moderate / Needs Improvement>"
    }}


**In summary: Validate if the document is an SOP. If not, return the specific error JSON. If it is, analyze based on the four criteria and return the structured feedback JSON.**

"""

review_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",system),
       ("human", "Document to review :\n\n {sop_text}"),
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
    json_str = get_json_from_resp(output)
    clean_json = json.loads(json_str)
    return clean_json
    # output = output.strip("`").strip()
    # output = output.replace("json", "",1)

    # # convert to dict
    # clean_json = json.loads(output)

    # save to json remove later
    # with open("SOPReview/output.json", "w") as f:
    #    json.dump(clean_json, f, indent=4)
    
def get_json_from_resp(text: str):
    # Extract JSON block inside triple backticks
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)

    if match:
        json_str = match.group(1)
    else:
        # If no triple backtick block, try to extract bare JSON
        json_str = text.strip()

    # Convert to dict
    return json_str