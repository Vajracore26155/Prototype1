# User Guide: Downloading PDF Audit Reports

## Quick Start

### How to Download an Audit Report

1. **Navigate to your audit results**
   - From the Dashboard or Configurations page
   - Click on any completed audit

2. **Click "Download Report"**
   - Located in the top-right corner of the page
   - Blue button with download icon 📥

3. **Wait for generation**
   - Button changes to "Generating..."
   - Takes 1-2 seconds

4. **PDF downloads automatically**
   - Saved to your browser's default download location
   - Filename: `audit_report_[ID]_[config-name].pdf`

---

## What's in the Report?

### 📄 Cover Page
- Audit ID and configuration name
- Vendor information
- Report generation date
- Current status

### 📊 Executive Summary
- **Compliance Score** - Overall percentage
- **Risk Level** - Critical/High/Medium/Low
- **Findings Summary** - Count by severity
- **Pass/Fail Statistics**

### ⚠️ Human Intervention Alert (if needed)
When the system couldn't interpret parts of your configuration:
- **Warning banner** explaining why
- **Interpretation confidence** percentage
- **Uninterpreted lines** count
- **Recommended action** - Review suggested AI mappings

### 🔍 Detailed Findings
For each security issue found:
- **Severity Level** - Color-coded badge
- **Rule Name and ID** - What was checked
- **Description** - Why it matters
- **Expected vs Actual** - What should be vs what is
- **Evidence** - Exact line from your config
- **Recommended Fix** - Command to resolve issue
- **Risk Score** - Impact assessment

### ✅ Passed Controls
Summary of security controls that passed

---

## When to Download Reports

### ✅ Best Practices

**Download reports when**:
- Completing a security audit cycle
- Preparing for compliance reviews
- Documenting security posture
- Sharing findings with team members
- Archiving historical audit results
- Presenting to management

**Report includes everything needed for**:
- Security documentation
- Compliance evidence
- Audit trails
- Remediation planning
- Executive briefings

---

## Understanding Report Indicators

### Status Badges

| Status | Meaning |
|--------|---------|
| **COMPLETED** 🟢 | Audit finished successfully |
| **NEEDS_REVIEW** 🟡 | Manual validation required |
| **PROCESSING** 🔵 | Currently running |
| **FAILED** 🔴 | Audit encountered an error |

### Severity Colors

| Severity | Color | Action |
|----------|-------|--------|
| **CRITICAL** | 🔴 Red | Fix immediately |
| **HIGH** | 🟠 Orange | Fix within 24 hours |
| **MEDIUM** | 🟡 Yellow | Fix within 1 week |
| **LOW** | 🟢 Green | Fix when convenient |

### Risk Levels

- **CRITICAL** - Severe security vulnerabilities, exploit likely
- **HIGH** - Significant risks, should be addressed urgently
- **MEDIUM** - Moderate risks, plan remediation
- **LOW** - Minor issues, good practice to fix

---

## Reading the Human Intervention Alert

If your report shows a **yellow warning banner**, it means:

### Why This Appears
Your configuration uses **proprietary or uncommon syntax** that our AI couldn't interpret with high confidence.

### What the Metrics Mean

**Interpretation Confidence: 2.0%**
- Only 2% of your config matched known patterns
- Lower = more unusual syntax

**Uninterpreted Lines: 145 / 148**
- 145 lines couldn't be mapped to security controls
- These lines need human expert review

**Pending AI Mappings: 12**
- AI has 12 suggestions for interpreting your config
- You should review and approve/reject these

### What You Should Do

1. **Review the findings** - They're based on best-effort interpretation
2. **Check AI mappings** - Go to the Learning page
3. **Approve accurate mappings** - Help the system learn
4. **Reject incorrect ones** - Prevent future errors
5. **Re-run the audit** - After approving mappings for better results

---

## Sharing Reports

### ✅ Reports are Safe to Share

- **No sensitive data** - All IPs, passwords, and secrets are masked
- **Professional format** - Suitable for stakeholders
- **Comprehensive** - Contains all needed context

### Who Should Get Reports?

**Internal**:
- Security team members
- Network administrators
- Compliance officers
- IT management
- DevOps engineers

**External** (with approval):
- Auditors
- Compliance assessors
- Security consultants

---

## Troubleshooting

### Button Says "Generating..." Forever
- **Cause**: Large audit or server overload
- **Solution**: Wait 30 seconds, then refresh page and try again

### Download Doesn't Start
- **Cause**: Browser blocking popup/download
- **Solution**: Check browser permissions, allow downloads from this site

### PDF Won't Open
- **Cause**: Incomplete download or corrupted file
- **Solution**: Download again, ensure stable internet connection

### "Failed to Download Report" Error
- **Cause**: Audit not found or server error
- **Solution**: Refresh page, verify audit exists, check backend logs

---

## Tips for Best Results

### 📋 Before Downloading

1. **Review the findings on screen** - Understand what's in the report
2. **Check human intervention alerts** - Know if manual review is needed
3. **Expand critical findings** - See all details before printing

### 📄 Using the Report

1. **Save with descriptive name** - Include date and system name
2. **Add to audit trail** - Keep with compliance documentation
3. **Track remediation** - Use findings list as a checklist
4. **Compare over time** - Download before and after fixes

### 🔄 Regular Reporting

- Download reports after each audit cycle
- Archive reports for compliance history
- Compare compliance scores month-over-month
- Track risk level trends

---

## Frequently Asked Questions

### Q: How large are the PDF files?
**A**: Typically 5-10 KB. Complex audits may be 15-20 KB.

### Q: Can I customize the report?
**A**: Currently no, but standard format includes all essential information.

### Q: Are reports generated in real-time?
**A**: Yes, generated on-demand when you click the button.

### Q: How long are reports stored?
**A**: Reports aren't stored server-side. Download creates a new PDF each time.

### Q: Can I download reports for old audits?
**A**: Yes, as long as the audit exists in the system.

### Q: Do reports include raw config files?
**A**: No, only findings and evidence snippets (sanitized).

### Q: Can I batch download multiple reports?
**A**: Not yet, but this is a planned feature.

---

## Example Use Cases

### 🎯 Scenario 1: Quarterly Compliance Review
1. Run audits on all network devices
2. Download PDF reports for each
3. Combine into compliance documentation
4. Submit to compliance team

### 🎯 Scenario 2: Security Improvement Sprint
1. Download report with current findings
2. Team works on remediation
3. Re-run audit after fixes
4. Download new report showing improvements
5. Compare before/after compliance scores

### 🎯 Scenario 3: Executive Briefing
1. Download report for critical systems
2. Present executive summary page
3. Highlight risk level and compliance score
4. Show critical/high findings count
5. Present remediation timeline

---

## Support

For issues or questions:
- Check the main README.md
- Review TROUBLESHOOTING.md
- Check backend logs for errors
- Contact your system administrator

---

**Last Updated**: September 9, 2026  
**Feature Version**: 1.0  
**Status**: Production Ready ✅
