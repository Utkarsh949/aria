<div align="center">

# 🤖 ARIA
### Autonomous Revenue Intelligence Agent

*Your AI-powered sales co-pilot — from first touch to closed-won.*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Powered%20by-Groq-orange?style=for-the-badge&logo=lightning&logoColor=white)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## ✨ What is ARIA?

ARIA is a multi-agent AI system that automates the most time-consuming parts of sales — researching prospects, monitoring deal health, predicting churn, and generating competitive battlecards. Powered by **Groq's ultra-fast inference**, everything runs locally on your machine with a clean browser dashboard.

---

## 🚀 Quick Start (3 steps)

### 1. Clone the repo

```bash
git clone https://github.com/Utkarsh949/aria.git
cd aria
```

### 2. Create a virtual environment and install dependencies

```bash
# Create venv
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Run ARIA

```bash
python aria.py
```

ARIA will open the browser dashboard automatically. On first run, it will ask for your **Groq API Key** in the UI — just paste it and you're good to go.

> 🔑 Get a free Groq API key at [console.groq.com](https://console.groq.com)

---

## 🧠 Agents

| Agent | What it does |
|---|---|
| 🔍 **Prospecting Agent** | Researches target companies, scores ICP fit, writes personalised outreach sequences |
| 📊 **Deal Intelligence Agent** | Detects risk signals, calculates health scores, generates recovery plays |
| 🔒 **Retention Agent** | Predicts churn risk, builds intervention plans, finds expansion opportunities |
| ⚔️ **Competitive Agent** | Creates live battlecards, positioning updates, and competitive re-engagement emails |

---

## 📁 Project Structure

```
aria/
├── aria.py                  # 🚀 Launcher — run this
├── server.py                # FastAPI server + dashboard
├── brain.py                 # LLM gateway + ARIA orchestrator
├── config.py                # All settings and prompts
├── crm.py                   # CRM connector (HubSpot / Salesforce)
├── agent_prospecting.py     # Prospecting agent
├── agent_deals.py           # Deal intelligence agent
├── agent_retention.py       # Retention agent
├── agent_competitive.py     # Competitive intelligence agent
├── dashboard.html           # Browser UI
└── requirements.txt         # Dependencies
```

---

## 🌐 API Endpoints

Once running, full interactive docs available at `http://localhost:8000/docs`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Conversational interface |
| `POST` | `/prospect` | Research + outreach sequence |
| `POST` | `/deal/analyse` | Deal risk + recovery play |
| `POST` | `/pipeline/audit` | Full pipeline health check |
| `POST` | `/retention/analyse` | Churn prediction + intervention |
| `POST` | `/competitive/battlecard` | Live battlecard generation |

---

## 🛠️ Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com)** — REST API framework
- **[Groq](https://groq.com)** — Ultra-fast LLM inference (Llama 3.3 70B)
- **[httpx](https://www.python-httpx.org)** — Async HTTP client
- **[Pydantic](https://docs.pydantic.dev)** — Data validation
- **[Uvicorn](https://www.uvicorn.org)** — ASGI server

---

<div align="center">

Made with ❤️ by [Utkarsh949](https://github.com/Utkarsh949)

</div>
