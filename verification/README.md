# Evaluation Verification Suite

Comprehensive verification system to ensure the evaluation process is accurate, consistent, and trustworthy.

## Overview

This verification suite tests the evaluation process against 8 critical criteria:

1. **Rubric Compliance** - LLM follows rubrics correctly
2. **Weighted Score Calculation** - Calculations are mathematically accurate
3. **JSON Validity** - Output is valid and complete JSON
4. **No Hallucination** - No score leakage or fabricated information
5. **Consistency** - Same idea produces consistent results



### `test_evaluation_verification.py`
Main verification test suite that runs all 8 tests.

**Usage:**
```bash
python verification/test_evaluation_verification.py
```

**Output:**
- Detailed test results for each criterion
- Pass/fail status for each test
- Summary with pass rate

### `generate_verification_report.py`
Generates a comprehensive markdown report with:
- Rubrics configuration
- Sample evaluations
- Weighted score verification
- Consistency analysis
- Edge case testing
- Recommendations

**Usage:**
```bash
python verification/generate_verification_report.py
```

**Output:**
- Creates `verification/VERIFICATION_REPORT.md`
- Detailed analysis and recommendations

## Prerequisites

1. **Database Setup**
   ```bash
   python database/setup_rubrics.py
   ```

2. **API Key**
   - Ensure `GEMINI_API_KEY` is configured in `config/config.py`

3. **Dependencies**
   - All standard project dependencies installed

## Running Verification

### Quick Verification
```bash
# Run all tests
python verification/test_evaluation_verification.py
```

### Detailed Report
```bash
# Generate comprehensive report
python verification/generate_verification_report.py

# View report
cat verification/VERIFICATION_REPORT.md
```

## Test Details

### Test 1: Rubric Compliance
**Purpose**: Verify LLM scores all rubric criteria

**Checks**:
- All criteria from rubrics are present in output
- Each criterion has a score
- No missing criteria

**Pass Criteria**: All rubric criteria scored

---

### Test 2: Weighted Score Calculation
**Purpose**: Verify mathematical accuracy of weighted totals

**Checks**:
- Manual calculation vs LLM calculation
- Floating point precision
- Formula correctness

**Pass Criteria**: Difference < 0.01

**Example**:
```
novelty:      0.30 × 8 = 2.40
clarity:      0.34 × 7 = 2.38
feasibility:  0.15 × 6 = 0.90
-----------------------------------
Manual Total:         5.68
LLM Total:           5.68
Difference:          0.00
```

---

### Test 3: JSON Validity
**Purpose**: Ensure output is valid, parseable JSON

**Checks**:
- Valid JSON syntax
- All required fields present
- Proper data types
- Serializable

**Pass Criteria**: Valid JSON with all required fields

**Required Fields**:
- `scores` (object)
- `weighted_total` (number)
- `investment_recommendation` (string)
- `key_strengths` (array)
- `key_concerns` (array)

---

### Test 4: No Hallucination
**Purpose**: Detect fabricated scores or information

**Checks**:
- Scores appropriate for information provided
- No overconfident scoring with minimal data
- Justifications reflect actual content
- `insufficient_info` flag used appropriately

**Pass Criteria**: Appropriate scoring for information quality

**Hallucination Indicators**:
- High scores (>7) with minimal information
- Confident justifications without supporting data
- Missing `insufficient_info` flags

---

### Test 5: Consistency
**Purpose**: Verify reproducible results

**Checks**:
- Run evaluation 3 times on same idea
- Compare weighted totals
- Calculate variance

**Pass Criteria**: Variance < 1.0 point

**Acceptable Ranges**:
- Excellent: variance < 0.5
- Good: variance < 1.0
- Acceptable: variance < 2.0
- Concern: variance ≥ 2.0

---

### Test 6: Score Ranges
**Purpose**: Validate scores are within bounds

**Checks**:
- Individual scores: 1-10
- Weighted total: 0-10
- No negative scores
- No scores > 10

**Pass Criteria**: All scores within valid ranges

---

