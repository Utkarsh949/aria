"""
ARIA — CRM Connector
Adapter layer for Salesforce, HubSpot, and any generic REST CRM.
Translates native schemas to ARIA's unified deal / account format.
Renamed from crm_connector.py. Connection settings come from config.py.
"""

import logging
from typing import Optional
from datetime import datetime

import httpx
import config

logger = logging.getLogger("aria.crm")


# ══════════════════════════════════════════════════════════════════════════════
# UNIFIED SCHEMA HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _deal_schema(
    id: str, name: str, value: float, stage: str, close_date: str,
    account: str, owner: str, close_probability: int,
    days_in_stage: int, last_activity: str, contacts: list,
    notes: str, competitor_mentions: list, **extra,
) -> dict:
    return {
        "id": id, "name": name, "value": value, "stage": stage,
        "close_date": close_date, "account": account, "owner": owner,
        "close_probability": close_probability,
        "days_in_stage": days_in_stage,
        "last_activity": last_activity,
        "contacts": contacts,
        "notes": notes,
        "competitor_mentions": competitor_mentions,
        **extra,
    }


def _account_schema(
    id: str, name: str, arr: float, tier: str, csm: str,
    health_score: int, nps: Optional[int], renewal_date: str,
    monthly_logins: int, feature_adoption_pct: int,
    open_tickets: int, ticket_sentiment: str,
    stakeholder_changes_90d: int, **extra,
) -> dict:
    return {
        "id": id, "name": name, "arr": arr, "tier": tier, "csm": csm,
        "health_score": health_score, "nps": nps,
        "renewal_date": renewal_date,
        "monthly_logins": monthly_logins,
        "feature_adoption_pct": feature_adoption_pct,
        "open_tickets": open_tickets,
        "ticket_sentiment": ticket_sentiment,
        "stakeholder_changes_90d": stakeholder_changes_90d,
        **extra,
    }


# ══════════════════════════════════════════════════════════════════════════════
# BASE CONNECTOR
# ══════════════════════════════════════════════════════════════════════════════

class CRMConnector:
    """Base class — override for each CRM platform."""

    def __init__(self, api_url: str, api_key: str, timeout: int = 30):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
        }

    async def get_pipeline(self) -> list[dict]:
        raise NotImplementedError

    async def get_accounts(self) -> list[dict]:
        raise NotImplementedError

    async def update_deal(self, deal_id: str, payload: dict) -> dict:
        raise NotImplementedError

    async def log_activity(self, deal_id: str, note: str,
                           activity_type: str = "aria_insight") -> dict:
        raise NotImplementedError

    async def create_task(self, deal_id: str, title: str,
                          due_date: str, owner: str) -> dict:
        raise NotImplementedError


# ══════════════════════════════════════════════════════════════════════════════
# HUBSPOT ADAPTER
# ══════════════════════════════════════════════════════════════════════════════

