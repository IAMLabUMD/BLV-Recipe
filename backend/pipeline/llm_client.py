"""
Unified LLM client that supports multiple providers (Groq, Anthropic).

This module provides a single interface for making LLM calls regardless of
the underlying provider, making it easy to switch providers without changing
step logic.
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

from pipeline.config import LLMProvider, LLMConfig


class LLMClient:
    """
    Unified client for making LLM calls with any supported provider.

    Usage:
        config = LLMConfig.get_config("step2_adapt_recipe")
        client = LLMClient.from_config(config)
        response = client.chat(
            system="You are a helpful assistant.",
            user_message="Hello!",
        )
    """

    def __init__(
        self,
        provider: LLMProvider,
        model: str,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the LLM client.

        Args:
            provider: LLM provider (groq, anthropic)
            model: Model name
            api_key: API key (if not provided, loaded from env)
        """
        self.provider = provider
        self.model = model
        self._client = None

        # Load env vars if needed
        load_dotenv()

        # Get API key
        if api_key:
            self.api_key = api_key
        else:
            if provider == LLMProvider.GROQ:
                self.api_key = os.getenv("GROQ_API_KEY")
                if not self.api_key:
                    raise RuntimeError("GROQ_API_KEY not set in .env")
            elif provider == LLMProvider.ANTHROPIC:
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
                if not self.api_key:
                    raise RuntimeError("ANTHROPIC_API_KEY not set in .env")
            else:
                raise ValueError(f"Unknown provider: {provider}")

        self._init_client()

    @classmethod
    def from_config(
        cls,
        config: dict,
        api_key: Optional[str] = None,
    ) -> LLMClient:
        """
        Create an LLM client from a configuration dict.

        Args:
            config: Dict with 'provider' and 'model' keys
            api_key: Optional API key

        Returns:
            LLMClient instance
        """
        return cls(
            provider=config["provider"],
            model=config["model"],
            api_key=api_key,
        )

    @classmethod
    def from_step_name(cls, step_name: str, api_key: Optional[str] = None) -> LLMClient:
        """
        Create an LLM client for a specific pipeline step.

        Args:
            step_name: Name of the pipeline step
            api_key: Optional API key

        Returns:
            LLMClient instance
        """
        config = LLMConfig.get_config(step_name)
        return cls.from_config(config, api_key)

    def _init_client(self) -> None:
        """Initialize the underlying client."""
        if self.provider == LLMProvider.GROQ:
            from groq import Groq
            self._client = Groq(api_key=self.api_key)
        elif self.provider == LLMProvider.ANTHROPIC:
            from anthropic import Anthropic
            self._client = Anthropic(api_key=self.api_key)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def chat(
        self,
        system: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Send a chat message and get a response.

        Args:
            system: System prompt
            user_message: User message
            temperature: Temperature for sampling (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Response text
        """
        if self.provider == LLMProvider.GROQ:
            return self._chat_groq(system, user_message, temperature, max_tokens)
        elif self.provider == LLMProvider.ANTHROPIC:
            return self._chat_anthropic(system, user_message, temperature, max_tokens)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _chat_groq(
        self,
        system: str,
        user_message: str,
        temperature: float,
        max_tokens: Optional[int],
    ) -> str:
        """Make a Groq API call."""
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_message}
        ]

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        response = self._client.chat.completions.create(**kwargs)

        return response.choices[0].message.content

    def _chat_anthropic(
        self,
        system: str,
        user_message: str,
        temperature: float,
        max_tokens: Optional[int],
    ) -> str:
        """Make an Anthropic API call."""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens or 6096,
            "system": system,
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "temperature": temperature,
        }

        response = self._client.messages.create(**kwargs)

        return response.content[0].text


# For backwards compatibility with existing code
def build_llm_client(step_name: str) -> LLMClient:
    """
    Create an LLM client for a pipeline step.

    This function is provided for backwards compatibility.

    Args:
        step_name: Name of the pipeline step

    Returns:
        LLMClient instance
    """
    return LLMClient.from_step_name(step_name)
