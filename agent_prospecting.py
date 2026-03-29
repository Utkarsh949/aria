"""
ARIA — Prospecting Agent
Researches targets, scores ICP fit, and writes personalised outreach sequences.
Renamed from prospecting_agent.py. All prompts live in config.py.
"""

import json
import re

from brain import AgentResult, LLMGateway
import config


class ProspectingAgent:
    NAME = "ProspectingAgent"

    def __init__(self, llm: LLMGateway):
        self.llm = llm

    async def run(self, company: str, role: str, extra: str = "") -> AgentResult:
        research   = await self._research(company, role, extra)
        score_raw  = await self._fit_score(research)
        sequence   = await self._outreach_sequence(research, score_raw)
        confidence = self._parse_confidence(score_raw)

        return AgentResult(
            agent=self.NAME,
            action="prospect_and_sequence",
            data={
                "company":          company,
                "target_role":      role,
                "research_summary": research,
                "fit_score":        score_raw,
                "outreach_sequence": sequence,
            },
            confidence=confidence,
            metadata={"extra_context": extra},
        )

    async def _research(self, company: str, role: str, extra: str) -> str:
        return await self.llm.complete(
            config.PROSPECTING_SYSTEM,
            config.prompt_prospect_research(company, role, extra),
        )

    async def _fit_score(self, research: str) -> str:
        return await self.llm.complete(
            config.PROSPECTING_SYSTEM,
            config.prompt_prospect_fit_score(research),
            temperature=0.3,
        )

    async def _outreach_sequence(self, research: str, score: str) -> dict:
        raw = await self.llm.complete(
            config.PROSPECTING_SYSTEM,
            config.prompt_prospect_sequence(research, score),
            temperature=0.8,
        )
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"raw": raw}

    def _parse_confidence(self, score_json: str) -> float:
        try:
            data = json.loads(score_json)
            return round(data.get("overall_score", 70) / 100, 2)
        except Exception:
            match = re.search(r'"overall_score"\s*:\s*(\d+)', score_json)
            return round(int(match.group(1)) / 100, 2) if match else 0.7
