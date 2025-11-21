#!/usr/bin/env python3
"""
Comprehensive Verification Tests for Evaluation Process

Tests:
1. LLM follows rubrics correctly
2. Weighted score calculation is accurate
3. Output JSON is valid and complete
4. No hallucination or score leakage
5. Consistent results for same idea
6. Scoring is trustworthy and reproducible
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.idea_evaluator import IdeaEvaluator
from config.config import GEMINI_API_KEY, DB_CONFIG
import psycopg2


class EvaluationVerifier:
    """Comprehensive verification for evaluation process"""
    
    def __init__(self):
        self.evaluator = IdeaEvaluator(api_key=GEMINI_API_KEY)
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    def run_all_tests(self):
        """Run all verification tests"""
        print("\n" + "="*100)
        print("🔍 EVALUATION VERIFICATION SUITE")
        print("="*100 + "\n")
        
        # Test 1: Rubric Compliance
        self.test_rubric_compliance()
        
        # Test 2: Weighted Score Calculation
        self.test_weighted_score_calculation()
        
        # Test 3: JSON Validity
        self.test_json_validity()
        
        # Test 4: No Hallucination
        self.test_no_hallucination()
        
        # Test 5: Consistency
        self.test_consistency()
        
        # Test 6: Score Range Validation
        self.test_score_ranges()
        
        # Test 7: Required Fields
        self.test_required_fields()
        
        # Test 8: Investment Recommendation Logic
        self.test_investment_recommendation()
        
        # Summary
        self.print_summary()
    
    def test_rubric_compliance(self):
        """Test 1: Verify LLM follows rubrics correctly"""
        print("="*100)
        print("TEST 1: Rubric Compliance")
        print("="*100 + "\n")
        
        # Get rubrics from database
        rubrics, system_prompt, user_prompt = self._get_rubrics()
        
        if not rubrics:
            self._record_test("Rubric Compliance", False, "No rubrics found in database")
            return
        
        # Test idea
        test_idea = self._get_test_idea()
        
        try:
            result = self.evaluator.evaluate_idea(
                test_idea, system_prompt, user_prompt, rubrics
            )
            
            # Check if all rubric criteria are scored
            missing_criteria = []
            for criterion in rubrics.keys():
                if "scores" in result:
                    if criterion not in result["scores"]:
                        missing_criteria.append(criterion)
                else:
                    missing_criteria.append(criterion)
            
            if missing_criteria:
                self._record_test(
                    "Rubric Compliance",
                    False,
                    f"Missing criteria: {missing_criteria}"
                )
            else:
                self._record_test(
                    "Rubric Compliance",
                    True,
                    f"All {len(rubrics)} criteria scored"
                )
                print(f"✅ All rubric criteria present and scored")
                for criterion in rubrics.keys():
                    score_data = result["scores"].get(criterion, {})
                    print(f"   - {criterion}: {score_data.get('score', 'N/A')}/10")
        
        except Exception as e:
            self._record_test("Rubric Compliance", False, str(e))
        
        print()
    
    def test_weighted_score_calculation(self):
        """Test 2: Verify weighted score calculation accuracy"""
        print("="*100)
        print("TEST 2: Weighted Score Calculation")
        print("="*100 + "\n")
        
        rubrics, system_prompt, user_prompt = self._get_rubrics()
        test_idea = self._get_test_idea()
        
        try:
            result = self.evaluator.evaluate_idea(
                test_idea, system_prompt, user_prompt, rubrics
            )
            
            # Manual calculation
            manual_total = 0.0
            calculation_steps = []
            
            for criterion, weight in rubrics.items():
                score_data = result["scores"].get(criterion, {})
                score = score_data.get("score", 0)
                weighted = weight * score
                manual_total += weighted
                calculation_steps.append(f"{criterion}: {weight} × {score} = {weighted:.2f}")
            
            manual_total = round(manual_total, 2)
            llm_total = result.get("weighted_total", 0)
            
            print(f"📊 Calculation Verification:")
            for step in calculation_steps:
                print(f"   {step}")
            print(f"\n   Manual Total: {manual_total}")
            print(f"   LLM Total: {llm_total}")
            print(f"   Difference: {abs(manual_total - llm_total):.4f}")
            
            # Allow small floating point difference
            if abs(manual_total - llm_total) < 0.01:
                self._record_test(
                    "Weighted Score Calculation",
                    True,
                    f"Accurate: {llm_total} (diff: {abs(manual_total - llm_total):.4f})"
                )
                print(f"\n✅ Weighted score calculation is accurate")
            else:
                self._record_test(
                    "Weighted Score Calculation",
                    False,
                    f"Mismatch: Manual={manual_total}, LLM={llm_total}"
                )
                print(f"\n❌ Weighted score mismatch detected")
        
        except Exception as e:
            self._record_test("Weighted Score Calculation", False, str(e))
        
        print()
    
    def test_json_validity(self):
        """Test 3: Verify output JSON is valid and complete"""
        print("="*100)
        print("TEST 3: JSON Validity and Completeness")
        print("="*100 + "\n")
        
        rubrics, system_prompt, user_prompt = self._get_rubrics()
        test_idea = self._get_test_idea()
        
        try:
            result = self.evaluator.evaluate_idea(
                test_idea, system_prompt, user_prompt, rubrics
            )
            
            # Verify JSON structure
            required_fields = [
                "scores",
                "weighted_total",
                "investment_recommendation",
                "key_strengths",
                "key_concerns"
            ]
            
            missing_fields = [f for f in required_fields if f not in result]
            
            if missing_fields:
                self._record_test(
                    "JSON Validity",
                    False,
                    f"Missing fields: {missing_fields}"
                )
                print(f"❌ Missing required fields: {missing_fields}")
            else:
                # Verify JSON can be serialized
                json_str = json.dumps(result, indent=2)
                parsed = json.loads(json_str)
                
                self._record_test(
                    "JSON Validity",
                    True,
                    "All required fields present and valid JSON"
                )
                print(f"✅ JSON is valid and complete")
                print(f"   Fields: {', '.join(required_fields)}")
                print(f"   JSON size: {len(json_str)} bytes")
        
        except json.JSONDecodeError as e:
            self._record_test("JSON Validity", False, f"Invalid JSON: {e}")
        except Exception as e:
            self._record_test("JSON Validity", False, str(e))
        
        print()
    
    def test_no_hallucination(self):
        """Test 4: Verify no hallucination or score leakage"""
        print("="*100)
        print("TEST 4: No Hallucination or Score Leakage")
        print("="*100 + "\n")
        
        rubrics, system_prompt, user_prompt = self._get_rubrics()
        
        # Test with minimal information
        minimal_idea = {
            "idea_title": "Simple Test Idea",
            "brief_summary": "A basic idea for testing",
            "challenge_opportunity": "",
            "novelty_benefits_risks": "",
            "primary_theme": "Not classified",
            "industry_name": "Not classified",
            "technologies_extracted": [],
            "extracted_files_content": ""
        }
        
        try:
            result = self.evaluator.evaluate_idea(
                minimal_idea, system_prompt, user_prompt, rubrics
            )
            
            # Check for hallucination indicators
            hallucination_detected = False
            hallucination_reasons = []
            
            # Check if scores are too high for minimal info
            for criterion, score_data in result.get("scores", {}).items():
                score = score_data.get("score", 0)
                insufficient_info = score_data.get("insufficient_info", False)
                
                if score > 7 and not insufficient_info:
                    hallucination_detected = True
                    hallucination_reasons.append(
                        f"{criterion} scored {score}/10 despite minimal info"
                    )
            
            # Check if justifications are generic
            generic_phrases = ["not provided", "insufficient", "unclear", "limited"]
            for criterion, score_data in result.get("scores", {}).items():
                justification = score_data.get("justification", "").lower()
                if not any(phrase in justification for phrase in generic_phrases):
                    if score_data.get("score", 0) > 6:
                        hallucination_detected = True
                        hallucination_reasons.append(
                            f"{criterion} has confident justification despite minimal info"
                        )
            
            if hallucination_detected:
                self._record_test(
                    "No Hallucination",
                    False,
                    "; ".join(hallucination_reasons)
                )
                print(f"❌ Potential hallucination detected:")
                for reason in hallucination_reasons:
                    print(f"   - {reason}")
            else:
                self._record_test(
                    "No Hallucination",
                    True,
                    "Appropriate scoring for minimal information"
                )
                print(f"✅ No hallucination detected")
                print(f"   Scores appropriately reflect limited information")
        
        except Exception as e:
            self._record_test("No Hallucination", False, str(e))
        
        print()
    
    def test_consistency(self):
        """Test 5: Verify consistent results for same idea"""
        print("="*100)
        print("TEST 5: Consistency and Reproducibility")
        print("="*100 + "\n")
        
        rubrics, system_prompt, user_prompt = self._get_rubrics()
        test_idea = self._get_test_idea()
        
        try:
            # Run evaluation 3 times
            results = []
            for i in range(3):
                result = self.evaluator.evaluate_idea(
                    test_idea, system_prompt, user_prompt, rubrics
                )
                results.append(result)
                print(f"   Run {i+1}: Weighted Total = {result.get('weighted_total', 0)}")
            
            # Compare weighted totals
            totals = [r.get("weighted_total", 0) for r in results]
            max_diff = max(totals) - min(totals)
            avg_total = sum(totals) / len(totals)
            
            print(f"\n   Average: {avg_total:.2f}")
            print(f"   Range: {min(totals):.2f} - {max(totals):.2f}")
            print(f"   Max Difference: {max_diff:.2f}")
            
            # Allow some variance due to LLM temperature
            if max_diff < 1.0:  # Less than 1 point difference
                self._record_test(
                    "Consistency",
                    True,
                    f"Consistent results (max diff: {max_diff:.2f})"
                )
                print(f"\n✅ Results are consistent (variance < 1.0)")
            else:
                self._record_test(
                    "Consistency",
                    False,
                    f"High variance detected (max diff: {max_diff:.2f})"
                )
                print(f"\n⚠️  High variance detected (max diff: {max_diff:.2f})")
        
        except Exception as e:
            self._record_test("Consistency", False, str(e))
        
        print()
    
    def test_score_ranges(self):
        """Test 6: Verify scores are within valid ranges"""
        print("="*100)
        print("TEST 6: Score Range Validation")
        print("="*100 + "\n")
        
        rubrics, system_prompt, user_prompt = self._get_rubrics()
        test_idea = self._get_test_idea()
        
        try:
            result = self.evaluator.evaluate_idea(
                test_idea, system_prompt, user_prompt, rubrics
            )
            
            invalid_scores = []
            
            # Check individual scores (1-10)
            for criterion, score_data in result.get("scores", {}).items():
                score = score_data.get("score", 0)
                if not (1 <= score <= 10):
                    invalid_scores.append(f"{criterion}: {score}")
            
            # Check weighted total (0-10)
            weighted_total = result.get("weighted_total", 0)
            if not (0 <= weighted_total <= 10):
                invalid_scores.append(f"weighted_total: {weighted_total}")
            
            if invalid_scores:
                self._record_test(
                    "Score Range Validation",
                    False,
                    f"Invalid scores: {invalid_scores}"
                )
                print(f"❌ Invalid score ranges detected:")
                for invalid in invalid_scores:
                    print(f"   - {invalid}")
            else:
                self._record_test(
                    "Score Range Validation",
                    True,
                    "All scores within valid ranges (1-10)"
                )
                print(f"✅ All scores within valid ranges")
                print(f"   Individual scores: 1-10")
                print(f"   Weighted total: {weighted_total:.2f} (0-10)")
        
        except Exception as e:
            self._record_test("Score Range Validation", False, str(e))
        
        print()
    
    def test_required_fields(self):
        """Test 7: Verify all required fields are present"""
        print("="*100)
        print("TEST 7: Required Fields Validation")
        print("="*100 + "\n")
        
        rubrics, system_prompt, user_prompt = self._get_rubrics()
        test_idea = self._get_test_idea()
        
        try:
            result = self.evaluator.evaluate_idea(
                test_idea, system_prompt, user_prompt, rubrics
            )
            
            # Check required fields in each score
            missing_fields = []
            for criterion in rubrics.keys():
                score_data = result.get("scores", {}).get(criterion, {})
                
                if "score" not in score_data:
                    missing_fields.append(f"{criterion}.score")
                if "justification" not in score_data:
                    missing_fields.append(f"{criterion}.justification")
                if "insufficient_info" not in score_data:
                    missing_fields.append(f"{criterion}.insufficient_info")
            
            # Check top-level fields
            if not result.get("key_strengths"):
                missing_fields.append("key_strengths (empty)")
            if not result.get("key_concerns"):
                missing_fields.append("key_concerns (empty)")
            
            if missing_fields:
                self._record_test(
                    "Required Fields",
                    False,
                    f"Missing: {missing_fields}"
                )
                print(f"❌ Missing required fields:")
                for field in missing_fields:
                    print(f"   - {field}")
            else:
                self._record_test(
                    "Required Fields",
                    True,
                    "All required fields present"
                )
                print(f"✅ All required fields present")
                print(f"   - Scores with justifications")
                print(f"   - Key strengths: {len(result.get('key_strengths', []))}")
                print(f"   - Key concerns: {len(result.get('key_concerns', []))}")
        
        except Exception as e:
            self._record_test("Required Fields", False, str(e))
        
        print()
    
    def test_investment_recommendation(self):
        """Test 8: Verify investment recommendation logic"""
        print("="*100)
        print("TEST 8: Investment Recommendation Logic")
        print("="*100 + "\n")
        
        rubrics, system_prompt, user_prompt = self._get_rubrics()
        test_idea = self._get_test_idea()
        
        try:
            result = self.evaluator.evaluate_idea(
                test_idea, system_prompt, user_prompt, rubrics
            )
            
            weighted_total = result.get("weighted_total", 0)
            recommendation = result.get("investment_recommendation", "")
            
            valid_recommendations = ["go", "consider-with-mitigations", "no-go"]
            
            # Check if recommendation is valid
            if recommendation not in valid_recommendations:
                self._record_test(
                    "Investment Recommendation",
                    False,
                    f"Invalid recommendation: {recommendation}"
                )
                print(f"❌ Invalid recommendation: {recommendation}")
            else:
                # Check if recommendation aligns with score
                expected = None
                if weighted_total >= 7.5:
                    expected = "go"
                elif weighted_total >= 5.0:
                    expected = "consider-with-mitigations"
                else:
                    expected = "no-go"
                
                if recommendation == expected:
                    self._record_test(
                        "Investment Recommendation",
                        True,
                        f"{recommendation} aligns with score {weighted_total:.2f}"
                    )
                    print(f"✅ Recommendation aligns with score")
                    print(f"   Score: {weighted_total:.2f}")
                    print(f"   Recommendation: {recommendation}")
                else:
                    self._record_test(
                        "Investment Recommendation",
                        False,
                        f"Mismatch: {recommendation} for score {weighted_total:.2f} (expected {expected})"
                    )
                    print(f"⚠️  Recommendation may not align with score")
                    print(f"   Score: {weighted_total:.2f}")
                    print(f"   Recommendation: {recommendation}")
                    print(f"   Expected: {expected}")
        
        except Exception as e:
            self._record_test("Investment Recommendation", False, str(e))
        
        print()
    
    def _get_rubrics(self):
        """Get rubrics from database"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT rubrics, system_prompt, user_prompt_template
                FROM evaluation_rubrics
                WHERE is_active = true
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                # Handle both string and dict types for rubrics
                rubrics = row[0]
                if isinstance(rubrics, str):
                    rubrics = json.loads(rubrics)
                return rubrics, row[1], row[2]
            else:
                return None, None, None
        
        except Exception as e:
            print(f"❌ Error fetching rubrics: {e}")
            return None, None, None
    
    def _get_test_idea(self):
        """Get a test idea for evaluation"""
        return {
            "idea_title": "AI-Powered Smart Waste Management System",
            "brief_summary": "An intelligent waste sorting system using computer vision and edge AI to automatically classify waste into recyclable, biodegradable, and non-recyclable categories at the point of disposal.",
            "challenge_opportunity": "Current waste management systems rely on manual sorting, leading to contamination and low recycling rates. This solution addresses the challenge by automating waste classification at source.",
            "novelty_benefits_risks": "Novel use of edge AI for real-time waste classification. Benefits include improved recycling rates, reduced contamination, and cost savings. Risks include accuracy in diverse lighting conditions and maintenance requirements.",
            "primary_theme": "Edge AI",
            "industry_name": "Consumer Business (Retail & CPG)",
            "technologies_extracted": ["Computer Vision", "Edge AI", "TensorFlow Lite", "Raspberry Pi", "Camera sensors"],
            "extracted_files_content": "Technical architecture includes edge devices with camera sensors, TensorFlow Lite models for classification, and cloud backend for analytics. Prototype demonstrates 92% accuracy in controlled environment."
        }
    
    def _record_test(self, test_name: str, passed: bool, details: str):
        """Record test result"""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        """Print test summary"""
        print("="*100)
        print("📊 VERIFICATION SUMMARY")
        print("="*100 + "\n")
        
        for result in self.test_results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status} - {result['test']}")
            print(f"       {result['details']}\n")
        
        print("="*100)
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n📈 Results: {self.passed}/{total} tests passed ({pass_rate:.1f}%)")
        
        if self.failed == 0:
            print("✅ All verification tests passed!")
        else:
            print(f"⚠️  {self.failed} test(s) failed - review details above")
        
        print("\n" + "="*100 + "\n")


def main():
    """Run verification suite"""
    verifier = EvaluationVerifier()
    verifier.run_all_tests()


if __name__ == "__main__":
    main()
