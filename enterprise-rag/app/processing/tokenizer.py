"""
Token Counter and Text Length Estimation
"""

import re
import logging

logger = logging.getLogger(__name__)


class TokenCounter:
    """
    Estimate token counts for various LLM models
    Supports OpenAI, Anthropic, and other models
    """

    # Model-specific token estimation factors
    MODEL_CONFIGS = {
        "gpt-4": {"avg_chars_per_token": 4},
        "gpt-3.5-turbo": {"avg_chars_per_token": 4},
        "claude-3-opus": {"avg_chars_per_token": 3.8},
        "claude-3-sonnet": {"avg_chars_per_token": 3.8},
        "mistral": {"avg_chars_per_token": 4},
    }

    @staticmethod
    def count_tokens(text: str, model: str = "gpt-4") -> int:
        """
        Estimate token count for text

        Args:
            text: Text to count
            model: Model name for accurate counting

        Returns:
            Estimated token count
        """
        if not text:
            return 0

        config = TokenCounter.MODEL_CONFIGS.get(model, {"avg_chars_per_token": 4})
        chars_per_token = config["avg_chars_per_token"]

        # Split by whitespace and punctuation for more accurate count
        tokens = len(re.findall(r"\b\w+\b|[^\w\s]", text))

        return max(tokens, len(text) // int(chars_per_token))

    @staticmethod
    def estimate_tokens_from_chars(char_count: int, model: str = "gpt-4") -> int:
        """
        Quick token estimation from character count

        Args:
            char_count: Number of characters
            model: Model name

        Returns:
            Estimated token count
        """
        config = TokenCounter.MODEL_CONFIGS.get(model, {"avg_chars_per_token": 4})
        chars_per_token = config["avg_chars_per_token"]
        return max(1, char_count // int(chars_per_token))

    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        return len(text.split())

    @staticmethod
    def count_sentences(text: str) -> int:
        """Count sentences in text"""
        sentences = re.split(r"[.!?]+", text)
        return sum(1 for s in sentences if s.strip())
