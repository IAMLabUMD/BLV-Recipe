"""
LLM Configuration for the recipe pipeline.

Configure which LLM provider and model to use for each step.
Supported providers: 'groq', 'anthropic'
"""

from enum import Enum
from typing import Optional


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    GROQ = "groq"
    ANTHROPIC = "anthropic"


class LLMConfig:
    """Configuration for LLM usage across the pipeline."""

    # Global LLM settings
    DEFAULT_PROVIDER = LLMProvider.GROQ
    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    STEP_CONFIGS = {
        "step2_adapt_recipe": {
            "provider": LLMProvider.GROQ,
            "model": "llama-3.3-70b-versatile",
        },
        "step3_handle_tools": {
            "provider": LLMProvider.GROQ,
            "model": "llama-3.3-70b-versatile",
        },
        "step4_detect_visual_cues": {
            "provider": LLMProvider.GROQ,
            "model": "llama-3.3-70b-versatile",
        },
        "step5_replace_visual_cues": {
            "provider": LLMProvider.GROQ,
            "model": "llama-3.3-70b-versatile",
        },
        "step6_to_accessible_html": {
            "provider": LLMProvider.GROQ,
            "model": "llama-3.3-70b-versatile",
        },
        "step7_add_tool_links": {
            "provider": LLMProvider.GROQ,
            "model": "llama-3.3-70b-versatile",
        },
    }

    @classmethod
    def get_config(cls, step_name: str) -> dict:
        """
        Get LLM configuration for a specific step.

        Args:
            step_name: Name of the pipeline step (e.g., "step2_adapt_recipe")

        Returns:
            Dict with 'provider' and 'model' keys
        """
        if step_name in cls.STEP_CONFIGS:
            return cls.STEP_CONFIGS[step_name]
        return {
            "provider": cls.DEFAULT_PROVIDER,
            "model": cls.DEFAULT_MODEL,
        }

    @classmethod
    def set_step_config(
        cls,
        step_name: str,
        provider: LLMProvider,
        model: str,
    ) -> None:
        """
        Update the LLM configuration for a specific step.

        Args:
            step_name: Name of the pipeline step
            provider: LLM provider to use
            model: Model name to use
        """
        cls.STEP_CONFIGS[step_name] = {
            "provider": provider,
            "model": model,
        }

    @classmethod
    def set_all_steps(
        cls,
        provider: LLMProvider,
        model: str,
    ) -> None:
        """
        Update the LLM configuration for all steps at once.

        Args:
            provider: LLM provider to use
            model: Model name to use
        """
        for step_name in cls.STEP_CONFIGS:
            cls.set_step_config(step_name, provider, model)


# Quick reference for common model names
MODELS = {
    # Groq models
    "llama-3.3-70b": "llama-3.3-70b-versatile",
    "llama-3.1-70b": "llama-3.1-70b-versatile",
    "mixtral-8x7b": "mixtral-8x7b-32768",

    # Anthropic models
    "claude-sonnet-4.6": "claude-sonnet-4-6",
    "claude-opus": "claude-3-5-sonnet-20241022",
    "claude-haiku": "claude-3-5-haiku-20241022",
}