class HubSpotConnector(CRMConnector):
    BASE = "https://api.hubapi.com"

    def __init__(self, access_token: str = ""):
        super().__init__(self.BASE, access_token or config.HUBSPOT_ACCESS_TOKEN)

    async def get_pipeline(self) -> list[dict]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(
                f"{self.BASE}/crm/v3/objects/deals",
                headers=self._headers(),
                params={
                    "properties": (
                        "dealname,amount,dealstage,closedate,hs_probability,"
                        "hubspot_owner_id,notes_last_updated,"
                        "hs_analytics_last_visit_timestamp"
                    ),
                    "limit": 100,
                },
            )
            resp.raise_for_status()
        return [self._map_deal(d) for d in resp.json().get("results", [])]

    def _map_deal(self, raw: dict) -> dict:
        p = raw.get("properties", {})
        return _deal_schema(
            id=raw.get("id", ""),
            name=p.get("dealname", ""),
            value=float(p.get("amount", 0) or 0),
            stage=p.get("dealstage", ""),
            close_date=p.get("closedate", ""),
            account=p.get("associatedcompanyid", ""),
            owner=p.get("hubspot_owner_id", ""),
            close_probability=int(float(p.get("hs_probability", 0) or 0)),
            days_in_stage=0,
            last_activity=p.get("notes_last_updated", ""),
            contacts=[],
            notes="",
            competitor_mentions=[],
        )

    async def update_deal(self, deal_id: str, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.patch(
                f"{self.BASE}/crm/v3/objects/deals/{deal_id}",
                headers=self._headers(),
                json={"properties": payload},
            )
            resp.raise_for_status()
            return resp.json()

    async def log_activity(self, deal_id: str, note: str,
                           activity_type: str = "aria_insight") -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.BASE}/crm/v3/objects/notes",
                headers=self._headers(),
                json={
                    "properties": {
                        "hs_note_body":  f"[ARIA {activity_type.upper()}] {note}",
                        "hs_timestamp":  datetime.utcnow().isoformat() + "Z",
                    },
                    "associations": [{
                        "to": {"id": deal_id},
                        "types": [{
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": 214,
                        }],
                    }],
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def get_accounts(self) -> list[dict]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(
                f"{self.BASE}/crm/v3/objects/companies",
                headers=self._headers(),
                params={
                    "properties": "name,annualrevenue,hs_lead_status,hubspot_owner_id",
                    "limit": 100,
                },
            )
            resp.raise_for_status()
        return [self._map_account(c) for c in resp.json().get("results", [])]

    def _map_account(self, raw: dict) -> dict:
        p = raw.get("properties", {})
        return _account_schema(
            id=raw.get("id", ""),
            name=p.get("name", ""),
            arr=float(p.get("annualrevenue", 0) or 0),
            tier="standard",
            csm=p.get("hubspot_owner_id", ""),
            health_score=70, nps=None,
            renewal_date="", monthly_logins=0,
            feature_adoption_pct=0, open_tickets=0,
            ticket_sentiment="neutral", stakeholder_changes_90d=0,
        )

    async def create_task(self, deal_id: str, title: str,
                          due_date: str, owner: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.BASE}/crm/v3/objects/tasks",
                headers=self._headers(),
                json={"properties": {
                    "hs_task_subject":   title,
                    "hs_task_status":    "NOT_STARTED",
                    "hs_timestamp":      due_date,
                    "hubspot_owner_id":  owner,
                }},
            )
            resp.raise_for_status()
            return resp.json()


# ══════════════════════════════════════════════════════════════════════════════
# SALESFORCE ADAPTER
# ══════════════════════════════════════════════════════════════════════════════