### Test 7: Required Fields
**Purpose**: Ensure completeness of evaluation

**Checks**:
- Each criterion has: score, justification, insufficient_info
- Top-level fields present
- Arrays not empty
- Proper structure

**Pass Criteria**: All required fields present and populated

**Required per Criterion**:
```json
{
  "score": 7,
  "justification": "Explanation...",
  "insufficient_info": false
}
```

---

### Test 8: Investment Recommendation
**Purpose**: Verify recommendation logic

**Checks**:
- Valid recommendation value
- Alignment with weighted total
- Logical consistency

**Pass Criteria**: Recommendation aligns with score

**Expected Logic**:
- Score ≥ 7.5 → "go"
- Score 5.0-7.5 → "consider-with-mitigations"
- Score < 5.0 → "no-go"

## Interpreting Results

### All Tests Pass ✅
```
📈 Results: 8/8 tests passed (100.0%)
✅ All verification tests passed!
```
**Action**: Evaluation system is production-ready

### Some Tests Fail ⚠️
```
📈 Results: 6/8 tests passed (75.0%)
⚠️ 2 test(s) failed - review details above
```
**Action**: Review failed tests and fix issues before production

### Common Issues

#### Weighted Score Mismatch
**Cause**: LLM calculation error or floating point precision
**Fix**: Server-side recalculation (already implemented)

#### Consistency Issues
**Cause**: High temperature or ambiguous prompts
**Fix**: Lower temperature (currently 0.2) or refine prompts

#### Hallucination
**Cause**: Insufficient information handling
**Fix**: Improve prompt to emphasize `insufficient_info` flag

#### Invalid JSON
**Cause**: LLM output formatting issues
**Fix**: Improve prompt with explicit JSON schema

## Best Practices

### Before Production
1. ✅ Run full verification suite
2. ✅ Generate and review verification report
3. ✅ Test with real data samples
4. ✅ Validate rubrics with stakeholders

### During Production
1. ✅ Monitor evaluation consistency
2. ✅ Log all evaluations for audit
3. ✅ Periodic verification runs
4. ✅ Review edge cases

### After Changes
1. ✅ Re-run verification after rubric changes
2. ✅ Re-run after prompt modifications
3. ✅ Re-run after model updates
4. ✅ Compare before/after results

## Troubleshooting

### Test Failures

**Rubric Compliance Failure**
```
❌ FAIL - Rubric Compliance
Missing criteria: ['security_compliance']
```
**Solution**: Check rubrics in database match evaluation output

**Weighted Score Failure**
```
❌ FAIL - Weighted Score Calculation
Mismatch: Manual=7.2, LLM=7.5
```
**Solution**: Already handled by server-side recalculation

**Consistency Failure**
```
❌ FAIL - Consistency
High variance detected (max diff: 2.3)
```
**Solution**: Lower temperature or refine prompts

### Database Issues

**No Rubrics Found**
```
❌ No active rubrics found in database
```
**Solution**: Run `python database/setup_rubrics.py`

**Connection Error**
```
❌ Error fetching rubrics: connection refused
```
**Solution**: Check PostgreSQL is running and DB_CONFIG is correct

## Continuous Monitoring

### Automated Verification
Add to CI/CD pipeline:
```bash
# In your CI/CD script
python verification/test_evaluation_verification.py
if [ $? -ne 0 ]; then
    echo "Verification failed!"
    exit 1
fi
```

### Periodic Checks
Schedule regular verification:
```bash
# Weekly verification
0 0 * * 0 cd /path/to/project && python verification/test_evaluation_verification.py
```

### Metrics to Track
- Pass rate over time
- Consistency variance trends
- Average weighted scores
- Hallucination incidents
- JSON parsing failures

## Support

For issues or questions:
1. Check test output details
2. Review VERIFICATION_REPORT.md
3. Check logs in `logs/` directory
4. Review rubrics configuration

## Version History

- **v1.0** - Initial verification suite
  - 8 core verification tests
  - Report generation
  - Comprehensive documentation
