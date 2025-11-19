import google.generativeai as genai
from llm.llm_provider import LLMProvider

class GeminiProvider(LLMProvider):
    """
    LLM Provider implementation for Google Gemini.
    """
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model
        self._client = None

    def _get_client(self):
        """
        Lazy loads the Gemini client.
        """
        if self._client is None:
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model_name)
        return self._client

    def generate_text(self, prompt: str) -> str:
        """
        Generates text using the Gemini model.

        Args:
            prompt (str): The input prompt.

        Returns:
            str: The generated text.
        """
        client = self._get_client()
        response = client.generate_content(prompt)
        return response.text
