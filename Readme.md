# 🎯 Agentic Lead Intelligence & Outreach Engine

An enterprise-ready multi-agent AI system that automates company research, extracts strategic pain points, and drafts personalized B2B cold outreach emails. Built with **LangGraph**, **Groq (Llama 3.3 70B)**, **FastAPI**, and **Streamlit**.

---

## 🏗️ Architecture

```
┌────────────────────────┐
│   User / Streamlit UI   │
└────────────┬─────────────┘
             │ HTTP POST
             ▼
┌────────────────────────┐
│    FastAPI REST API     │
└────────────┬─────────────┘
             │
             ▼
┌────────────────────────┐
│  LangGraph State Machine │
└────────────┬─────────────┘
             │
   ┌─────────┼─────────────┐
   ▼         ▼             ▼
[Researcher] [Analyst]  [Strategist]
   Node        Node         Node
```

| Node | Powered By | Responsibilities |
|---|---|---|
| **Researcher** | DuckDuckGo Live Search | Live business news, fault-tolerant `@retry` |
| **Analyst** | Llama-3 via Groq | Strategic priorities, decision-maker pains |
| **Strategist** | Llama-3 via Groq | High-converting hook, value proposition |

---

## ✨ Features

- **Multi-Agent Orchestration:** Structured state management using **LangGraph** (`Researcher` → `Analyst` → `Strategist`).
- **Live Web Grounding:** Eliminates hallucinations using live search results via `duckduckgo-search`.
- **Production Resilience:** Fault-tolerant network calls with exponential backoff and retry policies using **Tenacity**.
- **Decoupled Backend:** High-performance asynchronous **FastAPI** service with **Pydantic v2** data validation and interactive Swagger documentation (`/docs`).
- **Interactive Frontend:** Dual-column **Streamlit** dashboard with dedicated cards for insights, outreach copy, and raw payload inspection.

---

## 🛠️ Tech Stack

- **LLM:** Groq API (`llama-3.3-70b-versatile`)
- **Orchestration:** LangGraph, LangChain
- **Search Engine:** DuckDuckGo Search API
- **Backend:** FastAPI, Uvicorn, Pydantic
- **Frontend:** Streamlit
- **Resilience:** Tenacity

---

## 📁 Repository Structure

```text
lead-intelligence-saas/
├── app.py              # Streamlit interactive frontend
├── main.py              # FastAPI REST endpoint & schemas
├── graph.py              # LangGraph multi-agent workflow & retry logic
├── requirements.txt    # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore             # Git ignore rules for secrets & cache
└── README.md             # Documentation
```

---

## 🚀 Getting Started Locally

### 1. Prerequisites

- Python 3.10+
- Free [Groq Cloud API Key](https://console.groq.com/)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/lead-intelligence-saas.git
cd lead-intelligence-saas

# Create and activate a virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 4. Running the Application

**Step 1 — Start the FastAPI backend:**

```bash
uvicorn main:app --reload --port 8000
```

API docs will be available at `http://127.0.0.1:8000/docs`.

**Step 2 — Start the Streamlit frontend** (in a new terminal tab):

```bash
streamlit run app.py
```

Dashboard will be available at `http://localhost:8501`.

---

## 🌐 Cloud Deployment

- **Backend (FastAPI):** Deploy to [Render](https://render.com/) as a Web Service running `uvicorn main:app --host 0.0.0.0 --port 10000`, with `GROQ_API_KEY` set in the environment variables.
- **Frontend (Streamlit):** Deploy to [Streamlit Community Cloud](https://share.streamlit.io/), and set `BACKEND_API_URL` under app secrets.