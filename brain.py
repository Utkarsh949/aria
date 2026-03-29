"""
ARIA — Brain
Core LLM gateway and orchestrator engine.
Provider: Groq only.
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass, field

import httpx

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ARIA] %(levelname)s: %(message)s",
)
logger = logging.getLogger("aria.brain")


# ══════════════════════════════════════════════════════════════════════════════
# CONFIG DATACLASS
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class ARIAConfig:
    """Runtime configuration — reads from config.py which reads from env vars."""
    groq_api_key:   str   = field(default_factory=lambda: config.GROQ_API_KEY)
    crm_api_url:    str   = field(default_factory=lambda: config.CRM_API_URL)
    crm_api_key:    str   = field(default_factory=lambda: config.CRM_API_KEY)
    model_provider: str   = field(default_factory=lambda: config.MODEL_PROVIDER)
    model_name:     str   = field(default_factory=lambda: config.MODEL_NAME)
    max_tokens:     int   = field(default_factory=lambda: config.MAX_TOKENS)
    temperature:    float = field(default_factory=lambda: config.TEMPERATURE)


# ══════════════════════════════════════════════════════════════════════════════
# GROQ LLM GATEWAY
# ══════════════════════════════════════════════════════════════════════════════

class LLMGateway:
    """Sends completion requests to Groq's OpenAI-compatible API."""

    def __init__(self, cfg: ARIAConfig):
        self.cfg = cfg

    async def complete(self, system: str, user: str,
                       temperature: Optional[float] = None) -> str:
        temp  = temperature if temperature is not None else self.cfg.temperature
        model = self.cfg.model_name or "llama-3.3-70b-versatile"

        if not self.cfg.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Add it to config.py or set the GROQ_API_KEY environment variable. "
                "Get a free key at https://console.groq.com"
            )

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.cfg.groq_api_key}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model":      model,
                    "temperature": temp,
                    "max_tokens": self.cfg.max_tokens,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user",   "content": user},
                    ],
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]


# ══════════════════════════════════════════════════════════════════════════════
# AGENT RESULT
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class AgentResult:
    agent:      str
    action:     str
    data:       Any
    confidence: float
    timestamp:  str  = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata:   dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "agent":      self.agent,
            "action":     self.action,
            "data":       self.data,
            "confidence": self.confidence,
            "timestamp":  self.timestamp,
            "metadata":   self.metadata,
        }


# ══════════════════════════════════════════════════════════════════════════════
# ARIA ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

class ARIA:
    """
    ARIA — Autonomous Revenue Intelligence Agent.
    Orchestrates four specialist sub-agents powered by Groq.
    """

    def __init__(self, cfg: Optional[ARIAConfig] = None):
        self.cfg = cfg or ARIAConfig()
        self.llm = LLMGateway(self.cfg)
        logger.info(
            "ARIA initialised — provider=groq  model=%s",
            self.cfg.model_name,
        )

    async def chat(self, message: str, context: Optional[dict] = None) -> str:
        ctx = f"\n\nContext: {json.dumps(context)}" if context else ""
        return await self.llm.complete(
            config.ARIA_SYSTEM_PROMPT,
            message + ctx,
        )

    async def prospect(self, company: str, role: str, extra: str = "") -> AgentResult:
        from agent_prospecting import ProspectingAgent
        return await ProspectingAgent(self.llm).run(company=company, role=role, extra=extra)

    async def deal_intelligence(self, deal: dict) -> AgentResult:
        from agent_deals import DealIntelligenceAgent
        return await DealIntelligenceAgent(self.llm).run(deal=deal)

    async def retention(self, account: dict) -> AgentResult:
        from agent_retention import RetentionAgent
        return await RetentionAgent(self.llm).run(account=account)

    async def competitive_intel(self, deal_context: dict, competitor: str) -> AgentResult:
        from agent_competitive import CompetitiveAgent
        return await CompetitiveAgent(self.llm).run(
            deal_context=deal_context, competitor=competitor
        )

    async def full_pipeline_audit(self, pipeline: list[dict]) -> list[AgentResult]:
        from agent_deals import DealIntelligenceAgent
        agent = DealIntelligenceAgent(self.llm)
        return await asyncio.gather(*[agent.run(deal=d) for d in pipeline])
