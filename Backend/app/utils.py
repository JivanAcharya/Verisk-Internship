import logging

from typing import Any

from dataclasses import dataclass
from pathlib import Path

import emails
from jinja2 import Template
from app.core.config import settings
from AdaptiveRagChatbot.llm_config import llm
from langchain_core.prompts import ChatPromptTemplate

@dataclass
class EmailData:
    html_content: str
    subject : str


#for rendering email template
def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent / "email-templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


#email for new account
def generate_new_account_email(
    email_to: str, username: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"Welcome to {project_name}🎉"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            # "link": settings.FRONTEND_HOST,
            "link": "https://acharyajivan.com.np",
        },
    )
    return EmailData(html_content=html_content, subject=subject)


#function to send the actual email
def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, smtp=smtp_options)

    # print("\n ********  EMAIL SENT *********")
    # logger.info(f"send email result: {response}")

    
def rewrite_query(query: str, chat_context: str) -> str:
        """
        Function to rewrite the query using a large language model.
        
        Args:
            query (str): The original query to be rewritten.
        
        Returns:
            str: The rewritten query.
        """
        if chat_context is None:
            return query
        else:
            query_template = ChatPromptTemplate.from_messages([
                ("system",
                "You are query rewriting specialist for University Question and Answering application."
                " From the input of previous chat histroy and the human input, generate a clear query for the chat application. Donot make it more than two sentences."),
                ("system", "STRICTLY RESPOND WITH THE FINAL QUERY ONLY, IF THE CONTEXT DOES NOT SEEM RELEVANT DONOT REWRITE JUST RETURN THE QUERY AS IT IS, NO ADDITIONAL TEXT AND PREAMBLE."),
                ("system", f"Previous Chat History (for context, if relevant):\n{chat_context}"),
                ("human", "{input}")
            ])
            
            query = query_template.format(input= query)
            response = llm.invoke(query)
            new_query = response.content
            return new_query
