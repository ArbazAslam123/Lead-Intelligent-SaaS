from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from graph import lead_engine


# using Pydantic to define what valid incoming and outgoing data look like.
class LeadRequest(BaseModel):
    # user must send in the POST body
    company_name: str = Field(..., description="Target company name", examples=["stripe"])
    target_role: str = Field(..., description="Target decision maker", examples=["Head of Growth"])

class LeadResponse(BaseModel):
    # API promises to return
    company_name: str
    target_role: str
    research_data: str
    insights: str
    email_draft: str

app = FastAPI(
    title= "Agentic Lead Intelligence API",
    version= "1.0.0",
    description= " Autonomous multi-agent research and cold outreach pipeline."
)

@app.post("/generate-lead-intel", response_model=LeadResponse)
def generate_lead_intel(request: LeadRequest):
    try:
        # Package the request data for LangGraph  
        initial_input = {
        "company_name": request.company_name,
        "target_role": request.target_role
    }
        
        # Run the LangGraph pipeline
        result = lead_engine.invoke(initial_input)

        # Format and return the validated response
        return LeadResponse(
        company_name=result["company_name"],
        target_role=result["target_role"],
        research_data=result["research_data"],
        insights=result["insights"],
        email_draft=result["email_draft"]
    )
    
    except Exception as e:
        # Handle unexpected runtime errors gracefully
        raise HTTPException(status_code=500, detail=str(e))

