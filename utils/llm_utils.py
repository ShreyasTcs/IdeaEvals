import json
from typing import Dict
from llm.llm_provider import LLMProvider

def call_llm(llm_provider: LLMProvider, system_message: str, user_message: str) -> str:
    """Call LLM with system and user messages"""
    combined_prompt = f"{system_message}\n\n{user_message}\n\nIMPORTANT: Return ONLY valid JSON."
    response = llm_provider.generate_text(combined_prompt)
    text = response.strip()

    # Clean up markdown wrappers if LLM returns JSON inside ``` blocks
    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    return text

def parse_json(response: str) -> Dict:
    """Safely parse JSON from LLM output"""
    try:
        data = json.loads(response)
        if isinstance(data, list):  # Handle list wrapping
            data = data[0]
        if not isinstance(data, dict):
            raise ValueError("Invalid JSON structure returned by LLM.")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ LLM returned invalid JSON: {e}\nResponse: {response}")
