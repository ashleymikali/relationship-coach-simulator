"""Minimal async client for OpenRouter API."""

import os
from typing import Any

import httpx


class OpenRouterClient:
    """Async client for OpenRouter chat completions."""

    def __init__(self):
        self.api_key = os.environ["OPENROUTER_API_KEY"]
        self.model = os.environ["OPENROUTER_MODEL"]
        self.base_url = "https://openrouter.ai/api/v1"

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
    ) -> str:
        """
        Send a chat completion request to OpenRouter.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (0.0 to 2.0)

        Returns:
            The assistant's message text

        Raises:
            KeyError: If required environment variables are not set
            httpx.HTTPError: If the API request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
