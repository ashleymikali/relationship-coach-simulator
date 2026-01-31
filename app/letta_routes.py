# app/letta_routes.py

import os
import json
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/letta", tags=["letta"])


def _get_letta_config() -> tuple[str, str]:
    base_url = os.getenv("LETTA_BASE_URL", "").rstrip("/")
    api_key = os.getenv("LETTA_API_KEY", "")
    if not base_url or not api_key:
        raise RuntimeError("LETTA_BASE_URL and LETTA_API_KEY must be set in env")
    return base_url, api_key


def _agent_id_for_user(user_id: str) -> str:
    """
    Map your demo users to Letta agent IDs stored in env.
    Example env names:
    LETTA_MATCHMAKER_A_ID
    LETTA_MATCHMAKER_B_ID
    LETTA_MATCHMAKER_C_ID
    """
    mapping = {
        "user_001": os.getenv("LETTA_MATCHMAKER_A_ID", ""),
        "user_002": os.getenv("LETTA_MATCHMAKER_B_ID", ""),
        "user_003": os.getenv("LETTA_MATCHMAKER_C_ID", ""),
    }
    agent_id = mapping.get(user_id) or ""
    if not agent_id:
        raise HTTPException(status_code=400, detail=f"No Letta agent ID configured for {user_id}")
    return agent_id


class StoreIntakeRequest(BaseModel):
    user_id: str
    display_name: str
    preferences: list[str]
    dealbreakers: list[str]
    dating_thesis: str
    source: str  # "profile" | "live_intake" | "combined"


@router.post("/intake/store")
async def letta_store_intake(req: StoreIntakeRequest) -> Dict[str, Any]:
    """
    Use the Letta agent MCP tool store_intake_summary via the Letta REST API.
    """
    base_url, api_key = _get_letta_config()
    agent_id = _agent_id_for_user(req.user_id)

    # Build the Letta prompt that tells the agent to run its MCP tool.
    # We keep it simple so it consumes fewer tokens.
    prompt = (
        "Use the MCP tool store_intake_summary with these exact fields.\n"
        f"user_id: {req.user_id}\n"
        f"display_name: {req.display_name}\n"
        f"preferences: {req.preferences}\n"
        f"dealbreakers: {req.dealbreakers}\n"
        f"dating_thesis: {req.dating_thesis}\n"
        f"source: {req.source}\n"
        "Then reply ONLY with the memory label stored."
    )

    url = f"{base_url}/v1/agents/{agent_id}/messages"
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"messages": [{"role": "user", "content": prompt}]},
        )

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Letta API error: {response.status_code} {response.text}")

    data = response.json()
    return {"ok": True, "letta_response": data}


@router.get("/intake/get")
async def letta_get_intake(user_id: str, q: Optional[str] = None) -> Dict[str, Any]:
    """
    Ask the Letta agent to retrieve intake summary from long-term memory.
    q: optional query to filter memory search (defaults to 'intake_summary').
    """
    base_url, api_key = _get_letta_config()
    agent_id = _agent_id_for_user(user_id)

    query = q or "intake_summary"
    prompt = (
        f"Retrieve the intake summary for {user_id} from memory using the MCP tool retrieve_user_memory.\n"
        "Return EXACTLY valid JSON."
    )

    url = f"{base_url}/v1/agents/{agent_id}/messages"
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"messages": [{"role": "user", "content": prompt}]},
        )

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Letta API error: {response.status_code} {response.text}")

    return {"ok": True, "letta_response": response.json()}