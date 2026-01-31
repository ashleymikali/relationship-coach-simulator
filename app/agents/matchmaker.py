"""Matchmaker agent - represents one user's perspective in the dating simulation."""

import json
import time
from typing import Any, Dict

from app.agents.base import BaseAgent


def extract_json(text: str) -> Any:
    """Best-effort extraction of a JSON object from an LLM response."""
    t = text.strip()

    # Remove markdown code fences if present
    if t.startswith("```"):
        lines = t.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()

    # Extract the first {...} block
    start = t.find("{")
    end = t.rfind("}")
    if start != -1 and end != -1 and end > start:
        t = t[start : end + 1]

    return json.loads(t)


class MatchmakerAgent(BaseAgent):
    """
    Agent representing a single user's matchmaking perspective.
    
    Each user gets their own MatchmakerAgent that advocates for their
    preferences, simulates their behavior on dates, and evaluates compatibility.
    """

    def __init__(self, user_id: str, user_profile: Dict[str, Any]):
        """
        Initialize a matchmaker agent for a specific user.

        Args:
            user_id: Unique identifier for the user
            user_profile: User's profile data (preferences, personality, etc.)
        """
        super().__init__(
            name=f"Matchmaker_{user_id}",
            role=f"Advocate and simulator for user {user_id}"
        )
        self.user_id = user_id
        self.user_profile = user_profile
        self.memory.set_metadata("user_id", user_id)
        self.memory.set_metadata("profile", user_profile)

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process matchmaking tasks.

        Args:
            input_data: Task data (e.g., simulate_date, evaluate_match)

        Returns:
            Processing results
        """
        # Placeholder - business logic will be added later
        task_type = input_data.get("task_type", "unknown")
        
        return {
            "agent": self.name,
            "user_id": self.user_id,
            "task_type": task_type,
            "status": "not_implemented",
            "message": f"MatchmakerAgent for {self.user_id} received task: {task_type}"
        }

    async def run_intake_summary(
        self, 
        openrouter_client,
        extra_context: str | None = None
    ) -> Dict[str, Any]:
        """
        Generate an intake summary for this user using OpenRouter.
        
        Args:
            openrouter_client: OpenRouterClient instance
            extra_context: Optional live intake notes from Q&A session
            
        Returns:
            Parsed summary dict with preferences, dealbreakers, and dating_thesis
        """
        user = self.user_profile
        
        # Build base prompt
        prompt = f"""You are analyzing a dating profile for intake. Based on this profile, generate a structured summary.

User Profile:
- Name: {user['display_name']}
- Bio: {user['bio']}
- Traits: {', '.join(user['traits'])}
- Boundaries: {', '.join(user['boundaries'])}"""

        # Add live intake notes if provided
        if extra_context:
            prompt += f"""

Live Intake Notes (Q/A):
{extra_context}"""

        # Add JSON structure requirements
        prompt += """

Generate a JSON response with this exact structure:
{
  "preferences": [
    "preference 1",
    "preference 2",
    "preference 3",
    "preference 4",
    "preference 5",
    "preference 6"
  ],
  "dealbreakers": [
    "dealbreaker 1",
    "dealbreaker 2",
    "dealbreaker 3"
  ],
  "dating_thesis": "One sentence summarizing their dating philosophy and what they're looking for"
}

Rules:
- Return ONLY valid JSON (no markdown, no extra text).
- Be specific and insightful. Infer preferences from traits/bio/boundaries.
- If Live Intake Notes are provided, incorporate those insights into the summary.
"""
        
        messages = [{"role": "user", "content": prompt}]
        response_text = await openrouter_client.chat(messages, temperature=0.7)
        
        try:
            summary = extract_json(response_text)
            
            # Light validation / normalization
            if not isinstance(summary, dict):
                raise ValueError("Parsed JSON is not an object")
            
            summary.setdefault("preferences", [])
            summary.setdefault("dealbreakers", [])
            summary.setdefault("dating_thesis", "")
            
        except Exception:
            # Fallback if LLM doesn't return valid JSON
            summary = {
                "preferences": ["Unable to parse preferences"],
                "dealbreakers": ["Unable to parse dealbreakers"],
                "dating_thesis": response_text.strip()[:240],
            }
        
        # Store in agent memory
        self.memory.write(
            text=f"Intake summary for {user['display_name']}: {json.dumps(summary)}",
            metadata={
                "type": "intake_summary",
                "user_id": self.user_id,
                "timestamp": time.time(),
            },
        )
        
        return summary
