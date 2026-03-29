"""
ARIA — Central Configuration
All AI model settings, system prompts, and prompt templates live here.
Edit this file to change ARIA's behaviour, tone, or model without
touching any agent or server code.

Provider: Groq only.
Get a free key at https://console.groq.com
"""

import os
import json

# ══════════════════════════════════════════════════════════════════════════════
# MODEL / API SETTINGS
# ══════════════════════════════════════════════════════════════════════════════

# Provider is fixed to Groq
MODEL_PROVIDER = "groq"

# Groq model — change to any Groq-supported model:
#   llama-3.3-70b-versatile  (default, best quality)
#   llama-3.1-8b-instant     (fastest)
#   mixtral-8x7b-32768       (long context)
#   gemma2-9b-it
MODEL_NAME  = os.getenv("MODEL_NAME",    "llama-3.3-70b-versatile")
MAX_TOKENS  = int(os.getenv("MAX_TOKENS",    "2048"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# ── Groq API key ──────────────────────────────────────────────────────────────
# Set via environment variable OR paste your key directly as the default value.
# Get your free key at: https://console.groq.com
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")   # e.g.  gsk_xxxxxxxxxxxxxxxxxxxx

# ── CRM connection (optional) ─────────────────────────────────────────────────
CRM_API_URL  = os.getenv("CRM_API_URL",  "")
CRM_API_KEY  = os.getenv("CRM_API_KEY",  "")
CRM_PLATFORM = os.getenv("CRM_PLATFORM", "generic")  # hubspot | salesforce | generic

HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN", "")
SF_INSTANCE_URL      = os.getenv("SF_INSTANCE_URL",      "")
SF_ACCESS_TOKEN      = os.getenv("SF_ACCESS_TOKEN",      "")

# ── Server auth ───────────────────────────────────────────────────────────────
ARIA_API_KEYS = set(filter(None, os.getenv("ARIA_API_KEYS", "aria-demo-key").split(",")))

# ── UI server ─────────────────────────────────────────────────────────────────
UI_HOST      = os.getenv("ARIA_UI_HOST", "127.0.0.1")
UI_PORT      = int(os.getenv("ARIA_UI_PORT", "8000"))
ARIA_UI_PATH = os.getenv("ARIA_UI_PATH", "")


# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

ARIA_SYSTEM_PROMPT = """You are ARIA — Autonomous Revenue Intelligence Agent.
You are a world-class AI sales strategist embedded inside CRM and communication systems.
Your personality: sharp, empathetic, data-driven, and human. Never robotic.

You help sales teams by:
- Researching and qualifying prospects with precision
- Writing highly personalised outreach that feels human
- Detecting deal risk before it becomes deal loss
- Predicting churn and triggering retention plays
- Tracking competitive signals and updating battlecards

Always respond with specific, actionable, and evidence-based insights.
Be concise but never shallow. Be bold but never reckless.
Format structured output as JSON when requested."""

PROSPECTING_SYSTEM = """You are ARIA's Prospecting Intelligence engine.
You research B2B targets with the precision of a top-tier SDR and the empathy of a trusted advisor.
Always produce warm, specific, non-generic outreach. Reference real pain points. Sound human.
When asked for JSON, return ONLY valid JSON — no markdown fences."""

DEAL_SYSTEM = """You are ARIA's Deal Intelligence engine.
You think like a seasoned enterprise sales director who has closed thousands of deals.
You read between the lines — a missed meeting, a new stakeholder, a delayed POC all mean something.
You generate recovery plays that are specific, human, and executable TODAY.
Return ONLY valid JSON when asked for JSON. No markdown fences."""

RETENTION_SYSTEM = """You are ARIA's Revenue Retention engine.
You think like a best-in-class Customer Success Director who can see churn coming months away.
You interpret usage data, support tickets, NPS, and stakeholder signals to predict risk.
Your interventions are warm, proactive, and customer-centric — never panicked or desperate.
Return ONLY valid JSON when asked for JSON. No markdown fences."""

COMPETITIVE_SYSTEM = """You are ARIA's Competitive Intelligence engine.
You think like a product marketer who lives inside the sales trenches.
You know every competitor's weaknesses, messaging, and sales tactics.
You produce crisp, usable battlecards — not vague platitudes.
Every talking point must be specific, defensible, and easy to deliver in a call.
Return ONLY valid JSON when asked for JSON. No markdown fences."""


# ══════════════════════════════════════════════════════════════════════════════
# DEAL INTELLIGENCE — RISK WEIGHTS
# ══════════════════════════════════════════════════════════════════════════════

DEAL_RISK_WEIGHTS = {
    "no_engagement_7d":     25,
    "competitor_mentioned": 20,
    "champion_left":        30,
    "budget_freeze_signal": 25,
    "delayed_decision":     15,
    "negative_sentiment":   20,
    "poc_stalled":          20,
    "legal_hold":           15,
}

DEAL_STAGE_BONUS = {
    "closed_won":   0,
    "negotiation":  5,
    "proposal":     0,
    "discovery":   -5,
    "prospecting": -10,
}

DEAL_SEVERITY_PENALTY = {
    "low":      5,
    "medium":  12,
    "high":    20,
    "critical": 30,
}


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def prompt_prospect_research(company: str, role: str, extra: str) -> str:
    return f"""Research this prospect deeply:
Company: {company}
Target role: {role}
Additional context: {extra or 'None'}

Produce a structured research brief covering:
1. Company overview (size, industry, stage, funding if known)
2. Likely pain points for a {role} right now
3. Recent news or signals that create urgency
4. Key decision criteria for this type of buyer
5. Tone and language this persona responds to

Be specific. No fluff."""


def prompt_prospect_fit_score(research: str) -> str:
    return f"""Based on this research brief, return a JSON fit score:

{research}

Return ONLY this JSON:
{{
  "overall_score": <0-100>,
  "icp_match": <0-100>,
  "urgency": <0-100>,
  "budget_likelihood": <0-100>,
  "decision_maker_access": <0-100>,
  "rationale": "<2-3 sentence explanation>",
  "recommended_approach": "<direct / nurture / pass>"
}}"""


def prompt_prospect_sequence(research: str, score: str) -> str:
    return f"""Using this research and fit score, write a 3-touch outreach sequence.

Research:
{research}

Score:
{score}

Return ONLY this JSON:
{{
  "touch_1": {{
    "channel": "email",
    "subject": "<compelling subject line>",
    "body": "<personalised email body — warm, specific, under 120 words>",
    "send_delay_hours": 0
  }},
  "touch_2": {{
    "channel": "linkedin",
    "message": "<LinkedIn connection message — under 60 words>",
    "send_delay_hours": 48
  }},
  "touch_3": {{
    "channel": "email",
    "subject": "<follow-up subject>",
    "body": "<value-add follow-up — reference a specific insight, under 100 words>",
    "send_delay_hours": 120
  }},
  "personalization_hooks": ["<hook 1>", "<hook 2>", "<hook 3>"]
}}"""


def prompt_deal_risk(deal: dict) -> str:
    return f"""Analyse this deal for risk signals:

{json.dumps(deal, indent=2)}

Identify ALL present risk signals. Return ONLY this JSON:
{{
  "signals_detected": [
    {{
      "signal": "<signal name>",
      "severity": "<low|medium|high|critical>",
      "evidence": "<what in the deal data suggests this>",
      "days_until_impact": <integer>
    }}
  ],
  "primary_risk": "<single biggest threat to this deal>",
  "stakeholder_health": "<champion_strong|champion_weak|no_champion|unknown>",
  "engagement_trend": "<increasing|stable|declining|dead>",
  "competitor_threat_level": "<none|low|medium|high>"
}}"""


def prompt_deal_recovery(deal: dict, risk_profile: dict, health: int, urgency: str) -> str:
    return f"""Generate a recovery play for this deal.
Health score: {health}/100 — {urgency}

Deal: {json.dumps(deal, indent=2)}
Risk profile: {json.dumps(risk_profile, indent=2)}

Return ONLY this JSON:
{{
  "play_type": "<re-engage|neutralise_competitor|rebuild_champion|accelerate_close|rescue>",
  "urgency": "{urgency}",
  "primary_action": {{
    "what": "<specific action>",
    "who": "<who should take it>",
    "when": "<specific timing>",
    "channel": "<email|call|meeting|linkedin|exec_outreach>"
  }},
  "talking_points": [
    "<specific talking point 1 — reference deal context>",
    "<specific talking point 2>",
    "<specific talking point 3>"
  ],
  "email_template": {{
    "subject": "<subject line>",
    "body": "<personalised re-engagement email — under 150 words, warm and direct>"
  }},
  "success_metric": "<how to know this play worked>",
  "escalate_to_exec": <true|false>
}}"""


def prompt_deal_forecast(deal: dict, health: int, adjusted_prob: float) -> str:
    return f"""Given this deal and a health score of {health}/100, provide a close forecast.

Deal: {json.dumps(deal, indent=2)}
Adjusted win probability: {adjusted_prob}%

Return ONLY this JSON:
{{
  "win_probability": {adjusted_prob},
  "predicted_close_date": "<ISO date or 'unknown'>",
  "expected_value": <number>,
  "confidence_band": "<±X%>",
  "key_next_milestone": "<what must happen next for this deal to advance>",
  "risk_adjusted_value": <number>
}}"""


def prompt_retention_churn(account: dict) -> str:
    return f"""Analyse this account for churn risk:

{json.dumps(account, indent=2)}

Consider: login frequency, feature adoption, support ticket volume and sentiment,
NPS score, stakeholder changes, contract renewal date, payment history.

Return ONLY this JSON:
{{
  "churn_risk_score": <0-100>,
  "risk_tier": "<critical|high|medium|low|healthy>",
  "primary_churn_driver": "<single biggest reason>",
  "churn_signals": [
    {{
      "signal": "<signal name>",
      "weight": <1-10>,
      "observation": "<what the data shows>"
    }}
  ],
  "positive_signals": ["<green flag 1>", "<green flag 2>"],
  "days_to_renewal": <integer or null>,
  "sentiment_trend": "<improving|stable|declining|unknown>",
  "health_category": "<champion_engaged|passive_user|at_risk|ghost>"
}}"""


def prompt_retention_intervention(account: dict, churn_analysis: dict,
                                   risk: int, strategy: str) -> str:
    return f"""Build a retention intervention plan.
Strategy: {strategy}
Churn risk: {risk}/100

Account: {json.dumps(account, indent=2)}
Risk analysis: {json.dumps(churn_analysis, indent=2)}

Return ONLY this JSON:
{{
  "strategy": "{strategy}",
  "interventions": [
    {{
      "action": "<specific action>",
      "owner": "<csm|exec|product|support>",
      "timing": "<immediate|this_week|this_month>",
      "channel": "<call|email|qbr|in_person|in_app>"
    }}
  ],
  "outreach_email": {{
    "to": "<champion name or title>",
    "subject": "<subject>",
    "body": "<warm, proactive email — under 150 words, not sales-y>"
  }},
  "offer_levers": ["<lever 1 if needed>", "<lever 2>"],
  "escalate_to_exec": <true|false>,
  "success_criteria": "<what does retention look like in 30 days>",
  "30_day_plan": ["<week 1 action>", "<week 2 action>", "<week 3 action>", "<week 4 action>"]
}}"""


def prompt_retention_expansion(account: dict) -> str:
    return f"""Identify expansion revenue opportunities for this account:

{json.dumps(account, indent=2)}

Return ONLY this JSON:
{{
  "expansion_score": <0-100>,
  "opportunities": [
    {{
      "type": "<upsell|cross_sell|seat_expansion|new_use_case>",
      "description": "<specific opportunity>",
      "estimated_arr_increase": "<$X or X%>",
      "readiness": "<ready_now|in_60_days|in_180_days>"
    }}
  ],
  "recommended_timing": "<when to introduce expansion conversation>",
  "expansion_hook": "<one compelling reason to expand now>"
}}"""


def prompt_competitive_battlecard(deal: dict, competitor: str) -> str:
    return f"""Generate a competitive battlecard for this deal against {competitor}.

Deal context: {json.dumps(deal, indent=2)}

Return ONLY this JSON:
{{
  "competitor": "{competitor}",
  "our_strengths_vs_them": [
    {{"point": "<strength>", "proof": "<evidence or customer example>"}},
    {{"point": "<strength>", "proof": "<evidence>"}},
    {{"point": "<strength>", "proof": "<evidence>"}}
  ],
  "their_weaknesses": [
    {{"weakness": "<gap>", "how_to_surface": "<question or tactic to expose this>"}},
    {{"weakness": "<gap>", "how_to_surface": "<tactic>"}},
    {{"weakness": "<gap>", "how_to_surface": "<tactic>"}}
  ],
  "landmines": [
    "<question to plant doubt about competitor — phrased neutrally>",
    "<question 2>",
    "<question 3>"
  ],
  "their_likely_attacks": [
    {{"attack": "<what they'll say about us>", "response": "<our rebuttal>"}}
  ],
  "win_themes": ["<theme 1>", "<theme 2>", "<theme 3>"],
  "trap_setting_questions": [
    "<discovery question that surfaces our advantage>",
    "<question 2>"
  ]
}}"""


def prompt_competitive_positioning(deal: dict, competitor: str) -> str:
    return f"""Given that {competitor} is now in this deal, update our positioning.

Deal context: {json.dumps(deal, indent=2)}

Return ONLY this JSON:
{{
  "headline_message": "<single most important thing to communicate now>",
  "repositioning_narrative": "<2-3 sentence narrative shift to use in next call>",
  "proof_points": ["<specific proof point>", "<proof point 2>", "<proof point 3>"],
  "demo_focus": "<what to demo or emphasise given this competitor>",
  "avoid_saying": ["<message that plays into competitor's hands>"],
  "executive_hook": "<why the economic buyer should care about us vs them>"
}}"""


def prompt_competitive_email(deal: dict, competitor: str, key_strength: str) -> str:
    return f"""Write a subtle competitive re-engagement email for this deal where {competitor} is involved.
Do NOT mention the competitor by name. Reinforce our differentiated value.
Key strength to lead with: {key_strength}

Deal context: {json.dumps(deal, indent=2)}

Return ONLY this JSON:
{{
  "subject": "<subject line>",
  "body": "<email body — under 120 words, confident but not arrogant, human>",
  "p_s": "<optional P.S. that subtly plants a seed of doubt about alternatives>"
}}"""
