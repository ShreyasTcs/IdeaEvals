#!/usr/bin/env python3
"""
Generate detailed verification report for evaluation process
"""

import sys
import json
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.idea_evaluator import IdeaEvaluator
from config.config import GEMINI_API_KEY, DB_CONFIG
import psycopg2


def parse_rubrics(rubrics_data):
    """Helper to parse rubrics from database (handles both string and dict)"""
    if isinstance(rubrics_data, str):
        return json.loads(rubrics_data)
    return rubrics_data


def generate_report():
    """Generate comprehensive verification report"""
    
    report_file = Path("verification/VERIFICATION_REPORT.md")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Evaluation Verification Report\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Section 1: Rubrics Configuration
        f.write("## 1. Rubrics Configuration\n\n")
        rubrics_info = get_rubrics_info()
        f.write(rubrics_info)
        f.write("\n---\n\n")
        
        # Section 2: Sample Evaluation
        f.write("## 2. Sample Evaluation\n\n")
        sample_eval = run_sample_evaluation()
        f.write(sample_eval)
        f.write("\n---\n\n")
        
        # Section 3: Weighted Score Verification
        f.write("## 3. Weighted Score Verification\n\n")
        score_verification = verify_weighted_scores()
        f.write(score_verification)
        f.write("\n---\n\n")
        
        # Section 4: Consistency Analysis
        f.write("## 4. Consistency Analysis\n\n")
        consistency = analyze_consistency()
        f.write(consistency)
        f.write("\n---\n\n")
        
        # Section 5: Edge Cases
        f.write("## 5. Edge Cases Testing\n\n")
        edge_cases = test_edge_cases()
        f.write(edge_cases)
        f.write("\n---\n\n")
        
        # Section 6: Recommendations
        f.write("## 6. Recommendations\n\n")
        f.write(get_recommendations())
        f.write("\n")
    
    print(f"✅ Verification report generated: {report_file}")
    return report_file


def get_rubrics_info():
    """Get rubrics configuration information"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rubric_set_name, version, rubrics, is_active, created_at
            FROM evaluation_rubrics
            WHERE is_active = true
        """)
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            return "❌ No active rubrics found in database.\n"
        
        rubric_name, version, rubrics_json, is_active, created_at = row
        # Handle both string and dict types
        if isinstance(rubrics_json, str):
            rubrics = json.loads(rubrics_json)
        else:
            rubrics = rubrics_json
        
        output = f"**Rubric Set**: {rubric_name}\n"
        output += f"**Version**: {version}\n"
        output += f"**Status**: {'Active' if is_active else 'Inactive'}\n"
        output += f"**Created**: {created_at}\n\n"
        
        output += "### Rubric Criteria and Weights\n\n"
        output += "| Criterion | Weight | Percentage |\n"
        output += "|-----------|--------|------------|\n"
        
        total_weight = sum(rubrics.values())
        for criterion, weight in rubrics.items():
            percentage = (weight / total_weight * 100) if total_weight > 0 else 0
            output += f"| {criterion.replace('_', ' ').title()} | {weight:.2f} | {percentage:.1f}% |\n"
        
        output += f"\n**Total Weight**: {total_weight:.2f}\n"
        
        if abs(total_weight - 1.0) > 0.01:
            output += f"\n⚠️ **Warning**: Total weight is {total_weight:.2f}, expected 1.0\n"
        else:
            output += f"\n✅ **Verified**: Total weight equals 1.0\n"
        
        return output
    
    except Exception as e:
        return f"❌ Error fetching rubrics: {e}\n"


