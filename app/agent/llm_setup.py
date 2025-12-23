from langchain_google_genai import ChatGoogleGenerativeAI
from app.agent.tools import create_task, query_tasks, update_task
import os

def get_llm():
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    
    tools = [create_task, query_tasks, update_task]
    llm_with_tools = llm.bind_tools(tools)
    return llm_with_tools, tools
