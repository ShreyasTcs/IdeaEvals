import json
import logging
import re
from typing import Dict
from llm.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

RESPONSE_FORMAT_INSTRUCTION = """
YOUR RESPONSE MUST BE A SINGLE JSON OBJECT.
The JSON object must have the following structure:
{
    "scores": {
        "novelty_and_innovation": {
            "score": <int, 1-10>,
            "justification": "<string>"
        },
        "business_potential_and_impact": {
            "score": <int, 1-10>,
            "justification": "<string>"
        },
        // ... other rubric criteria ...
    },
    "weighted_total": <float>,
    "investment_recommendation": "<string, one of: 'strong-yes', 'consider-with-mitigations', 'no-go'>",
    "key_strengths": ["<string>", ...],
    "key_concerns": ["<string>", ...]
}
Ensure all scores are integers between 1 and 10.
The "weighted_total" will be recalculated by the system, so focus on accurate individual scores.
"""

class IdeaEvaluator:
    """Evaluates ideas using dynamic rubrics"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    def evaluate_idea(
        self,
        idea_data: Dict,
        base_system_prompt: str,
        user_prompt_template: str,
        rubrics: Dict[str, float]
    ) -> Dict:
        """Evaluate idea using dynamic rubrics"""
        
        system_prompt = f"{base_system_prompt}\n\n{RESPONSE_FORMAT_INSTRUCTION}\n\nYOUR ONLY RESPONSE MUST BE THE JSON OBJECT. DO NOT INCLUDE ANY OTHER TEXT, EXPLANATIONS, OR MARKDOWN OUTSIDE THE JSON."
        
        # Adding rubric weights and criteria
        rubric_criteria = "RUBRICS AND WEIGHTS (score each criterion 1-10, then use exact weights below):\n"
        for criterion, weight in rubrics.items():
            rubric_criteria += f"- {criterion.replace('_', ' ').title()}: Weight = {weight} ({weight * 100:.1f}%)\n"
        
        # Add rubric_criteria to the system prompt
        system_prompt += f"\n{rubric_criteria}"
        
        # Log the prompt for debugging
        logger.debug(f"System Prompt: {system_prompt}")
        
        # Get LLM response
        response = self.llm_provider.generate_text(system_prompt)
        
        # Log the response for debugging
        logger.debug(f"LLM Response: {response}")
        
        # Parse and return the response as a dictionary
        try:
            evaluation = json.loads(response)
            return evaluation
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response from LLM: {e}")
            return {"error": "Invalid JSON response from LLM"}
