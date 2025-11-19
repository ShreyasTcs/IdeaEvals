"""
Idea Evaluator - Uses dynamic rubrics
"""

import json
import logging
from typing import Dict
from llm.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


class IdeaEvaluator:
    """Evaluates ideas using dynamic rubrics"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    def evaluate_idea(
        self,
        idea_data: Dict,
        system_prompt: str,
        user_prompt_template: str,
        rubrics: Dict[str, float]
    ) -> Dict:
        """Evaluate idea using dynamic rubrics"""
        
        # Build rubric criteria text with weights
        rubric_criteria = "RUBRICS AND WEIGHTS (score each criterion 1–10, then use exact weights below):\n"
        for criterion, weight in rubrics.items():
            rubric_criteria += f"- {criterion.replace('_', ' ').title()}: Weight = {weight} ({weight * 100:.1f}%)\n"
        
        rubric_criteria += "\nIMPORTANT – WEIGHTED TOTAL CALCULATION:\n"
        rubric_criteria += "weighted_total = "
        rubric_criteria += " + ".join([f"({weight} × {criterion}_score)" for criterion, weight in rubrics.items()])
        rubric_criteria += "\nExample: If novelty=8, clarity=7, feasibility=6, etc., calculate the exact weighted sum."
        
        # Format user prompt
        user_prompt = user_prompt_template.format(
            rubric_criteria=rubric_criteria,
            idea_title=idea_data.get('idea_title', '')[:500],
            brief_summary=idea_data.get('brief_summary', '')[:2000],
            challenge_opportunity=idea_data.get('challenge_opportunity', '')[:2000],
            novelty_benefits_risks=idea_data.get('novelty_benefits_risks', '')[:2000],
            primary_theme=idea_data.get('primary_theme', 'Not classified'),
            industry_name=idea_data.get('industry_name', 'Not classified'),
            technologies_extracted=str(idea_data.get('technologies_extracted', []))[:500],
            extracted_files_content=idea_data.get('extracted_files_content', '')[:5000]
        )
        
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Call LLM
        response_text = self.llm_provider.generate_text(combined_prompt).strip()
        
        # Clean markdown code block wrappers (if present)
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        logger.info(f"Raw LLM response (first 500 chars): {response_text[:500]}")
        
        # Parse JSON safely
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON: {e}")
            logger.error(f"Response was: {response_text}")
            
            # Fallback default structure if parsing fails
            result = {
                "scores": {
                    criterion: {
                        "score": 5,
                        "justification": "Parsing failed",
                        "insufficient_info": True
                    } for criterion in rubrics.keys()
                },
                "weighted_total": 0.0,
                "investment_recommendation": "consider-with-mitigations",
                "key_strengths": [],
                "key_concerns": ["Evaluation parsing failed"]
            }
        
        # ✅ Recalculate weighted_total to ensure accuracy
        calculated_total = 0.0
        
        # Handle both possible JSON structures
        if "scores" in result:
            # Example structure: {"scores": {"novelty": {"score": 8, ...}, ...}}
            for criterion, weight in rubrics.items():
                score_entry = result["scores"].get(criterion, {})
                if isinstance(score_entry, dict) and "score" in score_entry:
                    try:
                        calculated_total += weight * float(score_entry["score"])
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid score type for {criterion}: {score_entry}")
        else:
            # Alternative structure: {"novelty": {"score": 8, ...}, ...}
            for criterion, weight in rubrics.items():
                score_entry = result.get(criterion, {})
                if isinstance(score_entry, dict) and "score" in score_entry:
                    try:
                        calculated_total += weight * float(score_entry["score"])
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid score type for {criterion}: {score_entry}")
        
        # Set final weighted total
        result["weighted_total"] = round(calculated_total, 2)
        logger.info(f"✅ Calcucllated weighted_total: {result['weighted_total']}")
        
        return result
