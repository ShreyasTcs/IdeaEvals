import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class VerificationProcessor:
    """
    Processes and verifies a single idea evaluation.
    """

    def __init__(self, rubrics: List[Dict[str, Any]]):
        self.rubrics = rubrics

    def verify_evaluation(self, evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifies a single evaluation result.
        """
        if not evaluation_result or "scores" not in evaluation_result:
            return {"error": "Invalid evaluation result provided for verification."}
            
        verification_report = {}

        # 1. Verify weighted scores
        weighted_score_verification = self._verify_weighted_scores(evaluation_result)
        verification_report['weighted_score_verification'] = weighted_score_verification

        # More verification steps can be added here.

        return verification_report

    def _verify_weighted_scores(self, evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifies the weighted score calculation based on the new rubrics structure.
        """
        manual_total = 0.0
        for rubric_item in self.rubrics:
            # The key for the scores dict should be the lowercase name without spaces
            criterion_key = rubric_item.get("name", "").lower().replace(" ", "_")
            weight = rubric_item.get("weight", 0.0)
            
            score_data = evaluation_result.get("scores", {}).get(criterion_key, {})
            score = score_data.get("score", 0)
            manual_total += weight * score

        llm_total = evaluation_result.get('weighted_total', 0)
        
        # Check for prototype bonus
        content_type = evaluation_result.get('content_type', 'Text')
        llm_total_before_bonus = llm_total
        if content_type == 'Prototype':
            llm_total_before_bonus -= 2

        difference = abs(manual_total - llm_total_before_bonus)

        return {
            "manual_total": round(manual_total, 2),
            "llm_total_before_bonus": round(llm_total_before_bonus, 2),
            "llm_total_final": llm_total,
            "difference": round(difference, 2),
            "is_accurate": difference < 0.1 # Loosen tolerance slightly for float math
        }
