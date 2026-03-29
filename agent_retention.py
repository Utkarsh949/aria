"""
ARIA — Retention Agent
Predicts churn risk, builds intervention plans, and finds expansion opportunities.
Renamed from retention_agent.py. All prompts live in config.py.
"""

import json

from brain import AgentResult, LLMGateway
import config


class RetentionAgent:
    NAME = "RetentionAgent"

    def __init__(self, llm: LLMGateway):
        self.llm = llm

    async def run(self, account: dict) -> AgentResult:
        churn_analysis = await self._predict_churn(account)
        churn_score    = self._extract_churn_score(churn_analysis)
        intervention   = await self._build_intervention(account, churn_analysis)
        expansion_opps = await self._find_expansion(account)

        return AgentResult(
            agent=self.NAME,
            action="retention_analysis",
            data={
                "account_id":              account.get("id", "unknown"),
                "account_name":            account.get("name", ""),
                "churn_risk_score":        churn_score,
                "churn_analysis":          churn_analysis,
                "intervention":            intervention,
                "expansion_opportunities": expansion_opps,
            },
            confidence=round(1 - churn_score / 100, 2),
            metadata={
                "arr":  account.get("arr", 0),
                "tier": account.get("tier", "standard"),
            },
        )

    async def _predict_churn(self, account: dict) -> dict:
        raw = await self.llm.complete(
            config.RETENTION_SYSTEM,
            config.prompt_retention_churn(account),
            temperature=0.2,
        )
        try:
            return json.loads(raw)
        except Exception:
            return {"churn_risk_score": 50, "raw": raw}

    def _extract_churn_score(self, analysis: dict) -> int:
        return analysis.get("churn_risk_score", 50) if isinstance(analysis, dict) else 50

    async def _build_intervention(self, account: dict, churn_analysis: dict) -> dict:
        risk = churn_analysis.get("churn_risk_score", 50)

        if risk >= 75:
            strategy = "immediate executive rescue"
        elif risk >= 50:
            strategy = "proactive success intervention"
        elif risk >= 25:
            strategy = "value reinforcement and growth"
        else:
            strategy = "advocacy and expansion"

        raw = await self.llm.complete(
            config.RETENTION_SYSTEM,
            config.prompt_retention_intervention(account, churn_analysis, risk, strategy),
            temperature=0.7,
        )
        try:
            return json.loads(raw)
        except Exception:
            return {"raw": raw}

    async def _find_expansion(self, account: dict) -> dict:
        raw = await self.llm.complete(
            config.RETENTION_SYSTEM,
            config.prompt_retention_expansion(account),
            temperature=0.5,
        )
        try:
            return json.loads(raw)
        except Exception:
            return {"raw": raw}