class SalesforceConnector(CRMConnector):
    def __init__(self, instance_url: str = "", access_token: str = ""):
        super().__init__(
            instance_url  or config.SF_INSTANCE_URL,
            access_token  or config.SF_ACCESS_TOKEN,
        )

    async def get_pipeline(self) -> list[dict]:
        soql = (
            "SELECT Id,Name,Amount,StageName,CloseDate,Probability,"
            "OwnerId,AccountId,LastActivityDate,Description "
            "FROM Opportunity WHERE IsClosed=false LIMIT 200"
        )
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(
                f"{self.api_url}/services/data/v58.0/query",
                headers=self._headers(),
                params={"q": soql},
            )
            resp.raise_for_status()
        return [self._map_deal(r) for r in resp.json().get("records", [])]

    def _map_deal(self, r: dict) -> dict:
        return _deal_schema(
            id=r.get("Id", ""),
            name=r.get("Name", ""),
            value=float(r.get("Amount", 0) or 0),
            stage=r.get("StageName", ""),
            close_date=r.get("CloseDate", ""),
            account=r.get("AccountId", ""),
            owner=r.get("OwnerId", ""),
            close_probability=int(r.get("Probability", 0) or 0),
            days_in_stage=0,
            last_activity=str(r.get("LastActivityDate", "")),
            contacts=[], notes=r.get("Description", ""),
            competitor_mentions=[],
        )

    async def update_deal(self, deal_id: str, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.patch(
                f"{self.api_url}/services/data/v58.0/sobjects/Opportunity/{deal_id}",
                headers=self._headers(), json=payload,
            )
            resp.raise_for_status()
        return {"status": "updated", "id": deal_id}

    async def log_activity(self, deal_id: str, note: str,
                           activity_type: str = "aria_insight") -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.api_url}/services/data/v58.0/sobjects/Task",
                headers=self._headers(),
                json={
                    "Subject":      f"[ARIA] {activity_type}",
                    "Description":  note,
                    "WhatId":       deal_id,
                    "Status":       "Completed",
                    "ActivityDate": datetime.utcnow().strftime("%Y-%m-%d"),
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def get_accounts(self) -> list[dict]:
        soql = "SELECT Id,Name,AnnualRevenue,OwnerId,Industry FROM Account LIMIT 200"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(
                f"{self.api_url}/services/data/v58.0/query",
                headers=self._headers(), params={"q": soql},
            )
            resp.raise_for_status()
        return [self._map_account(r) for r in resp.json().get("records", [])]

    def _map_account(self, r: dict) -> dict:
        return _account_schema(
            id=r.get("Id", ""), name=r.get("Name", ""),
            arr=float(r.get("AnnualRevenue", 0) or 0),
            tier="standard", csm=r.get("OwnerId", ""),
            health_score=70, nps=None, renewal_date="",
            monthly_logins=0, feature_adoption_pct=0,
            open_tickets=0, ticket_sentiment="neutral",
            stakeholder_changes_90d=0,
        )

    async def create_task(self, deal_id: str, title: str,
                          due_date: str, owner: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.api_url}/services/data/v58.0/sobjects/Task",
                headers=self._headers(),
                json={
                    "Subject":      title,
                    "WhatId":       deal_id,
                    "OwnerId":      owner,
                    "ActivityDate": due_date,
                    "Status":       "Not Started",
                },
            )
            resp.raise_for_status()
            return resp.json()


# ══════════════════════════════════════════════════════════════════════════════
# GENERIC REST ADAPTER
# ══════════════════════════════════════════════════════════════════════════════

class GenericCRMConnector(CRMConnector):
    """Adapter for any REST CRM that follows common conventions."""

    async def get_pipeline(self) -> list[dict]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.api_url}/deals", headers=self._headers())
            resp.raise_for_status()
        raw = resp.json()
        return raw.get("data", raw) if isinstance(raw, dict) else raw

    async def get_accounts(self) -> list[dict]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.api_url}/accounts", headers=self._headers())
            resp.raise_for_status()
        raw = resp.json()
        return raw.get("data", raw) if isinstance(raw, dict) else raw

    async def update_deal(self, deal_id: str, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.patch(
                f"{self.api_url}/deals/{deal_id}",
                headers=self._headers(), json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    async def log_activity(self, deal_id: str, note: str,
                           activity_type: str = "aria_insight") -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.api_url}/activities",
                headers=self._headers(),
                json={"deal_id": deal_id, "type": activity_type, "note": note},
            )
            resp.raise_for_status()
            return resp.json()

    async def create_task(self, deal_id: str, title: str,
                          due_date: str, owner: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.api_url}/tasks",
                headers=self._headers(),
                json={
                    "deal_id": deal_id, "title": title,
                    "due_date": due_date, "owner": owner,
                },
            )
            resp.raise_for_status()
            return resp.json()


# ══════════════════════════════════════════════════════════════════════════════
# FACTORY
# ══════════════════════════════════════════════════════════════════════════════

def get_crm_connector(platform: str = "") -> CRMConnector:
    """
    Return the right connector based on CRM_PLATFORM in config.py / env.
    Override by passing platform explicitly.
    """
    platform = (platform or config.CRM_PLATFORM).lower()
    if platform == "hubspot":
        return HubSpotConnector()
    elif platform == "salesforce":
        return SalesforceConnector()
    else:
        return GenericCRMConnector(config.CRM_API_URL, config.CRM_API_KEY)