def run_sample_evaluation():
    """Run a sample evaluation and document results"""
    try:
        evaluator = IdeaEvaluator(api_key=GEMINI_API_KEY)
        
        # Get rubrics
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
        
        if not row:
            return "❌ No active rubrics found.\n"
        
        rubrics = parse_rubrics(row[0])
        system_prompt = row[1]
        user_prompt = row[2]
        
        # Test idea
        test_idea = {
            "idea_title": "AI-Powered Code Review Assistant",
            "brief_summary": "An intelligent code review system that uses LLMs to automatically review pull requests, identify bugs, suggest improvements, and ensure coding standards compliance.",
            "challenge_opportunity": "Manual code reviews are time-consuming and inconsistent. This solution automates initial review, allowing developers to focus on complex logic and architecture.",
            "novelty_benefits_risks": "Combines static analysis with LLM understanding of code context. Benefits include faster reviews and consistent standards. Risks include false positives and over-reliance on automation.",
            "primary_theme": "AI in software engineering lifecycle",
            "industry_name": "Technology, Software & Services (TechSS)",
            "technologies_extracted": ["GPT-4", "GitHub API", "Python", "Static Analysis", "CI/CD"],
            "extracted_files_content": "Architecture includes GitHub webhook integration, GPT-4 for semantic analysis, and automated PR comments. Supports multiple languages and custom rule sets."
        }
        
        result = evaluator.evaluate_idea(test_idea, system_prompt, user_prompt, rubrics)
        
        output = f"**Test Idea**: {test_idea['idea_title']}\n\n"
        output += "### Evaluation Results\n\n"
        
        # Individual scores
        output += "#### Individual Scores\n\n"
        output += "| Criterion | Score | Justification |\n"
        output += "|-----------|-------|---------------|\n"
        
        for criterion in rubrics.keys():
            score_data = result.get("scores", {}).get(criterion, {})
            score = score_data.get("score", "N/A")
            justification = score_data.get("justification", "N/A")[:100]
            output += f"| {criterion.replace('_', ' ').title()} | {score}/10 | {justification}... |\n"
        
        # Weighted total
        output += f"\n**Weighted Total**: {result.get('weighted_total', 0):.2f}/10\n\n"
        
        # Investment recommendation
        output += f"**Investment Recommendation**: {result.get('investment_recommendation', 'N/A')}\n\n"
        
        # Strengths and concerns
        output += "#### Key Strengths\n\n"
        for strength in result.get("key_strengths", []):
            output += f"- {strength}\n"
        
        output += "\n#### Key Concerns\n\n"
        for concern in result.get("key_concerns", []):
            output += f"- {concern}\n"
        
        return output
    
    except Exception as e:
        return f"❌ Error running sample evaluation: {e}\n"


def verify_weighted_scores():
    """Verify weighted score calculations"""
    try:
        evaluator = IdeaEvaluator(api_key=GEMINI_API_KEY)
        
        # Get rubrics
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
        
        rubrics = parse_rubrics(row[0])
        system_prompt = row[1]
        user_prompt = row[2]
        
        # Simple test idea
        test_idea = {
            "idea_title": "Test Idea",
            "brief_summary": "A test idea for verification",
            "challenge_opportunity": "Testing",
            "novelty_benefits_risks": "Testing",
            "primary_theme": "Test",
            "industry_name": "Test",
            "technologies_extracted": ["Test"],
            "extracted_files_content": "Test"
        }
        
        result = evaluator.evaluate_idea(test_idea, system_prompt, user_prompt, rubrics)
        
        # Manual calculation
        output = "### Manual Calculation Verification\n\n"
        output += "```\n"
        
        manual_total = 0.0
        for criterion, weight in rubrics.items():
            score_data = result.get("scores", {}).get(criterion, {})
            score = score_data.get("score", 0)
            weighted = weight * score
            manual_total += weighted
            output += f"{criterion:30s}: {weight:.2f} × {score:2d} = {weighted:.2f}\n"
        
        output += f"{'-'*60}\n"
        output += f"{'Manual Total':30s}: {manual_total:.2f}\n"
        output += f"{'LLM Total':30s}: {result.get('weighted_total', 0):.2f}\n"
        output += f"{'Difference':30s}: {abs(manual_total - result.get('weighted_total', 0)):.4f}\n"
        output += "```\n\n"
        
        if abs(manual_total - result.get('weighted_total', 0)) < 0.01:
            output += "✅ **Verification**: Weighted score calculation is accurate (difference < 0.01)\n"
        else:
            output += "⚠️ **Warning**: Weighted score mismatch detected\n"
        
        return output
    
    except Exception as e:
        return f"❌ Error verifying weighted scores: {e}\n"


