import os
import streamlit as st
import requests

# 1. Page Configuration
st.set_page_config(
    page_title="Lead Intel Agent SaaS",
    page_icon="🎯",
    layout="wide"
)

# 2. Dynamic API URL Resolution
# Checks Streamlit Secrets -> Environment Variables -> Localhost fallback
DEFAULT_URL = "http://127.0.0.1:8000/generate-lead-intel"
if "BACKEND_API_URL" in st.secrets:
    API_URL = st.secrets["BACKEND_API_URL"]
else:
    API_URL = os.getenv("BACKEND_API_URL", DEFAULT_URL)

# 3. Header Section
st.title("🎯 Agentic Lead Intelligence & Outreach")
st.markdown("Autonomous research and personalized cold outreach powered by LangGraph & Groq.")

# 4. Input Form
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

# 5. Execution & Display Logic
if submit_button:
    if not company_name.strip() or not target_role.strip():
        st.warning("Please provide both a company name and a target role.")
    else:
        payload = {
            "company_name": company_name.strip(),
            "target_role": target_role.strip()
        }
        
        with st.spinner("Agents are researching the web and drafting strategy... (May take 30-50s if backend is waking up)"):
            try:
                # 120s timeout handles Render free-tier cold starts
                response = requests.post(API_URL, json=payload, timeout=120)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Pipeline completed successfully!")
                    
                    # Box 1: Extracted Insights
                    st.subheader("💡 Strategic Insights (Analyst Agent)")
                    with st.container(border=True):
                        st.markdown(data.get("insights", "No insights generated."))
                    
                    # Box 2: Cold Email Draft
                    st.subheader("✉️ Personalized Cold Email (Strategist Agent)")
                    with st.container(border=True):
                        st.markdown(data.get("email_draft", "No email draft generated."))
                        
                    # Box 3: Raw Research Data (Collapsible)
                    with st.expander("🔍 View Raw Research Data (Researcher Agent)"):
                        st.text(data.get("research_data", "No raw search data available."))
                        
                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")
                    
            except requests.exceptions.Timeout:
                st.error("The request timed out. If your backend is hosted on Render's free tier, it may be waking up from sleep. Please try submitting once more.")
            except requests.exceptions.ConnectionError:
                st.error(f"Could not connect to the backend at `{API_URL}`. Ensure your FastAPI server is live and the URL is configured properly.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")