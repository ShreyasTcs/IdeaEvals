import json
import logging
import re
from typing import Dict
from llm.llm_provider import LLMProvider

from pathlib import Path

logger = logging.getLogger(__name__)

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
        
        prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        with open(prompts_dir / "scoring_guidelines.txt", "r") as f:
            scoring_rubric = f.read()

        # Prepare data for the prompt
        full_content = f"""
        Summary: {idea_data.get('brief_summary', '')}
        Challenge/Opportunity: {idea_data.get('challenge_opportunity', '')}
        Novelty/Benefits/Risks: {idea_data.get('novelty_benefits_risks', '')}
        Responsible AI: {idea_data.get('responsible_ai', '')}
        """

        prompt_data = {
            "scoring_rubric": scoring_rubric,
            "category_context": "",  # This can be developed further if needed
            "idea_title": idea_data.get('idea_title', ''),
            "idea_description": idea_data.get('brief_summary', ''),
            "idea_category": idea_data.get('primary_theme', 'N/A'),
            "tags_str": ", ".join(idea_data.get('technologies_extracted', [])),
            "full_content": full_content,
            "supporting_materials": idea_data.get('extracted_files_content', 'N/A')
        }

        # Create the user prompt
        user_prompt = user_prompt_template.format(**prompt_data)

        # Combine system and user prompts
        final_prompt = f"{base_system_prompt}\n\n{user_prompt}"
        
        # Log the prompt for debugging
        logger.debug(f"Final Prompt for LLM: {final_prompt}")
        
        # Get LLM response
        response = self.llm_provider.generate_text(final_prompt)
        
        # Log the response for debugging
        logger.debug(f"LLM Response: {response}")
        
        # Parse and return the response as a dictionary
        try:
            # Clean up markdown wrappers if LLM returns JSON inside ``` blocks
            if response.startswith("```json"):
                response = response.replace("```json", "").replace("```", "").strip()
            elif response.startswith("```"):
                response = response.replace("```", "").strip()
            
            evaluation = json.loads(response)
            return evaluation
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response from LLM: {e}\nResponse was: {response}")
            return {"error": "Invalid JSON response from LLM", "raw_response": response}
