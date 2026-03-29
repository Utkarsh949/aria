"""
ARIA — Deal Intelligence Agent
Monitors pipeline health, detects risk signals, and generates recovery plays.
Renamed from deal_intelligence_agent.py. All prompts live in config.py.
"""

import json

from brain import AgentResult, LLMGateway
import config


class DealIntelligenceAgent:
    NAME = "DealIntelligenceAgent"

    def __init__(self, llm: LLMGateway):
        self.llm = llm

    async def run(self, deal: dict) -> AgentResult:
        risk_profile  = await self._analyse_risk(deal)
        health_score  = self._calculate_health(risk_profile, deal)
        recovery_play = await self._generate_recovery(deal, risk_profile, health_score)
        forecast      = await self._forecast(deal, health_score)

        return AgentResult(
            agent=self.NAME,
            action="deal_intelligence",
            data={
                "deal_id":       deal.get("id", "unknown"),
                "deal_name":     deal.get("name", ""),
                "health_score":  health_score,
                "risk_profile":  risk_profile,
                "recovery_play": recovery_play,
                "forecast":      forecast,
            },
            confidence=round(health_score / 100, 2),
            metadata={
                "deal_value": deal.get("value", 0),
                "stage":      deal.get("stage", ""),
            },
        )

    async def _analyse_risk(self, deal: dict) -> dict:
        raw = await self.llm.complete(
            config.DEAL_SYSTEM,
            config.prompt_deal_risk(deal),
            temperature=0.2,
        )
        try:
            return json.loads(raw)
        except Exception:
            return {"raw": raw, "signals_detected": [], "primary_risk": "unknown"}

    def _calculate_health(self, risk_profile: dict, deal: dict) -> int:
        score = 100

        # Penalise by detected signal severity
        for sig in risk_profile.get("signals_detected", []):
            score -= config.DEAL_SEVERITY_PENALTY.get(sig.get("severity", "low"), 5)

        # Bonus / penalty by deal stage
        score += config.DEAL_STAGE_BONUS.get(
            str(deal.get("stage", "")).lower(), 0
        )

        # Penalise for long stagnation in current stage
        days_open = deal.get("days_in_stage", 0)
        if days_open > 30:
            score -= min(15, (days_open - 30) // 5)

        return max(0, min(100, score))

    async def _generate_recovery(self, deal: dict, risk_profile: dict, health: int) -> dict:
        if health >= 75:
            urgency = "maintain momentum"
        elif health >= 50:
            urgency = "intervene within 48 hours"
        else:
            urgency = "URGENT — immediate action required"

        raw = await self.llm.complete(
            config.DEAL_SYSTEM,
            config.prompt_deal_recovery(deal, risk_profile, health, urgency),
            temperature=0.7,
        )
        try:
            return json.loads(raw)
        except Exception:
            return {"raw": raw}

    async def _forecast(self, deal: dict, health: int) -> dict:
        base_prob = deal.get("close_probability", 50)
        adjusted  = round((base_prob * 0.4) + (health * 0.6), 1)

        raw = await self.llm.complete(
            config.DEAL_SYSTEM,
            config.prompt_deal_forecast(deal, health, adjusted),
            temperature=0.2,
        )
        try:
            return json.loads(raw)
        except Exception:
            return {"win_probability": adjusted, "raw": raw}
