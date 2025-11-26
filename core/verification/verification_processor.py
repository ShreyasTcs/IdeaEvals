import logging
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)


class VerificationProcessor:
    """
    Processes and verifies a single idea evaluation.
    Compatible with new verification logic.
    """

    def __init__(self, rubrics: List[Dict[str, Any]]):
        self.rubrics = rubrics
        self.passed = 0
        self.failed = 0
        self.warnings = []

    def verify_evaluation(self, evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifies a single evaluation result with comprehensive checks.
        
        Returns:
            {
                "verification_status": "completed" or "failed",
                "checks_passed": int,
                "checks_failed": int,
                "rubric_compliance": {...},
                "json_validity": {...},
                "hallucination_check": {...},
                "consistency_check": {...},
                "warnings": [...]
            }
        """
        if not evaluation_result or "scores" not in evaluation_result:
            return {
                "verification_status": "failed",
                "error": "Invalid evaluation result provided for verification.",
                "checks_passed": 0,
                "checks_failed": 1
            }
        
        verification_report = {}
        self.passed = 0
        self.failed = 0
        self.warnings = []

        # 1. Verify rubric compliance
        rubric_compliance = self._verify_rubric_compliance(evaluation_result)
        verification_report['rubric_compliance'] = rubric_compliance

        # 2. Verify JSON validity
        json_validity = self._verify_json_validity(evaluation_result)
        verification_report['json_validity'] = json_validity

        # 3. Verify no hallucination
        hallucination_check = self._verify_no_hallucination(evaluation_result)
        verification_report['hallucination_check'] = hallucination_check

        # 4. Verify weighted scores (original check, enhanced)
        weighted_score_check = self._verify_weighted_scores(evaluation_result)
        verification_report['weighted_score_verification'] = weighted_score_check

        # 5. Overall status
        verification_report['verification_status'] = 'completed' if self.failed == 0 else 'failed'
        verification_report['checks_passed'] = self.passed
        verification_report['checks_failed'] = self.failed
        verification_report['warnings'] = self.warnings

        return verification_report

    def _verify_rubric_compliance(self, evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Check if all rubric criteria are present in scores"""
        expected_criteria = set()
        for rubric_item in self.rubrics:
            criterion_key = rubric_item.get("name", "").lower().replace(" ", "_")
            expected_criteria.add(criterion_key)
        
        actual_criteria = set(evaluation_result.get("scores", {}).keys())
        missing = expected_criteria - actual_criteria
        
        if missing:
            self.failed += 1
            self.warnings.append(f"Missing criteria: {missing}")
            return {
                "status": "failed",
                "expected_criteria": list(expected_criteria),
                "actual_criteria": list(actual_criteria),
                "missing_criteria": list(missing),
                "is_compliant": False
            }
        else:
            self.passed += 1
            return {
                "status": "passed",
                "expected_criteria": list(expected_criteria),
                "actual_criteria": list(actual_criteria),
                "missing_criteria": [],
                "is_compliant": True
            }

    def _verify_json_validity(self, evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Verify all required fields are present and valid"""
        required_fields = ['scores', 'weighted_total', 'investment_recommendation']
        missing_fields = []
        invalid_fields = []
        
        for field in required_fields:
            if field not in evaluation_result or evaluation_result[field] is None:
                missing_fields.append(field)
        
        # Validate scores structure
        if 'scores' in evaluation_result:
            try:
                scores = evaluation_result['scores']
                if isinstance(scores, str):
                    json.loads(scores)  # Test if valid JSON string
                
                # Validate each score has required structure
                for criterion, score_data in scores.items():
                    if not isinstance(score_data, dict):
                        invalid_fields.append(f"scores.{criterion}")
                    elif 'score' not in score_data:
                        invalid_fields.append(f"scores.{criterion}.score")
                        
            except (json.JSONDecodeError, AttributeError) as e:
                invalid_fields.append(f"scores: {str(e)}")
        
        # Validate arrays if present
        for array_field in ['key_strengths', 'key_concerns']:
            if array_field in evaluation_result:
                value = evaluation_result[array_field]
                if isinstance(value, str):
                    try:
                        json.loads(value)
                    except json.JSONDecodeError:
                        invalid_fields.append(array_field)
        
        if missing_fields or invalid_fields:
            self.failed += 1
            self.warnings.append(f"JSON validation issues: missing={missing_fields}, invalid={invalid_fields}")
            return {
                "status": "failed",
                "missing_fields": missing_fields,
                "invalid_fields": invalid_fields,
                "is_valid": False
            }
        else:
            self.passed += 1
            return {
                "status": "passed",
                "missing_fields": [],
                "invalid_fields": [],
                "is_valid": True
            }

    def _verify_no_hallucination(self, evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Verify scores are reasonable given available information"""
        # Check if minimal information is available
        summary = evaluation_result.get('brief_summary', '')
        challenge = evaluation_result.get('challenge_opportunity', '')
        novelty = evaluation_result.get('novelty_benefits_risks', '')
        files_content = evaluation_result.get('extracted_files_content', '')
        
        has_minimal_info = (
            (not summary or len(summary.strip()) < 50) and
            (not challenge or len(challenge.strip()) < 50) and
            (not novelty or len(novelty.strip()) < 50) and
            (not files_content or len(files_content.strip()) < 100)
        )
        
        suspicious_scores = []
        
        if has_minimal_info:
            scores = evaluation_result.get('scores', {})
            for criterion, score_data in scores.items():
                score = score_data.get('score', 0)
                insufficient_info = score_data.get('insufficient_info', False)
                
                # Flag if score > 7 despite minimal info and not marked as insufficient
                if score > 7 and not insufficient_info:
                    suspicious_scores.append({
                        "criterion": criterion,
                        "score": score,
                        "reason": "High score despite minimal information"
                    })
        
        if suspicious_scores:
            # Warning, not failure
            self.warnings.append(f"Possible hallucination: {len(suspicious_scores)} high scores despite minimal info")
            self.passed += 1  # Don't fail on this
            return {
                "status": "warning",
                "has_minimal_info": has_minimal_info,
                "suspicious_scores": suspicious_scores,
                "is_hallucination_free": False
            }
        else:
            self.passed += 1
            return {
                "status": "passed",
                "has_minimal_info": has_minimal_info,
                "suspicious_scores": [],
                "is_hallucination_free": True
            }

    def _verify_weighted_scores(self, evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifies the weighted score calculation based on the rubrics structure.
        Enhanced version with more detailed checks.
        """
        manual_total = 0.0
        score_breakdown = []
        
        for rubric_item in self.rubrics:
            criterion_key = rubric_item.get("name", "").lower().replace(" ", "_")
            weight = rubric_item.get("weight", 0.0)
            
            score_data = evaluation_result.get("scores", {}).get(criterion_key, {})
            score = score_data.get("score", 0)
            weighted_score = weight * score
            manual_total += weighted_score
            
            score_breakdown.append({
                "criterion": criterion_key,
                "weight": weight,
                "score": score,
                "weighted_score": round(weighted_score, 2)
            })

        llm_total = evaluation_result.get('weighted_total', 0)
        
        # Check for prototype bonus
        content_type = evaluation_result.get('content_type', 'Text')
        prototype_bonus = 2 if content_type == 'Prototype' else 0
        llm_total_before_bonus = llm_total - prototype_bonus

        difference = abs(manual_total - llm_total_before_bonus)
        is_accurate = difference < 0.1  # Tolerance for floating point math

        if is_accurate:
            self.passed += 1
        else:
            self.failed += 1
            self.warnings.append(
                f"Weighted score mismatch: manual={manual_total:.2f}, "
                f"llm={llm_total_before_bonus:.2f}, diff={difference:.2f}"
            )

        return {
            "status": "passed" if is_accurate else "failed",
            "manual_total": round(manual_total, 2),
            "llm_total_before_bonus": round(llm_total_before_bonus, 2),
            "llm_total_final": llm_total,
            "prototype_bonus": prototype_bonus,
            "difference": round(difference, 2),
            "is_accurate": is_accurate,
            "score_breakdown": score_breakdown
        }
