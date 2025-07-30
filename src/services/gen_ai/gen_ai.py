from abc import ABC, abstractmethod


class GenAI(ABC):
    @abstractmethod
    def rephrase_post(self, text: str, additional_instructions: str | None = None) -> str:
        """
        Rephrase post text using Gen AI.

        Args:
            text: Original text to rephrase
            additional_instructions: Optional additional instructions for rephrasing

        Returns:
            Rephrased text or empty string if failed
        """
        pass
