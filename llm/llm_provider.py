from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """
    Abstract base class for a generic Language Model Provider.
    """
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """
        Generates text based on a given prompt.

        Args:
            prompt (str): The input prompt for the language model.

        Returns:
            str: The generated text.
        """
        pass
