# app/intake_live.py

"""Live intake interview session management."""

import time
from typing import Any, Dict, List
from uuid import uuid4

from app.openrouter_client import OpenRouterClient
from app.registry import get_matchmaker

# In-memory session storage
_sessions: Dict[str, Dict[str, Any]] = {}

# Deterministic fallback questions (for demo reliability)
_FALLBACK_QUESTIONS = [
    "How do you like to handle conflict or tension when it comes up with a partner?",
    "What are your biggest dealbreakers or red flags in dating?",
    "What does a great week in a relationship look like for you (time together vs. alone, routines, etc.)?",
    "What kind of emotional support do you like to give and receive?",
]


def start_session(user_id: str) -> Dict[str, Any]:
    """
    Start a new live intake session for a user.
    """
    session_id = str(uuid4())

    first_question = (
        "What matters most to you in a romantic relationship, and how would you describe your ideal relationship dynamic?"
    )

    session = {
        "session_id": session_id,
        "user_id": user_id,
        "step_index": 0,  # 0-based question index
        "questions": [first_question],
        "answers": [],
        "created_at": time.time(),
        "is_complete": False,
    }

    _sessions[session_id] = session

    return {"session_id": session_id, "question": first_question, "step_index": 0}


async def submit_answer(session_id: str, answer_text: str) -> Dict[str, Any]:
    """
    Submit an answer to the current question and get the next question, or finalize at 5 answers.
    """
    session = _sessions.get(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    if session["is_complete"]:
        raise ValueError(f"Session {session_id} is already complete")

    # Store the answer
    session["answers"].append(answer_text)

    # Write Q/A to agent memory
    agent = get_matchmaker(session["user_id"])
    current_question = session["questions"][session["step_index"]]
    if agent:
        agent.memory.write(
            text=f"Q: {current_question}\nA: {answer_text}",
            metadata={
                "type": "intake_live",
                "session_id": session_id,
                "step_index": session["step_index"],
                "timestamp": time.time(),
            },
        )

    # Move to next step
    session["step_index"] += 1

    # Completed all 5 questions -> finalize
    if session["step_index"] >= 5:
        session["is_complete"] = True

        # Build extra_context from Q/A pairs
        qa_pairs = []
        for i, (q, a) in enumerate(zip(session["questions"], session["answers"]), 1):
            qa_pairs.append(f"Q{i}: {q}\nA{i}: {a}")
        extra_context = "\n\n".join(qa_pairs)

        # Generate final summary with extra_context
        if not agent:
            final_summary = {
                "preferences": [],
                "dealbreakers": [],
                "dating_thesis": "No agent available for this user.",
            }
        else:
            client = OpenRouterClient()
            final_summary = await agent.run_intake_summary(client, extra_context=extra_context)

        return {
            "session_id": session_id,
            "question": None,
            "step_index": session["step_index"],
            "is_complete": True,
            "final_summary": final_summary,
        }

    # Otherwise generate next question (adaptive with fallback)
    next_question = await _generate_next_question(
        questions=session["questions"],
        answers=session["answers"],
        step_index=session["step_index"],
    )

    session["questions"].append(next_question)

    return {
        "session_id": session_id,
        "question": next_question,
        "step_index": session["step_index"],
        "is_complete": False,
        "final_summary": None,
    }


async def _generate_next_question(questions: List[str], answers: List[str], step_index: int) -> str:
    """
    Generate the next adaptive question based on previous Q/A.
    step_index is the NEXT question index (0-based) after increment.
    """
    prev_question = questions[-1]
    prev_answer = answers[-1]

    # step_index values:
    # 1 -> question #2
    # 2 -> question #3
    # 3 -> question #4
    # 4 -> question #5

    client = OpenRouterClient()

    prompt = f"""You are conducting a dating intake interview. Generate the next question (question #{step_index + 1} of 5).

Previous question: {prev_question}
Their answer: {prev_answer}

Generate a follow-up question that:
1) References their previous answer in ONE sentence (adaptive feel)
2) Stays short and conversational
3) Explores a different aspect of dating/relationships (values, communication style, deal-breakers, lifestyle compatibility, emotional needs)
4) Is open-ended and encourages thoughtful response

Return ONLY the question text, no extra commentary.
"""

    try:
        messages = [{"role": "user", "content": prompt}]
        next_question = await client.chat(messages, temperature=0.6)
        q = next_question.strip()
        if q:
            return q
    except Exception:
        pass

    # Fallback mapping:
    # step_index=1 -> fallback[0]
    # step_index=2 -> fallback[1]
    # step_index=3 -> fallback[2]
    # step_index=4 -> fallback[3]
    fallback_idx = max(0, min(step_index - 1, len(_FALLBACK_QUESTIONS) - 1))
    return _FALLBACK_QUESTIONS[fallback_idx]


def get_status(session_id: str) -> Dict[str, Any]:
    """
    Get the current status of a session.
    """
    session = _sessions.get(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    return {
        "session_id": session["session_id"],
        "user_id": session["user_id"],
        "step_index": session["step_index"],
        "total_questions": 5,
        "questions_answered": len(session["answers"]),
        "is_complete": session["is_complete"],
        "created_at": session["created_at"],
    }
