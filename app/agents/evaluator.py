# app/agents/evaluator.py

"""Neutral evaluator agent - provides unbiased match analysis and explanations."""

import json
import time
from typing import Any, Dict, List, Optional, Tuple

from app.agents.base import BaseAgent


class NeutralEvaluatorAgent(BaseAgent):
    """
    Neutral third-party agent that evaluates matches objectively.

    This agent synthesizes information from both MatchmakerAgents,
    produces explainable match scores, and generates final reports.
    """

    def __init__(self):
        super().__init__(
            name="Agent#3_NeutralEvaluator",
            role="Objective match evaluator and explainability provider",
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        task_type = input_data.get("task_type", "unknown")
        return {
            "agent": self.name,
            "task_type": task_type,
            "status": "not_implemented",
            "message": f"NeutralEvaluator received task: {task_type}",
        }

    async def generate_match_report(
        self,
        user_a: Dict[str, Any],
        agent_a,
        user_b: Dict[str, Any],
        agent_b,
        openrouter_client,
    ) -> str:
        """
        Generate an explainable match report for two users.
        Also (best-effort) references the most recent date_exchange between them.
        """
        intake_a = self._extract_intake_summary(agent_a)
        intake_b = self._extract_intake_summary(agent_b)

        exch = self._extract_latest_date_exchange(agent_a, agent_b, user_a, user_b)
        exch_quote = self._extract_short_quote(exch, max_len=160) if exch else None

        quote_clause = ""
        if exch_quote:
            quote_clause = f"""
You also have a snippet from their most recent simulated date exchange:
QUOTE: "{exch_quote}"

Include EXACTLY ONE bullet in REASONING that cites the QUOTE and ties it to a preference or dealbreaker from the intake summaries.
""".rstrip()

        prompt = f"""You are a neutral matchmaking evaluator. Analyze these two dating profiles and their intake summaries to determine compatibility.

USER A: {user_a['display_name']}
Bio: {user_a['bio']}
Intake Summary:
{json.dumps(intake_a, indent=2)}

USER B: {user_b['display_name']}
Bio: {user_b['bio']}
Intake Summary:
{json.dumps(intake_b, indent=2)}
{quote_clause}

Generate a match evaluation report with this structure:

VERDICT: [ACCEPT or REJECT]

REASONING:
• [Reason 1 grounded in intake summaries]
• [Reason 2 grounded in intake summaries]
• [Reason 3 grounded in intake summaries]

PREDICTED FRICTION POINT:
[One specific area where conflict might arise based on their profiles]

SUGGESTED FIRST DATE:
[One icebreaker activity or conversation starter that plays to their strengths]

Rules:
- Be specific and reference actual preferences/dealbreakers from the intake summaries
- ACCEPT if compatibility is strong; REJECT if dealbreakers conflict
- Keep it concise and demo-friendly
- Return plain text, not JSON
"""

        report = await openrouter_client.chat(
            [{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        self.memory.write(
            text=f"Match evaluation: {user_a['display_name']} × {user_b['display_name']}\n{report}",
            metadata={
                "type": "match_report",
                "user_a_id": user_a["user_id"],
                "user_b_id": user_b["user_id"],
                "timestamp": time.time(),
            },
        )

        return report.strip()

    async def score_date_exchange(
        self,
        scene: str,
        transcript: List[Dict[str, Any]],
        intake_a: Dict[str, Any],
        intake_b: Dict[str, Any],
        openrouter_client,
    ) -> Dict[str, Any]:
        """
        Score a date exchange and return structured JSON with scores and reasoning.
        """
        transcript_text = "\n".join([f"{t['name']}: {t['text']}" for t in transcript])

        prompt = f"""You are scoring a first date exchange. Analyze the conversation and return a JSON score.

Scene: {scene}

Transcript:
{transcript_text}

Intake Summary A:
{json.dumps(intake_a, indent=2)}

Intake Summary B:
{json.dumps(intake_b, indent=2)}

Generate a JSON response with this EXACT structure:
{{
  "score_a": <0-10 integer, how well A performed>,
  "score_b": <0-10 integer, how well B performed>,
  "compatibility": <0-100 integer, overall compatibility>,
  "reasons": [
    "reason 1 grounded in behavior",
    "reason 2 grounded in behavior",
    "reason 3 grounded in behavior"
  ],
  "quote": "one short memorable quote from the transcript (under 100 chars)"
}}

Rules:
- Return ONLY valid JSON, no markdown, no extra text
- Scores should reflect communication quality, boundary respect, and alignment with intake preferences
- Quote should be verbatim from transcript
"""

        response = await openrouter_client.chat(
            [{"role": "user", "content": prompt}],
            temperature=0.5,
        )

        try:
            from app.agents.matchmaker import extract_json  # re-use your helper

            score_data = extract_json(response)

            if not isinstance(score_data, dict):
                raise ValueError("score_data not dict")

            score_data.setdefault("score_a", 5)
            score_data.setdefault("score_b", 5)
            score_data.setdefault("compatibility", 50)
            score_data.setdefault("reasons", ["Unable to parse reasons"])
            score_data.setdefault("quote", "")

            return score_data
        except Exception:
            return {
                "score_a": 5,
                "score_b": 5,
                "compatibility": 50,
                "reasons": ["Scoring failed - unable to parse LLM response"],
                "quote": "",
            }

    async def run_date_exchange(
        self,
        user_a: Dict[str, Any],
        agent_a,
        user_b: Dict[str, Any],
        agent_b,
        openrouter_client,
    ) -> Dict[str, Any]:
        """
        Simulate a 6-turn date exchange between two users.
        Returns: scene, transcript, evaluator_notes, score, delta_insight, reflections
        """
        intake_a = self._extract_intake_summary(agent_a)
        intake_b = self._extract_intake_summary(agent_b)

        # 1) Scene
        scene_prompt = f"""You are setting the scene for a first date between {user_a['display_name']} and {user_b['display_name']}.

Generate a 2-4 sentence scene description. Choose a setting (restaurant, coffee shop, park, art gallery, etc.) that feels natural for a first date. Be specific and atmospheric.

Return ONLY the scene description, no extra commentary.
"""
        scene = await openrouter_client.chat(
            [{"role": "user", "content": scene_prompt}],
            temperature=0.7,
        )
        scene = scene.strip()

        # 2) Test moment
        test_moment_prompt = """Generate a brief test moment for a first date. This should be a minor awkward or challenging situation that reveals how people handle discomfort.

Examples:
- [The waiter brings the wrong order]
- [An awkward joke lands badly]
- [Someone's phone rings with an urgent call]
- [A minor disagreement about the menu]

Return ONLY the bracketed stage direction, keep it under 15 words.
"""
        test_moment = await openrouter_client.chat(
            [{"role": "user", "content": test_moment_prompt}],
            temperature=0.8,
        )
        test_moment = test_moment.strip()
        if not test_moment.startswith("["):
            test_moment = f"[{test_moment}]"

        # 3) Conversation (6 turns)
        transcript: List[Dict[str, Any]] = []
        running = ""

        for turn in range(6):
            is_user_a = (turn % 2 == 0)
            current_user = user_a if is_user_a else user_b
            current_intake = intake_a if is_user_a else intake_b
            speaker_label = "A" if is_user_a else "B"

            system_prompt = f"""You are roleplaying as {current_user['display_name']} on a first date.

Your profile:
- Bio: {current_user['bio']}
- Traits: {', '.join(current_user['traits'])}
- Boundaries: {', '.join(current_user['boundaries'])}

Your intake summary:
{json.dumps(current_intake, indent=2)}

Scene:
{scene}

Conversation so far:
{running}

Stay in character. Keep your response natural and conversational (2-4 sentences max).
"""

            user_prompt = (
                f"{test_moment}\nRespond naturally to what just happened."
                if turn == 2
                else "Continue the conversation naturally."
            )

            response = await openrouter_client.chat(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
            )
            response = response.strip()

            transcript.append(
                {"speaker": speaker_label, "name": current_user["display_name"], "text": response}
            )
            running += f"{current_user['display_name']}: {response}\n"

        transcript_text = "\n".join([f"{t['name']}: {t['text']}" for t in transcript])

        # 4) Evaluator notes
        notes_prompt = f"""You observed this first date exchange between {user_a['display_name']} and {user_b['display_name']}.

Scene: {scene}

Transcript:
{transcript_text}

Write 3 concise bullet-point observations about their interaction. Focus on:
- How they handled the test moment
- Communication styles and compatibility
- Red flags or green flags

Return ONLY the 3 bullets, no extra commentary.
"""
        notes_response = await openrouter_client.chat(
            [{"role": "user", "content": notes_prompt}],
            temperature=0.6,
        )

        evaluator_notes = [
            line.strip().lstrip("•-*").strip()
            for line in notes_response.strip().split("\n")
            if line.strip() and not line.strip().startswith("#")
        ][:3]

        ts = time.time()

        # ---------------------------------------------------------------------
        # Improvement #1 (Delta Insight):
        # Explicitly connect "intake expectations" vs "observed behavior" with
        # one crisp mini-analysis. Useful for the demo: “explainable agent”.
        # ---------------------------------------------------------------------
        delta_insight = await self._generate_delta_insight(
            user_a=user_a,
            user_b=user_b,
            intake_a=intake_a,
            intake_b=intake_b,
            scene=scene,
            transcript_text=transcript_text,
            evaluator_notes=evaluator_notes,
            openrouter_client=openrouter_client,
        )

        if delta_insight:
            self.memory.write(
                text=(
                    f"Delta insight: {user_a['display_name']} × {user_b['display_name']}\n"
                    f"{delta_insight}"
                ),
                metadata={
                    "type": "date_delta_insight",
                    "user_a_id": user_a["user_id"],
                    "user_b_id": user_b["user_id"],
                    "timestamp": ts,
                },
            )

        # Store date exchange in each matchmaker memory
        if agent_a and hasattr(agent_a, "memory"):
            agent_a.memory.write(
                text=f"Date exchange with {user_b['display_name']}:\n{scene}\n\n{transcript_text}",
                metadata={
                    "type": "date_exchange",
                    "partner_user_id": user_b["user_id"],
                    "timestamp": ts,
                },
            )

        if agent_b and hasattr(agent_b, "memory"):
            agent_b.memory.write(
                text=f"Date exchange with {user_a['display_name']}:\n{scene}\n\n{transcript_text}",
                metadata={
                    "type": "date_exchange",
                    "partner_user_id": user_a["user_id"],
                    "timestamp": ts,
                },
            )

        self.memory.write(
            text=(
                f"Date exchange: {user_a['display_name']} × {user_b['display_name']}\n"
                f"Scene: {scene}\n"
                f"Transcript:\n{transcript_text}\n"
                f"Notes: {'; '.join(evaluator_notes)}"
            ),
            metadata={
                "type": "date_exchange_eval",
                "user_a_id": user_a["user_id"],
                "user_b_id": user_b["user_id"],
                "timestamp": ts,
            },
        )

        # ---------------------------------------------------------------------
        # Improvement #2 (Matchmaker Reflections):
        # After the date, each MatchmakerAgent writes a short “advocate” note:
        # what they liked, what concerned them, and what they'd ask next.
        # This gives you “agentic” memory growth without Letta yet.
        # ---------------------------------------------------------------------
        reflection_a = await self._write_matchmaker_reflection(
            agent=agent_a,
            self_user=user_a,
            other_user=user_b,
            self_intake=intake_a,
            scene=scene,
            transcript_text=transcript_text,
            openrouter_client=openrouter_client,
            timestamp=ts,
        )

        reflection_b = await self._write_matchmaker_reflection(
            agent=agent_b,
            self_user=user_b,
            other_user=user_a,
            self_intake=intake_b,
            scene=scene,
            transcript_text=transcript_text,
            openrouter_client=openrouter_client,
            timestamp=ts,
        )

        reflections = {
            user_a["user_id"]: reflection_a,
            user_b["user_id"]: reflection_b,
        }

        # 5) Score
        score = await self.score_date_exchange(
            scene,
            transcript,
            intake_a,
            intake_b,
            openrouter_client,
        )

        self.memory.write(
            text=(
                f"Date score: {user_a['display_name']} × {user_b['display_name']}\n"
                f"{json.dumps(score, indent=2)}"
            ),
            metadata={
                "type": "date_score",
                "user_a_id": user_a["user_id"],
                "user_b_id": user_b["user_id"],
                "timestamp": ts,
            },
        )

        return {
            "scene": scene,
            "transcript": transcript,
            "evaluator_notes": evaluator_notes,
            "delta_insight": delta_insight,
            "reflections": reflections,
            "score": score,
        }

    async def generate_pipeline_report(
        self,
        user_a: Dict[str, Any],
        agent_a,
        user_b: Dict[str, Any],
        agent_b,
        exchanges: List[Dict[str, Any]],
        openrouter_client,
    ) -> str:
        """
        Generate a final pipeline report that synthesizes multiple date exchanges.
        """
        intake_a = self._extract_intake_summary(agent_a)
        intake_b = self._extract_intake_summary(agent_b)

        scores = [e.get("score") or {} for e in exchanges]
        compat_vals = [float(s.get("compatibility", 0)) for s in scores]
        a_vals = [float(s.get("score_a", 0)) for s in scores]
        b_vals = [float(s.get("score_b", 0)) for s in scores]

        avg_compat = sum(compat_vals) / len(compat_vals) if compat_vals else 0.0
        avg_a = sum(a_vals) / len(a_vals) if a_vals else 0.0
        avg_b = sum(b_vals) / len(b_vals) if b_vals else 0.0

        quotes = [s.get("quote", "") for s in scores if s.get("quote")]
        quotes_text = "\n".join([f'- "{q}"' for q in quotes[:3]]) if quotes else "- (no quote extracted)"

        prompt = f"""You are generating a final matchmaking pipeline report after observing {len(exchanges)} simulated date exchange(s).

USER A: {user_a['display_name']}
Intake Summary:
{json.dumps(intake_a, indent=2)}

USER B: {user_b['display_name']}
Intake Summary:
{json.dumps(intake_b, indent=2)}

AGGREGATE SCORES:
- Average Compatibility: {avg_compat:.1f}/100
- {user_a['display_name']} Performance: {avg_a:.1f}/10
- {user_b['display_name']} Performance: {avg_b:.1f}/10

MEMORABLE QUOTES FROM EXCHANGES:
{quotes_text}

Generate a final match evaluation report with this structure:

VERDICT: [ACCEPT or REJECT]

REASONING:
• [Reason 1 - reference at least ONE quote from above]
• [Reason 2 - grounded in scores and intake summaries]
• [Reason 3 - grounded in scores and intake summaries]

PREDICTED FRICTION POINT:
[One specific area where conflict might arise]

SUGGESTED FIRST DATE:
[One icebreaker activity that plays to their strengths]

Rules:
- ACCEPT if avg compatibility >= 60, otherwise REJECT
- At least ONE bullet in REASONING must cite a quote
- Be specific and reference actual data
- Return plain text, not JSON
"""

        report = await openrouter_client.chat(
            [{"role": "user", "content": prompt}],
            temperature=0.6,
        )

        self.memory.write(
            text=f"Pipeline report: {user_a['display_name']} × {user_b['display_name']}\n{report.strip()}",
            metadata={
                "type": "pipeline_report",
                "user_a_id": user_a["user_id"],
                "user_b_id": user_b["user_id"],
                "timestamp": time.time(),
            },
        )

        return report.strip()

    # -------------------------------------------------------------------------
    # Improvements #1 and #2 helpers
    # -------------------------------------------------------------------------

    async def _generate_delta_insight(
        self,
        user_a: Dict[str, Any],
        user_b: Dict[str, Any],
        intake_a: Dict[str, Any],
        intake_b: Dict[str, Any],
        scene: str,
        transcript_text: str,
        evaluator_notes: List[str],
        openrouter_client,
    ) -> str:
        """
        Generate a short explainability nugget: what each person signaled they want (intake)
        vs what they actually did (date transcript).
        """
        notes_text = "\n".join([f"- {n}" for n in (evaluator_notes or [])]) or "- (no notes)"
        prompt = f"""You are the neutral evaluator. Produce a short "delta insight" connecting intake expectations to observed behavior.

Scene:
{scene}

Intake A ({user_a['display_name']}):
{json.dumps(intake_a, indent=2)}

Intake B ({user_b['display_name']}):
{json.dumps(intake_b, indent=2)}

Observed transcript:
{transcript_text}

Evaluator notes:
{notes_text}

Return EXACTLY this structure (plain text, no markdown):

A_DELTA: <1 sentence: one intake expectation vs one observed behavior>
B_DELTA: <1 sentence: one intake expectation vs one observed behavior>
SHARED_SIGNAL: <1 sentence: what the interaction suggests about compatibility>

Rules:
- Reference at least one concrete behavior from the transcript in each DELTA.
- Keep each line under ~180 characters.
"""
        try:
            out = await openrouter_client.chat([{"role": "user", "content": prompt}], temperature=0.5)
            return out.strip()
        except Exception:
            return ""

    async def _write_matchmaker_reflection(
        self,
        agent,
        self_user: Dict[str, Any],
        other_user: Dict[str, Any],
        self_intake: Dict[str, Any],
        scene: str,
        transcript_text: str,
        openrouter_client,
        timestamp: float,
    ) -> str:
        """
        Have each MatchmakerAgent write a brief advocate reflection.
        Writes into that agent's memory and returns the reflection text.
        """
        if not agent or not hasattr(agent, "memory") or not hasattr(agent.memory, "write"):
            return ""

        prompt = f"""You are the MatchmakerAgent advocating for {self_user['display_name']}.

Their intake summary (what they want / avoid):
{json.dumps(self_intake, indent=2)}

They just went on a simulated first date with {other_user['display_name']}.

Scene:
{scene}

Transcript:
{transcript_text}

Write a short advocate reflection with EXACTLY this structure (plain text, no markdown):

GREEN_FLAGS:
- <bullet 1 grounded in transcript>
- <bullet 2 grounded in transcript>

CONCERNS:
- <bullet 1 grounded in transcript and tied to a dealbreaker or boundary>
- <bullet 2 grounded in transcript and tied to a preference mismatch>

NEXT_QUESTION:
<one follow-up question you would ask {self_user['display_name']} in a real intake>

Rules:
- Keep bullets crisp and specific.
- Cite at least one direct behavior or line from the transcript in GREEN_FLAGS and CONCERNS.
"""
        try:
            reflection = await openrouter_client.chat([{"role": "user", "content": prompt}], temperature=0.6)
            reflection = reflection.strip()

            agent.memory.write(
                text=(
                    f"Matchmaker reflection after date with {other_user['display_name']}:\n"
                    f"{reflection}"
                ),
                metadata={
                    "type": "matchmaker_reflection",
                    "partner_user_id": other_user["user_id"],
                    "timestamp": timestamp,
                },
            )
            return reflection
        except Exception:
            return ""

    # -------------------------------------------------------------------------
    # Existing helpers
    # -------------------------------------------------------------------------

    def _extract_intake_summary(self, agent) -> Dict[str, Any]:
        """
        Retrieve intake summary with substring fallback.
        (No dependency on latest_by_type to keep compatibility with your current Memory class.)
        """
        if not agent or not hasattr(agent, "memory") or not hasattr(agent.memory, "search"):
            return {
                "preferences": ["No intake summary available"],
                "dealbreakers": ["No intake summary available"],
                "dating_thesis": "No intake summary available",
            }

        results = agent.memory.search("Intake summary", k=5)
        entry = results[-1] if results else None

        if entry:
            text = entry.get("text", "")
            try:
                start = text.find("{")
                end = text.rfind("}")
                if start != -1 and end != -1 and end > start:
                    return json.loads(text[start : end + 1])
            except Exception:
                pass

        return {
            "preferences": ["No intake summary available"],
            "dealbreakers": ["No intake summary available"],
            "dating_thesis": "No intake summary available",
        }

    def _extract_latest_date_exchange(
        self,
        agent_a,
        agent_b,
        user_a: Dict[str, Any],
        user_b: Dict[str, Any],
    ) -> Optional[str]:
        """
        Find the most recent date_exchange memory text for this pair from either agent.
        Returns the memory text (string) or None.
        """
        candidates: List[Tuple[float, str]] = []

        def collect(agent, partner_id: str):
            if not agent or not hasattr(agent, "memory") or not hasattr(agent.memory, "all"):
                return
            for e in agent.memory.all():
                md = e.get("metadata") or {}
                if md.get("type") != "date_exchange":
                    continue
                if md.get("partner_user_id") and md.get("partner_user_id") != partner_id:
                    continue
                ts = float(md.get("timestamp") or 0.0)
                txt = e.get("text", "")
                if txt:
                    candidates.append((ts, txt))

        collect(agent_a, user_b["user_id"])
        collect(agent_b, user_a["user_id"])

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[0])
        return candidates[-1][1]

    def _extract_short_quote(self, exchange_text: str, max_len: int = 160) -> str:
        """
        Pull a short quote from stored exchange text.
        """
        lines = [ln.strip() for ln in exchange_text.splitlines() if ":" in ln]
        q = lines[-1] if lines else exchange_text.strip()
        q = " ".join(q.split())
        if len(q) > max_len:
            q = q[: max_len - 1].rstrip() + "…"
        return q