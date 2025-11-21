import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from llm.llm_provider import LLMProvider

load_dotenv()  # Load environment variables from .env file

class AzureOpenAIProvider(LLMProvider):
    """
    LLM Provider implementation for Azure OpenAI.
    """
    def __init__(self):
        """
        Initialize the AzureOpenAIProvider.
        The API key, model, and endpoint are loaded from environment variables.
        """
        # Load environment variables from .env
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.model_name = os.getenv("AZURE_OPENAI_MODEL", "gpt-4")  # Default to "gpt-4"
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01")  # Default to current version
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self._client = None

        if not all([self.api_key, self.azure_endpoint]):
            raise ValueError("Missing required environment variables: AZURE_OPENAI_API_KEY or AZURE_OPENAI_ENDPOINT")

    def _get_client(self):
        """
        Lazy loads the Azure OpenAI client.
        
        Returns:
            AzureOpenAI: The Azure OpenAI client instance.
        """
        if self._client is None:
            self._client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.azure_endpoint
            )
        return self._client

    def generate_text(self, prompt: str) -> str:
        """
        Generates text using the Azure OpenAI model.

        Args:
            prompt (str): The input prompt.

        Returns:
            str: The generated text.
        """
        client = self._get_client()
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error generating text: {e}")
            return None
