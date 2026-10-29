"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for language model providers.

    All LLM providers must implement the `generate` method to produce
    text completions from a given prompt.
    """

    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate a text completion from the given prompt.

        Args:
            prompt: The input prompt to generate a completion for.
            max_tokens: Maximum number of tokens in the response.

        Returns:
            The generated text completion.
        """
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if this provider is available and configured.

        Returns:
            True if the provider can accept requests.
        """
        ...
