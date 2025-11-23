import json
import logging
from typing import Dict, Any, List

from llm.llm_provider import LLMProvider
from pathlib import Path

logger = logging.getLogger(__name__)

class IdeaEvaluator:
    """Evaluates ideas using dynamic rubrics"""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def _format_rubrics_for_prompt(self, rubrics: List[Dict[str, Any]]) -> str:
        """Formats the rubrics from a list of dicts into a string for the LLM prompt."""
        if not rubrics:
            return "No rubrics provided."

        formatted_rubrics = ["EXPERT EVALUATION CRITERIA & QUESTIONS (weights in parentheses):"]
        
        # Find the scoring scale from the first rubric item, assuming it's consistent
        # Default if not found
        scoring_scale = rubrics[0].get('scoring_scale_anchor', "9–10 Outstanding | 7–8 Strong | 5–6 Fair | 3–4 Weak | 1–2 Poor")

        for i, rubric in enumerate(rubrics, 1):
            name = rubric.get('name', 'Unnamed Criterion').upper()
            weight = int(rubric.get('weight', 0) * 100)
            description = rubric.get('description', 'No description available.')
            
            formatted_rubrics.append(f"{i}) {name} ({weight}%)")
            formatted_rubrics.append(f"   - {description}")

        formatted_rubrics.append(f"\nSCORING SCALE ANCHORS (1–10): {scoring_scale}")
        
        return "\n".join(formatted_rubrics)

    def evaluate_idea(
        self,
        idea_data: Dict,
        base_system_prompt: str,
        user_prompt_template: str,
        rubrics: List[Dict[str, Any]]
    ) -> Dict:
        """Evaluate idea using dynamic rubrics"""
        
        prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        with open(prompts_dir / "scoring_guidelines.txt", "r", encoding='utf-8') as f:
            scoring_rubric = f.read()

        # Format rubrics for the prompt
        rubrics_str = self._format_rubrics_for_prompt(rubrics)

        # Prepare data for the prompt
        full_content = f"""
        Summary: {idea_data.get('brief_summary', '')}
        Challenge/Opportunity: {idea_data.get('challenge_opportunity', '')}
        Novelty/Benefits/Risks: {idea_data.get('novelty_benefits_risks', '')}
        Responsible AI: {idea_data.get('responsible_ai', '')}
        """

        prompt_data = {
            "rubrics": rubrics_str,
            "scoring_rubric": scoring_rubric,
            "category_context": "",  # This can be developed further if needed
            "idea_title": idea_data.get('idea_title', ''),
            "idea_description": idea_data.get('brief_summary', ''),
            "idea_category": idea_data.get('primary_theme', 'N/A'),
            "content_type": idea_data.get('content_type', 'Text'),
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
