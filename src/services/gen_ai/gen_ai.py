from abc import ABC, abstractmethod


class GenAI(ABC):
    @abstractmethod
    def rephrase_post(self, text: str, additional_instructions: str | None = None) -> str:
        pass
