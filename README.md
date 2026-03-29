# ARIA — Autonomous Revenue Intelligence Agent
> *"Your AI sales co-pilot — from first touch to closed-won."*

## Quick Start
```bash
pip install -r requirements.txt
cp .env.example .env   # add your API key
python aria_cli.py --demo         # full demo
uvicorn api_server:app --port 8000  # REST server
```

## Files
| File | Purpose |
|---|---|
| `aria_core.py` | Orchestrator + universal LLM gateway (Anthropic/OpenAI/Google) |
| `api_server.py` | FastAPI REST API with auth + webhooks |
| `aria_cli.py` | Interactive terminal CLI |
| `aria/agents/prospecting_agent.py` | Research, fit scoring, outreach sequences |
| `aria/agents/deal_intelligence_agent.py` | Risk detection, health scoring, recovery plays |
| `aria/agents/retention_agent.py` | Churn prediction, intervention workflows |
| `aria/agents/competitive_agent.py` | Battlecards, positioning, competitive emails |
| `aria/integrations/crm_connector.py` | HubSpot + Salesforce + Generic REST adapters |

## Switch AI Provider
```bash
MODEL_PROVIDER=anthropic  ANTHROPIC_API_KEY=sk-ant-...  MODEL_NAME=claude-opus-4-5
MODEL_PROVIDER=openai     OPENAI_API_KEY=sk-...          MODEL_NAME=gpt-4o
MODEL_PROVIDER=google     GOOGLE_API_KEY=AIza...         MODEL_NAME=gemini-1.5-pro
```

## API Endpoints
- `POST /chat` — Conversational interface
- `POST /prospect` — Research + outreach sequence
- `POST /deal/analyse` — Deal risk + recovery play
- `POST /pipeline/audit` — Full pipeline health check
- `POST /retention/analyse` — Churn prediction + intervention
- `POST /competitive/battlecard` — Live battlecard generation
- `POST /webhook/crm` — CRM event webhook (auto-triggers agents)
