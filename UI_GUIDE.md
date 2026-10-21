# 🏦 Loan Application System - UI Guide

## Quick Start

### Option 1: Run the Web UI (Recommended)

```bash
cd "Loan Application"
python3 server.py
```

Then open your browser to: **http://localhost:8000**

### Option 2: Run the Python Demo

```bash
cd "Loan Application"
python3 demo.py
```

---

## Web UI Features

### 📝 Submit Application Tab

**Left Panel - Application Form:**
Fill in the following details about the loan applicant:

1. **Applicant ID** - Unique identifier (e.g., APP001)
2. **Age** - Applicant age (18-100 years)
3. **Annual Income** - Income in dollars
4. **Credit Score** - FICO score (300-850)
5. **Employment Type** - Select from:
   - Employed (full-time job)
   - Self-Employed (business owner)
   - Unemployed
   - Retired

6. **Location** - Select from:
   - New York
   - California
   - Texas
   - Florida
   - Illinois
   - Other

7. **Loan Amount** - Amount requesting in dollars
8. **Loan Tenure** - Repayment period (1-30 years)
9. **Existing Liabilities** - Current debts in dollars

**Buttons:**
- 🚀 **Submit Application** - Process the application
- 🔄 **Clear Form** - Reset all fields
- 📊 **Load Sample Data** - Auto-fill with demo values

### ✅ Decision Result Panel

After submission, shows:

**Decision Badge:**
- 🟢 **APPROVE** (Green) - Application approved
- 🔴 **REJECT** (Red) - Application rejected  
- 🟡 **REVIEW** (Yellow) - Needs manual review

**Key Metrics:**
- **Risk Score** (0-100): Lower is better
  - 0-30: Very safe
  - 30-50: Safe
  - 50-65: Moderate
  - 65-80: High risk
  - 80-100: Very high risk

- **Confidence Level** (0-100%): How certain the system is

**Explanation:**
Detailed reasoning for the decision

**Key Decision Factors:**
List of factors that influenced the decision

**Case ID:** 
Unique identifier for this application (for tracking)

### 📊 Analysis Details Tab

Shows comprehensive financial analysis:

- **Income Stability Score** - Based on employment type and age
- **Employment Risk** - Assessment of job security
- **Debt-to-Income Ratio** - Monthly debt vs monthly income
- **Credit Risk Level** - Based on credit score
- **Loan Amount Risk** - Based on loan-to-income ratio
- **Anomalies** - Any unusual or risky patterns detected

### 📜 History Tab

Shows all previously submitted applications with:
- Applicant ID
- Decision outcome
- Risk score
- Case ID
- Submission timestamp

### 📈 Statistics Tab

System-wide statistics:
- **Total Applications** - Number processed
- **Approved** - Count of approved applications
- **Rejected** - Count of rejected applications
- **Approval Rate** - Percentage of approved vs total

---

## Sample Data to Try

### Application 1: Likely to Approve ✅
```
Applicant ID: GOOD001
Age: 38
Income: $95,000
Employment: Employed
Credit Score: 780
Loan Amount: $250,000
Tenure: 20 years
Liabilities: $30,000
```

**Expected Result:** APPROVE
- Good income stability
- High credit score
- Reasonable debt-to-income ratio
- Risk Score: ~10/100

### Application 2: Likely to Reject ❌
```
Applicant ID: RISKY001
Age: 32
Income: $50,000
Employment: Unemployed
Credit Score: 580
Loan Amount: $400,000
Tenure: 30 years
Liabilities: $200,000
```

**Expected Result:** REJECT
- High existing debt
- Low credit score
- Unemployed status
- Loan much larger than income
- Risk Score: ~85/100

### Application 3: Borderline ⚠️
```
Applicant ID: BORDER001
Age: 45
Income: $120,000
Employment: Self-Employed
Credit Score: 710
Loan Amount: $300,000
Tenure: 25 years
Liabilities: $100,000
```

**Expected Result:** APPROVE or REVIEW
- Self-employed (medium stability)
- Adequate credit score
- Moderate debt levels
- Risk Score: ~45-55/100

---

## Decision Algorithm

### Risk Score Calculation (0-100)

**Base Score:** 50

**Adjustments:**
1. **Income Stability** (-25% of score)
   - Employed, Age 30+: +30 points
   - Employed, Age <30: +10 points
   - Self-Employed: 0 points
   - Unemployed/Retired: -20 points

2. **Employment Risk** (±10-20 points)
   - Low: -10 points
   - Medium: 0 points
   - High: +10 points
   - Very High: +20 points

3. **Debt-to-Income Ratio** (±8-15 points)
   - <30%: -15 points (excellent)
   - 30-50%: -8 points (good)
   - 50-70%: +5 points (acceptable)
   - >70%: +15 points (concerning)

4. **Credit Score Risk** (±5-20 points)
   - Low (750+): -15 points
   - Medium (700-749): -5 points
   - High (650-699): +10 points
   - Very High (<650): +20 points

5. **Loan Amount Risk** (±10-25 points)
   - Low: -10 points
   - Medium: 0 points
   - High: +15 points
   - Very High: +25 points

6. **Anomalies** (+10 per anomaly)
   - Loan >> Annual income
   - Debt-to-income > 70%

**Final Range:** 0-100 (Clamped)

### Decision Classifications

| Risk Score | Decision | Confidence |
|-----------|----------|-----------|
| 0-30 | APPROVE | 95% |
| 30-50 | APPROVE | 75% |
| 50-65 | REVIEW | 80% |
| 65-80 | REJECT | 75% |
| 80-100 | REJECT | 95% |

---

## Tips for Using the System

### ✅ Do's:
- ✓ Use realistic income and credit scores
- ✓ Try different scenarios to understand the logic
- ✓ Check the analysis details to see how decisions are made
- ✓ Review the history to track trends
- ✓ Use Load Sample Data for quick testing

### ❌ Don'ts:
- ✗ Enter invalid age (must be 18-100)
- ✗ Use negative numbers for income or loan amount
- ✗ Credit scores outside 300-850 range
- ✗ Loan tenure > 30 years

### 🎯 Best Practices:

1. **Test Different Profiles:**
   - High income + low debt = Easy approval
   - Low income + high debt = Easy rejection
   - Mixed indicators = Requires analysis

2. **Understand the Metrics:**
   - Risk Score: Overall danger assessment
   - Confidence: How sure the system is
   - Each factor contributes to final decision

3. **Review Key Factors:**
   - Always check the explanation
   - Look at specific factors that influenced decision
   - Use Analysis Details tab for deep dive

4. **Track Applications:**
   - Use History tab to review all submissions
   - Monitor approval rate over time
   - Identify patterns in decisions

---

## System Architecture

The UI connects to a multi-agent AI system with:

1. **Applicant Profile Agent** - Analyzes employment and stability
2. **Financial Risk Agent** - Calculates financial metrics
3. **Loan Decision Agent** - Synthesizes decision
4. **Compliance Agent** - Creates audit trail

All agents work together through an orchestration layer to provide explainable, auditable decisions.

---

## Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
kill -9 <PID>

# Try different port
python3 server.py 8080
```

### Page won't load
- Refresh the browser (Ctrl+R or Cmd+R)
- Clear cache (Ctrl+Shift+Delete)
- Try different browser

### Form submission not working
- Check all required fields are filled
- Verify values are in valid ranges
- Check browser console for errors (F12)

---

## Contact & Support

For issues or questions:
1. Check this guide first
2. Review the SETUP.md for installation help
3. Check ARCHITECTURE.md for system design details
4. See API.md for REST API endpoints

---

**Happy Lending! 🏦💰**
