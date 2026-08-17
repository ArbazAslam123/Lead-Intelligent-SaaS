from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from duckduckgo_search import DDGS
import os 
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from pydantic import SecretStr
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

class AgentState(TypedDict):
    company_name: str
    target_role: str
    research_data: str
    insights: str
    email_draft: str

# Building a resilient helper function
@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=2, max=6),
    reraise=False  # Do not crash the API if search fails
)
def search_company(company_name: str) -> str:
    try:
        ddgs = DDGS()
        query = f"{company_name} company news initiatives challenges"
        # Convert the generator to a list to ensure we actually fetched data
        results = list(ddgs.text(query, max_results=3))

        # Fallback to a simpler query if the detailed one fails
        if not results:
            results = list(ddgs.text(company_name, max_results=3))

        if results:
            raw_text = "\n".join([f"- {r.get('title', '')}: {r.get('body', '')}" for r in results])
            return raw_text
            
    except Exception as e:
        print(f"Search warning: {e}")
        
    # Safe Fallback: Pass context to the LLM instead of crashing
    return f"Live search data unavailable for {company_name}. Rely on pre-trained enterprise business knowledge."


# Node 1: The Researcher Agent Node
def researcher_node(state: AgentState) -> dict:
    target_company = state["company_name"]
    search_results = search_company(target_company)
    return {'research_data': search_results}


# Fixed Model Initialization
api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(
    api_key=SecretStr(api_key) if api_key is not None else None, 
    model="llama-3.3-70b-versatile"  # Used the correct Groq model
)

# Node 2: The Analyst Agent Node
def analyst_node(state: AgentState) -> dict:
    # Read input data from the state
    r_data = state["research_data"]
    t_role = state["target_role"]
    c_name = state["company_name"]

    # Constructing the Prompt for the LLM
    prompt = f"""
    You are an expert Business Analyst.
    Analyze the following research on {c_name} for reaching out to a {t_role}.

    Research Data:
    {r_data}

    Extract:
    1. Key business priorities or recent initiatives.
    2. Potential pain points relevant to a {t_role}.
    Keep it concise (3-4 bullet points).
    """
    
    # Calling the LLM to analyze the research data
    response = llm.invoke(prompt)
    return {"insights": response.content}


# Node 3: The Email Drafting Agent Node (The Strategist Agent)
def strategist_node(state: AgentState) -> dict:
    # Extract the needed fields
    c_name = state["company_name"]
    t_role = state["target_role"]
    insights = state["insights"]

    # Constructing the Email Prompt for the LLM
    prompt = f"""
    You are an elite B2B cold email strategist.
    Write a concise (under 120 words), high-converting cold email to the {t_role} at {c_name}.

    Use these researched insights to personalize the hook:
    {insights}

    Structure:
    - Personalized observation/hook based on the insights.
    - Value proposition (how AI automation helps their exact bottleneck).
    - Soft call to action (e.g., open to a 5-minute chat?).
    """
    
    response = llm.invoke(prompt)
    return {"email_draft": response.content}


# Linking the nodes together to form a state graph
workflow = StateGraph(AgentState)

# Register all nodes
workflow.add_node("researcher", researcher_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("strategist", strategist_node)

# Connect the nodes with directed edges
workflow.add_edge(START, "researcher")
workflow.add_edge("researcher", "analyst")
workflow.add_edge("analyst", "strategist")
workflow.add_edge("strategist", END)

# Compile into a runnable engine
lead_engine = workflow.compile()