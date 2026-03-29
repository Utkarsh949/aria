"""
ARIA — Competitive Intelligence Agent
Generates battlecards, positioning updates, and competitive re-engagement emails.
Renamed from competitive_agent.py. All prompts live in config.py.
"""

import json

from brain import AgentResult, LLMGateway
import config


class CompetitiveAgent:
    NAME = "CompetitiveAgent"

    def __init__(self, llm: LLMGateway):
        self.llm = llm

    async def run(self, deal_context: dict, competitor: str) -> AgentResult:
        battlecard  = await self._generate_battlecard(deal_context, competitor)
        positioning = await self._positioning_update(deal_context, competitor)
        email_nudge = await self._competitive_email(deal_context, competitor, battlecard)

        return AgentResult(
            agent=self.NAME,
            action="competitive_intelligence",
            data={
                "deal_id":     deal_context.get("id", "unknown"),
                "competitor":  competitor,
                "battlecard":  battlecard,
                "positioning": positioning,
                "email_nudge": email_nudge,
            },
            confidence=0.82,
            metadata={"deal_stage": deal_context.get("stage", "")},
        )

    async def _generate_battlecard(self, deal: dict, competitor: str) -> dict:
        raw = await self.llm.complete(
            config.COMPETITIVE_SYSTEM,
            config.prompt_competitive_battlecard(deal, competitor),
            temperature=0.5,
        )
        try:
            return json.loads(raw)
        except Exception:
            return {"raw": raw}

    async def _positioning_update(self, deal: dict, competitor: str) -> dict:
        raw = await self.llm.complete(
            config.COMPETITIVE_SYSTEM,
            config.prompt_competitive_positioning(deal, competitor),
            temperature=0.6,
        )
        try:
            return json.loads(raw)
        except Exception:
            return {"raw": raw}

    async def _competitive_email(self, deal: dict, competitor: str,
                                  battlecard: dict) -> dict:
        # Pull the top strength to anchor the email on
        key_strength = ""
        strengths = battlecard.get("our_strengths_vs_them", [])
        if strengths and isinstance(strengths, list):
            first = strengths[0]
            key_strength = (
                first.get("point", "") if isinstance(first, dict) else str(first)
            )

        raw = await self.llm.complete(
            config.COMPETITIVE_SYSTEM,
            config.prompt_competitive_email(deal, competitor, key_strength),
            temperature=0.8,
        )
        try:
            return json.loads(raw)
        except Exception:
            return {"raw": raw}
