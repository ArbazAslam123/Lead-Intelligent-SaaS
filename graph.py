from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from duckduckgo_search import DDGS
import os 
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import SecretStr
from typer import prompt
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type




load_dotenv()

class AgentState(TypedDict):
    company_name: str
    target_role: str
    research_data: str
    insights: str
    email_draft: str


#Building a helper function to fetch live data from the web

@retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
)

def search_company(company_name: str) -> str:
    ddgs= DDGS()
    query= f"{company_name} company news initiatives challenges"
    results= ddgs.text(query, max_results=3)

    if not results:
        raise ValueError("Search returned no results")

    raw_text= "\n".join([f"{r['title']}: {r['body']}" for r in results])
    return raw_text


# Node:1 The Researcher Agent Node

def researcher_node(state: AgentState) -> dict:
    target_company= state["company_name"]
    search_results= search_company(target_company)
    return {'research_data': search_results}



api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(api_key=SecretStr(api_key) if api_key is not None else None, model="openai/gpt-oss-120b")

# Node:2 The Analyst Agent Node

def analyst_node(state: AgentState) -> dict:
    # Read input data from the state

    r_data= state["research_data"]
    t_role= state["target_role"]
    c_name= state["company_name"]

    # Constructing the Prompt for the LLM
    prompt=f"""
    You are an expert Business Analyst.
    Analyze the following research on {c_name} for reaching out to a {t_role}.

    Research Data:
    {r_data}

    Extract:
    1. Key bussiness priorities  or recent initiatives.
    2. Potential pain points relevant to a {t_role}.
    Keep it concise (3-4 bullet points).

"""
    
    # Calling the LLM to analyze the research data
    response=llm.invoke(prompt)

    return {"insights":response.content}


# Node:3 The Email Drafting Agent Node ( The Strategist Agent)

def strategist_node(state: AgentState) -> dict:

    # Extract the needed fields
    c_name= state["company_name"]
    t_role= state["target_role"]
    insights= state["insights"]

    # Constructing the Email Prompt for the LLM
    prompt=f"""
    You are an elite B2B cold email strategist.
    Write a concise (under 120 words), high-converting cold email to the {t_role} at {c_name}.

    Use these researched insights to personalize the hook:
    {insights}

    Structure:
    - Personalized observation/hook based on the insights.
    - Value proposition (how AI automation helps their exact bottleneck).
    - soft call to action (e.g., open to a 5-minute chat?).
"""
    
    response=llm.invoke(prompt)
    return {"email_draft": response.content}


# Linking the nodes together to form a state graph

workflow= StateGraph(AgentState)

# Register all nodes (give each a name and function)
workflow.add_node("researcher",researcher_node)
workflow.add_node("analyst",analyst_node)
workflow.add_node("strategist",strategist_node)

# Connects the nodes with directed edges

workflow.add_edge(START,"researcher")
workflow.add_edge("researcher","analyst")
workflow.add_edge("analyst","strategist")
workflow.add_edge("strategist",END)

# Compile into  a runnable engine
lead_engine= workflow.compile()


# Executing the Engine

initial_input= {
    'company_name':"Shopify",
    'target_role': "VP of Customer Support"
}

# Run the pipeline

final_output= lead_engine.invoke(initial_input)

print("--- RESEARCH DATA ---")
print(final_output["research_data"])

print("\n--- INSIGHTS ---")
print(final_output["insights"])

print("\n--- EMAIL DRAFT ---")
print(final_output["email_draft"])