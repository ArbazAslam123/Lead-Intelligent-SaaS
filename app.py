import streamlit as st
import requests

# 1. Page Configuration
st.set_page_config(
    page_title="Lead Intel Agent SaaS",
    page_icon="🎯",
    layout="wide"
)

# 2. Header Section
st.title("🎯 Agentic Lead Intelligence & Outreach")
st.markdown("Autonomous research and personalized cold outreach powered by LangGraph & Groq.")

# 3. Input Controls (Sidebar or Form)
with st.form("lead_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input(
            label="Target Company",
            placeholder="e.g., Notion, Stripe, Shopify",
            help="The company you want the AI agents to research."
        )
        
    with col2:
        target_role = st.text_input(
            label="Target Role / Decision Maker",
            placeholder="e.g., Head of Operations, VP of Sales",
            help="The specific title of the person you plan to email."
        )
        
    submit_button = st.form_submit_button("⚡ Run Agent Pipeline", use_container_width=True)

# 4. Execution & Display Logic
if submit_button:
    if not company_name or not target_role:
        st.warning("Please provide both a company name and a target role.")
    else:
        # Backend API URL
        API_URL = "http://127.0.0.1:8000/generate-lead-intel"
        payload = {
            "company_name": company_name.strip(),
            "target_role": target_role.strip()
        }
        
        with st.spinner("Agents are researching the web and drafting strategy..."):
            try:
                response = requests.post(API_URL, json=payload, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success("Pipeline completed successfully!")
                    
                    # Box 1: Extracted Insights
                    st.subheader("💡 Strategic Insights (Analyst Agent)")
                    with st.container(border=True):
                        st.markdown(data["insights"])
                    
                    # Box 2: Cold Email Draft
                    st.subheader("✉️ Personalized Cold Email (Strategist Agent)")
                    with st.container(border=True):
                        st.markdown(data["email_draft"])
                        
                    # Box 3: Raw Research Data (Collapsible)
                    with st.expander("🔍 View Raw Research Data (Researcher Agent)"):
                        st.text(data["research_data"])
                        
                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI backend. Make sure Uvicorn is running on http://127.0.0.1:8000.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")