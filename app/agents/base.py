"""Base agent class for the agentic matchmaking system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Memory:
    """Simple memory interface for agents (placeholder for Letta-backed memory)."""

    def __init__(self):
        self._entries: List[Dict[str, Any]] = []
        self._metadata: Dict[str, Any] = {}

    def write(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Write a memory entry."""
        self._entries.append({"text": text, "metadata": metadata or {}})

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Naive placeholder search (substring match).
        Replace with Letta / vector search later.
        """
        q = query.lower().strip()
        hits = [e for e in self._entries if q in str(e.get("text", "")).lower()]
        return hits[:k]

    # Improvement A: metadata-based retrieval (reliable, avoids brittle substring matching)
    def search_metadata(self, key: str, value: Any, k: int = 5) -> List[Dict[str, Any]]:
        """
        Return up to k entries whose metadata[key] == value.
        This is a very reliable stand-in for "type filters" before Letta.
        """
        hits: List[Dict[str, Any]] = []
        for e in reversed(self._entries):  # newest-first
            md = e.get("metadata") or {}
            if md.get(key) == value:
                hits.append(e)
                if len(hits) >= k:
                    break
        return hits

    def latest_by_type(self, entry_type: str) -> Optional[Dict[str, Any]]:
        """Convenience: newest entry where metadata['type'] == entry_type."""
        hits = self.search_metadata("type", entry_type, k=1)
        return hits[0] if hits else None

    def all(self) -> List[Dict[str, Any]]:
        """Return all memory entries."""
        return list(self._entries)

    def set_metadata(self, key: str, value: Any) -> None:
        self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self._metadata.get(key, default)

    def clear(self) -> None:
        self._entries.clear()
        self._metadata.clear()


class BaseAgent(ABC):
    """Abstract base class for all agents in the system."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.memory = Memory()

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Any:
        """Process input and return output."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', role='{self.role}')"
