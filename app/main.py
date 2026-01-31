# app/main.py

import asyncio
import json
from typing import AsyncGenerator

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.openrouter_client import OpenRouterClient
from app.registry import list_users, get_user, get_matchmaker, get_evaluator

from app.letta_routes import router as letta_router

app = FastAPI(title="Hang the DJ API")

app.include_router(letta_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    user_text: str


class LiveAnswerRequest(BaseModel):
    answer_text: str


def _agent_has_intake_summary(agent) -> bool:
    """
    Works with your placeholder Memory:
    - Prefer metadata type == 'intake_summary' if entries exist
    - Fallback to substring search for 'Intake summary'
    """
    if not agent or not hasattr(agent, "memory"):
        return False

    mem = agent.memory

    if hasattr(mem, "all"):
        for e in reversed(mem.all()):
            md = e.get("metadata") or {}
            if md.get("type") == "intake_summary":
                return True

    if hasattr(mem, "search"):
        hits = mem.search("Intake summary", k=1)
        return bool(hits)

    return False


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/users")
async def get_users():
    return {"users": list_users()}


@app.post("/api/intake/{user_id}")
async def create_intake(user_id: str):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    agent = get_matchmaker(user_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Matchmaker agent for {user_id} not found")

    client = OpenRouterClient()
    summary = await agent.run_intake_summary(client)
    return {"user_id": user_id, "summary": summary}


@app.post("/api/report/{user_a_id}/{user_b_id}")
async def generate_report(user_a_id: str, user_b_id: str):
    user_a = get_user(user_a_id)
    if not user_a:
        raise HTTPException(status_code=404, detail=f"User {user_a_id} not found")

    user_b = get_user(user_b_id)
    if not user_b:
        raise HTTPException(status_code=404, detail=f"User {user_b_id} not found")

    agent_a = get_matchmaker(user_a_id)
    if not agent_a:
        raise HTTPException(status_code=404, detail=f"Matchmaker for {user_a_id} not found")

    agent_b = get_matchmaker(user_b_id)
    if not agent_b:
        raise HTTPException(status_code=404, detail=f"Matchmaker for {user_b_id} not found")

    evaluator = get_evaluator()
    client = OpenRouterClient()

    report = await evaluator.generate_match_report(
        user_a=user_a,
        agent_a=agent_a,
        user_b=user_b,
        agent_b=agent_b,
        openrouter_client=client,
    )

    return {"report": report}


@app.post("/api/intake/live/start/{user_id}")
async def start_live_intake(user_id: str):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    from app.intake_live import start_session

    return start_session(user_id)


@app.post("/api/intake/live/answer/{session_id}")
async def submit_live_answer(session_id: str, request: LiveAnswerRequest):
    answer_text = request.answer_text.strip()
    if not answer_text:
        raise HTTPException(status_code=400, detail="answer_text is required")

    from app.intake_live import submit_answer

    try:
        return await submit_answer(session_id, answer_text)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/intake/live/status/{session_id}")
async def get_live_intake_status(session_id: str):
    from app.intake_live import get_status

    try:
        return get_status(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/date/exchange/{user_a_id}/{user_b_id}")
async def run_date_exchange(user_a_id: str, user_b_id: str):
    user_a = get_user(user_a_id)
    if not user_a:
        raise HTTPException(status_code=404, detail=f"User {user_a_id} not found")

    user_b = get_user(user_b_id)
    if not user_b:
        raise HTTPException(status_code=404, detail=f"User {user_b_id} not found")

    agent_a = get_matchmaker(user_a_id)
    if not agent_a:
        raise HTTPException(status_code=404, detail=f"Matchmaker for {user_a_id} not found")

    agent_b = get_matchmaker(user_b_id)
    if not agent_b:
        raise HTTPException(status_code=404, detail=f"Matchmaker for {user_b_id} not found")

    client = OpenRouterClient()

    if not _agent_has_intake_summary(agent_a):
        await agent_a.run_intake_summary(client)

    if not _agent_has_intake_summary(agent_b):
        await agent_b.run_intake_summary(client)

    evaluator = get_evaluator()

    result = await evaluator.run_date_exchange(
        user_a=user_a,
        agent_a=agent_a,
        user_b=user_b,
        agent_b=agent_b,
        openrouter_client=client,
    )

    return result


@app.post("/api/pipeline/{user_a_id}/{user_b_id}")
async def run_pipeline(user_a_id: str, user_b_id: str):
    user_a = get_user(user_a_id)
    if not user_a:
        raise HTTPException(status_code=404, detail=f"User {user_a_id} not found")

    user_b = get_user(user_b_id)
    if not user_b:
        raise HTTPException(status_code=404, detail=f"User {user_b_id} not found")

    agent_a = get_matchmaker(user_a_id)
    if not agent_a:
        raise HTTPException(status_code=404, detail=f"Matchmaker for {user_a_id} not found")

    agent_b = get_matchmaker(user_b_id)
    if not agent_b:
        raise HTTPException(status_code=404, detail=f"Matchmaker for {user_b_id} not found")

    client = OpenRouterClient()

    if not _agent_has_intake_summary(agent_a):
        await agent_a.run_intake_summary(client)

    if not _agent_has_intake_summary(agent_b):
        await agent_b.run_intake_summary(client)

    evaluator = get_evaluator()

    exchanges = []
    for _ in range(3):
        exchanges.append(
            await evaluator.run_date_exchange(
                user_a=user_a,
                agent_a=agent_a,
                user_b=user_b,
                agent_b=agent_b,
                openrouter_client=client,
            )
        )

    final_report = await evaluator.generate_pipeline_report(
        user_a=user_a,
        agent_a=agent_a,
        user_b=user_b,
        agent_b=agent_b,
        exchanges=exchanges,
        openrouter_client=client,
    )

    return {
        "user_a_id": user_a_id,
        "user_b_id": user_b_id,
        "dates": exchanges,
        "final_report": final_report,
    }


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    async def event_generator() -> AsyncGenerator[dict, None]:
        try:
            client = OpenRouterClient()

            yield {
                "event": "meta",
                "data": json.dumps(
                    {
                        "timestamp": asyncio.get_running_loop().time(),
                        "model": client.model,
                    }
                ),
            }

            yield {
                "event": "transcript",
                "data": json.dumps({"speaker": "user", "text": request.user_text}),
            }

            yield {
                "event": "transcript",
                "data": json.dumps(
                    {
                        "speaker": "agent#3",
                        "text": "Neutral evaluator online. Generating an explainable response.",
                    }
                ),
            }

            system_prompt = """
You are Agent #3, the neutral evaluator in an agentic matchmaking demo called "Hang the DJ".

Context you must assume is true:
- There are 3 demo users: Jordan (user_001), Alex (user_002), Sam (user_003).
- The backend exposes:
  - GET /api/users
  - POST /api/intake/{user_id}
  - POST /api/report/{user_a_id}/{user_b_id}
  - POST /api/date/exchange/{user_a_id}/{user_b_id}
  - POST /api/pipeline/{user_a_id}/{user_b_id}
  - Live intake endpoints exist too (/api/intake/live/...)
- The UI lets the presenter:
  1) run intake
  2) simulate dates
  3) generate reports
  4) ask you questions via this streaming endpoint

Your job:
- Answer in a demo-friendly way.
- If asked to explain the demo, summarize the workflow.
- 5–8 sentences unless asked for detail.
""".strip()

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.user_text},
            ]

            response_text = await client.chat(messages, temperature=0.4)

            chunk_size = 60
            for i in range(0, len(response_text), chunk_size):
                chunk = response_text[i : i + chunk_size]
                yield {"event": "delta", "data": json.dumps({"speaker": "agent#3", "text": chunk})}
                await asyncio.sleep(0.05)

            yield {"event": "done", "data": json.dumps({"status": "complete"})}

        except Exception as e:
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(event_generator())
