# 🔧 FIX: OTP Emails Not Sending to Actual Email Addresses

## Problem Summary
- ✅ OTP codes are generated and stored in database
- ✅ Email drafts are created in backend
- ❌ Emails are NOT being sent to actual email addresses
- ❌ Emails only print to console (CONSOLE MODE enabled)

---

## Root Cause
The SMTP password is set to placeholder `INSERT_YOUR_16_CHAR_GMAIL_APP_PASSWORD_HERE`, which causes the email service to detect that credentials are missing and fall back to **CONSOLE MODE**.

EmailService logic:
```python
self.console_mode = not (self.smtp_user and self.smtp_password)
```

Since password is a placeholder (not valid), `console_mode = True` → emails print to console only.

---

## SOLUTION A: Use Gmail (RECOMMENDED)

### Step 1: Get Gmail App Password
1. Go to: **https://myaccount.google.com/apppasswords**
2. If 2FA is not enabled:
   - Go to https://myaccount.google.com/security
   - Enable 2-Factor Authentication
   - Then go back to apppasswords
3. Select "Mail" → "Windows Computer"
4. Google generates a **16-character password** (with spaces)
5. Copy it (e.g., `xxxx xxxx xxxx xxxx`)

### Step 2: Update .env File
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=mayankparab4811@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
FROM_EMAIL=noreply@vajra-security.com
FROM_NAME=VAJRA Security System
```

### Step 3: Restart Backend

**If backend is running in a terminal:**
- Press `Ctrl+C` to stop
- Run: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`

**If backend is running in Kiro:**
- Reload the terminal or restart

### Step 4: Test OTP Email
```powershell
cd backend
python test_full_flow.py
```

Check the recipient email inbox - you should receive the OTP code!

---

## SOLUTION B: Use SendGrid (Alternative)

### Setup SendGrid
1. Sign up: https://sendgrid.com
2. Get API key from dashboard
3. Create sender identity/domain

### Update .env
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.your-sendgrid-api-key-here
FROM_EMAIL=noreply@your-domain.com
FROM_NAME=VAJRA Security System
```

---

## SOLUTION C: Use Console Mode (Development Only)

If you want to continue in console mode for testing:

```env
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
FROM_EMAIL=noreply@vajra-security.com
FROM_NAME=VAJRA Security System
```

Then emails will print to console. Extract OTP codes from console output and use them for testing.

---

## Verification Checklist

After setting up SMTP, verify:

- [ ] `.env` has real SMTP credentials (not placeholders)
- [ ] Backend has been restarted
- [ ] Run `python test_email_status.py` - should show SMTP configured
- [ ] Run `python test_full_flow.py`
- [ ] Check backend logs for `[SUCCESS] Email sent successfully to`
- [ ] Check email inbox for actual OTP email
- [ ] Email contains correct 6-digit OTP code
- [ ] OTP code can be used to verify the vendor flow

---

## Quick Troubleshooting

### Issue: "Email service in CONSOLE MODE"
**Cause:** SMTP_PASSWORD is missing or invalid
**Fix:** Enter real Gmail App Password or SendGrid API key

### Issue: "SMTP AUTH FAILED"
**Cause:** Wrong password or Gmail 2FA not enabled
**Fix:** Generate new app password, make sure 2FA is ON

### Issue: "Connection refused"
**Cause:** SMTP port blocked by firewall
**Fix:** Try port 465 with SSL (not 587)

### Issue: Email sent but not received
**Cause:** SMTP_USER doesn't match authenticated account
**Fix:** Use same email for SMTP_USER and Gmail account

---

## Current Status

```
SMTP_HOST: smtp.gmail.com
SMTP_PORT: 587
SMTP_USER: mayankparab4811@gmail.com
SMTP_PASSWORD: ❌ NEEDS REAL APP PASSWORD
Console Mode: ✅ ENABLED (emails print to console only)
```

---

## Next Action Required

**Choose one:**

1. **[OPTION A]** Provide Gmail App Password
   - Go to https://myaccount.google.com/apppasswords
   - Send me the 16-character password
   - I'll update .env and restart backend

2. **[OPTION B]** Continue with Console Mode
   - Emails will print to backend console
   - You can manually copy OTP codes
   - OK for development/testing

3. **[OPTION C]** Use SendGrid API Key
   - Sign up at SendGrid
   - Get API key
   - I'll configure it

---

**Please let me know which option you prefer, or provide your Gmail App Password!**