def analyze_consistency():
    """Analyze consistency across multiple runs"""
    try:
        evaluator = IdeaEvaluator(api_key=GEMINI_API_KEY)
        
        # Get rubrics
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
        
        rubrics = parse_rubrics(row[0])
        system_prompt = row[1]
        user_prompt = row[2]
        
        # Test idea
        test_idea = {
            "idea_title": "Consistency Test Idea",
            "brief_summary": "Testing consistency",
            "challenge_opportunity": "Testing",
            "novelty_benefits_risks": "Testing",
            "primary_theme": "Test",
            "industry_name": "Test",
            "technologies_extracted": ["Test"],
            "extracted_files_content": "Test"
        }
        
        # Run 3 times
        results = []
        for i in range(3):
            result = evaluator.evaluate_idea(test_idea, system_prompt, user_prompt, rubrics)
            results.append(result.get('weighted_total', 0))
        
        output = "### Consistency Test (3 runs)\n\n"
        output += "| Run | Weighted Total |\n"
        output += "|-----|----------------|\n"
        
        for i, total in enumerate(results, 1):
            output += f"| {i} | {total:.2f} |\n"
        
        avg = sum(results) / len(results)
        min_val = min(results)
        max_val = max(results)
        variance = max_val - min_val
        
        output += f"\n**Average**: {avg:.2f}\n"
        output += f"**Range**: {min_val:.2f} - {max_val:.2f}\n"
        output += f"**Variance**: {variance:.2f}\n\n"
        
        if variance < 0.5:
            output += "✅ **Excellent**: Very consistent results (variance < 0.5)\n"
        elif variance < 1.0:
            output += "✅ **Good**: Consistent results (variance < 1.0)\n"
        elif variance < 2.0:
            output += "⚠️ **Acceptable**: Moderate variance (< 2.0)\n"
        else:
            output += "❌ **Concern**: High variance detected (≥ 2.0)\n"
        
        return output
    
    except Exception as e:
        return f"❌ Error analyzing consistency: {e}\n"


def test_edge_cases():
    """Test edge cases"""
    output = "### Edge Case Scenarios\n\n"
    
    edge_cases = [
        {
            "name": "Minimal Information",
            "description": "Idea with very limited details",
            "expected": "Low scores with 'insufficient_info' flags"
        },
        {
            "name": "Excellent Idea",
            "description": "Well-documented, innovative, feasible idea",
            "expected": "High scores (8-10) with strong justifications"
        },
        {
            "name": "Poor Idea",
            "description": "Unclear, unfeasible, or derivative idea",
            "expected": "Low scores (1-4) with clear concerns"
        }
    ]
    
    output += "| Edge Case | Description | Expected Behavior |\n"
    output += "|-----------|-------------|-------------------|\n"
    
    for case in edge_cases:
        output += f"| {case['name']} | {case['description']} | {case['expected']} |\n"
    
    output += "\n**Note**: Run `test_evaluation_verification.py` for detailed edge case testing.\n"
    
    return output


def get_recommendations():
    """Get recommendations for evaluation process"""
    return """### Recommendations for Production Use

1. **Rubric Validation**
   - ✅ Ensure total weights sum to 1.0
   - ✅ Review criterion definitions regularly
   - ✅ Validate against business objectives

2. **Score Verification**
   - ✅ Always recalculate weighted totals server-side
   - ✅ Don't trust LLM calculations blindly
   - ✅ Log discrepancies for analysis

3. **Consistency Monitoring**
   - ✅ Run periodic consistency tests
   - ✅ Monitor score variance over time
   - ✅ Adjust temperature if needed (currently 0.2)

4. **Quality Assurance**
   - ✅ Review sample evaluations manually
   - ✅ Check for hallucination patterns
   - ✅ Validate investment recommendations

5. **Error Handling**
   - ✅ Implement fallback scoring
   - ✅ Log all evaluation failures
   - ✅ Retry with exponential backoff

6. **Audit Trail**
   - ✅ Store raw LLM responses
   - ✅ Track evaluation timestamps
   - ✅ Enable reproducibility

7. **Continuous Improvement**
   - ✅ Collect feedback on evaluations
   - ✅ Refine prompts based on results
   - ✅ Update rubrics as needed
"""


if __name__ == "__main__":
    generate_report()
