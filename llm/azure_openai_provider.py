from llm.llm_provider import LLMProvider

class AzureOpenAIProvider(LLMProvider):
    """
    Placeholder for Azure OpenAI provider.
    """
    def __init__(self, api_key: str, endpoint: str, deployment_name: str):
        # Initialization for Azure OpenAI would go here
        raise NotImplementedError("AzureOpenAIProvider is not yet implemented.")

    def generate_text(self, prompt: str) -> str:
        """
        Generates text using Azure OpenAI.
        """
        raise NotImplementedError("AzureOpenAIProvider is not yet implemented.")
