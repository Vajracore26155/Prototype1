# OTP Email Configuration Guide

## Issue
OTP codes are being generated and stored in the database, but emails are only printing to the console (not being sent to actual email addresses).

## Root Cause
The SMTP credentials are set to the placeholder `your-app-password-here`, which causes the email service to fall back to console mode.

## Solution

### Option 1: Use Gmail with App Password (RECOMMENDED)

#### Step 1: Set up Gmail 2FA and App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer" (or your device)
3. Google will generate a 16-character app password
4. Copy this password

#### Step 2: Update .env file
Replace `your-app-password-here` with the actual app password:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=mayankparab4811@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  (paste your 16-char app password here)
FROM_EMAIL=noreply@vajra-security.com
FROM_NAME=VAJRA Security System
```

#### Step 3: Restart Backend
```powershell
# Stop current backend process
# Then restart:
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

#### Step 4: Test OTP
```powershell
cd backend
python test_full_flow.py
```

You should now see OTP emails arriving in the actual email inbox instead of just console output.

---

### Option 2: Use Alternative Email Provider

You can use any SMTP provider that supports SMTP relay:
- SendGrid
- AWS SES
- Mailgun
- Azure SendGrid
- etc.

Update the SMTP credentials accordingly in `.env`

---

### Option 3: Temporary Console Mode (Development Only)

If you want to keep using console mode for testing, just comment out the SMTP settings again:

```env
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=
# SMTP_PASSWORD=
```

Then emails will print to console.

---

## Verification

After updating SMTP credentials:

1. Check backend logs for: `[SUCCESS] Email sent successfully to`
2. Check recipient email inbox for OTP code
3. Use the OTP code to verify the flow works end-to-end

---

## Troubleshooting

### Error: "SMTP AUTH FAILED"
- App password is incorrect or expired
- Gmail 2FA is not enabled
- Solution: Generate a new app password

### Error: "Port 587 refused"
- Gmail SMTP port blocked by firewall
- Solution: Try port 465 with SSL instead

### Error: "Invalid email from address"
- FROM_EMAIL doesn't match SMTP_USER
- Solution: Use same email address or configure SMTP relay correctly

---

## Quick Test Without Real Email

If you don't have Gmail or prefer not to use real credentials right now, you can:

1. Leave SMTP settings commented out
2. Run tests and check console output for OTP codes
3. Use those codes to test the verification flow
4. Frontend would need to handle "check console" for OTP in development mode

---

## Next Steps

1. [ ] Get Gmail App Password
2. [ ] Update SMTP_PASSWORD in .env
3. [ ] Restart backend
4. [ ] Test OTP email sending
5. [ ] Verify emails arrive in inbox
6. [ ] Complete vendor flow end-to-end
