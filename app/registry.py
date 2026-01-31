"""Registry for demo users and their agents."""

from typing import Dict, List, Any, Optional

from app.agents import MatchmakerAgent, NeutralEvaluatorAgent
from app.users import get_demo_users, get_user_by_id


class AgentRegistry:
    """Singleton registry for managing users and their agents."""

    def __init__(self):
        self._users: List[Dict[str, Any]] = []
        self._matchmakers: Dict[str, MatchmakerAgent] = {}
        self._evaluator: Optional[NeutralEvaluatorAgent] = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize users and create agents."""
        # Load demo users
        self._users = get_demo_users()

        # Create one MatchmakerAgent per user
        for user in self._users:
            user_id = user["user_id"]
            self._matchmakers[user_id] = MatchmakerAgent(
                user_id=user_id,
                user_profile=user
            )

        # Create singleton NeutralEvaluatorAgent
        self._evaluator = NeutralEvaluatorAgent()

    def list_users(self) -> List[Dict[str, Any]]:
        """
        Get all demo users.

        Returns:
            List of user profile dictionaries
        """
        return list(self._users)

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user profile by user_id.

        Args:
            user_id: The user's unique identifier

        Returns:
            User profile dict or None if not found
        """
        for u in self._users:
            if u["user_id"] == user_id:
                return u
        return None

    def get_matchmaker(self, user_id: str) -> Optional[MatchmakerAgent]:
        """
        Get the MatchmakerAgent for a specific user.

        Args:
            user_id: The user's unique identifier

        Returns:
            MatchmakerAgent instance or None if not found
        """
        return self._matchmakers.get(user_id)

    def get_evaluator(self) -> NeutralEvaluatorAgent:
        """
        Get the singleton NeutralEvaluatorAgent.

        Returns:
            NeutralEvaluatorAgent instance
        """
        if self._evaluator is None:
            raise RuntimeError("Evaluator not initialized")
        return self._evaluator


# Global singleton instance
_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """
    Get the global AgentRegistry singleton.

    Returns:
        AgentRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry


# Convenience functions that delegate to the singleton registry

def list_users() -> List[Dict[str, Any]]:
    """Get all demo users."""
    return get_registry().list_users()


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get a user profile by user_id."""
    return get_registry().get_user(user_id)


def get_matchmaker(user_id: str) -> Optional[MatchmakerAgent]:
    """Get the MatchmakerAgent for a specific user."""
    return get_registry().get_matchmaker(user_id)


def get_evaluator() -> NeutralEvaluatorAgent:
    """Get the singleton NeutralEvaluatorAgent."""
    return get_registry().get_evaluator()
