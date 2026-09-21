# Email Service Configuration Guide

## Overview

The Tatva system uses email for:
- **Vendor OTP Codes** - One-time passwords for vendor login
- **Admin Notifications** - New vendor registration alerts
- **Approval Emails** - Vendor approval/rejection notifications

## Email Service Configuration

### Current Configuration

The system is configured to use **Gmail SMTP** for sending emails.

**Key Files:**
- `.env` - Email configuration variables
- `backend/app/services/email_service.py` - Email service implementation

### Configuration Steps

#### Step 1: Generate Gmail App Password

Since Gmail requires authentication, you need an "App Password" (not your regular Gmail password).

1. Go to: https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already enabled)
3. After enabling 2-Step Verification, create an App Password:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Google will generate a 16-character password (e.g., `xxxx xxxx xxxx xxxx`)

#### Step 2: Update .env Configuration

Edit `.env` file in the backend directory:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
FROM_EMAIL=tatva-noreply@vajra-security.com
FROM_NAME=VAJRA Tatva System
ADMIN_EMAIL=admin@yourcompany.com
```

**Important:**
- `SMTP_USER` - Your Gmail address
- `SMTP_PASSWORD` - The 16-character App Password (NOT your Gmail password)
- `ADMIN_EMAIL` - Where admin notifications will be sent
- `FROM_EMAIL` - Display name in emails

#### Step 3: Verify Configuration

The system logs email operations. You can verify email configuration by:

1. **Console Mode Detection** - When the server starts:
   ```
   [WARNING] Email service in CONSOLE MODE (SMTP not configured)
   ```
   This means SMTP credentials are missing or invalid.

2. **Console Logging** - If SMTP is not working, emails are logged to console:
   ```
   [CONSOLE] OTP Email
   To: vendor@example.com
   Code: 123456
   ```

### Email Templates

#### 1. Vendor OTP Email

**When:** Vendor requests OTP code for login

**Subject:** `Your Tatva Login OTP`

**Content:**
- 6-digit OTP code
- Expiration time (10 minutes)
- Security information
- Brand footer

#### 2. Vendor Approval Email

**When:** Admin approves vendor registration

**Subject:** `Your Tatva Registration - Approved`

**Content:**
- Approval notification
- Organization name
- Next steps for login
- Contact information for support

#### 3. Vendor Rejection Email

**When:** Admin rejects vendor registration

**Subject:** `Your Tatva Registration - Not Approved`

**Content:**
- Rejection notification
- Optional rejection reason
- Instructions to contact admin
- Support information

#### 4. Admin Notification Email

**When:** New vendor registers

**Subject:** `New Vendor Access Request — Tatva`

**Content:**
- Vendor company name
- Vendor contact information
- Request ID for tracking
- Link to admin dashboard
- Admin action required message

---

## Email Service Implementation

### Key Functions

**`send_vendor_otp(to_email, otp_code, expires_at)`**
- Sends OTP code to vendor
- Used during vendor login flow
- Includes security messaging

**`send_vendor_approval_notification(to_email, vendor_name, ...)`**
- Sends approval/rejection notification
- Includes next steps or rejection reason

**`send_admin_approval_request(admin_email, vendor_name, ...)`**
- Notifies admin of new registration
- Includes vendor details for review

### Console Mode vs. SMTP Mode

#### Console Mode (SMTP Not Configured)
- Emails are NOT sent
- Emails are logged to console with `[CONSOLE]` prefix
- Useful for development/testing without real email

**Indicates:**
```
[WARNING] Email service in CONSOLE MODE (SMTP not configured)
```

#### SMTP Mode (SMTP Configured)
- Emails are sent via Gmail SMTP
- Console shows status: `[SUCCESS] Email sent successfully`
- On error: `[ERROR] Failed to send email...`

---

## Testing Email Configuration

### Test 1: System Startup Check

```bash
# Start the backend server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Expected Output (if SMTP configured):**
```
[STARTUP] Starting SIH26155 Network Security Auditor...
[SUCCESS] Database initialized successfully
[STARTUP] Application ready!
```

**If SMTP NOT configured:**
```
[WARNING] Email service in CONSOLE MODE (SMTP not configured)
```

### Test 2: Vendor Registration Email

1. Go to http://localhost:5173/vendor/register
2. Submit vendor registration form
3. Check console for admin notification email logging

**Expected Console Output:**
```
[CONSOLE] Admin Notification Email
To: mayankparab4811@gmail.com
Subject: New Vendor Access Request — Tatva
```

### Test 3: OTP Request Email

1. Go to http://localhost:5173/vendor/login
2. Enter vendor email
3. Click "Send OTP Code"
4. Check console for OTP email

**Expected Console Output:**
```
[CONSOLE] OTP Email
To: vendor@example.com
Code: 123456
Expires: 10 minutes
```

### Test 4: Approval Email

1. Login as admin
2. Go to "Vendor Management"
3. Approve a pending vendor
4. Check console for approval notification

**Expected Console Output:**
```
[CONSOLE] Vendor Approval Email
To: vendor@example.com
Subject: Your Tatva Registration - Approved
```

---

## Common Issues & Solutions

### Issue 1: "Email service in CONSOLE MODE"

**Problem:** SMTP credentials are not configured

**Solution:**
1. Check `.env` file has SMTP settings
2. Verify `SMTP_USER` and `SMTP_PASSWORD` are set
3. Restart the backend server

### Issue 2: "Connection refused" on port 587

**Problem:** Gmail SMTP server not reachable

**Solution:**
1. Check internet connection
2. Verify `SMTP_HOST=smtp.gmail.com`
3. Try using port 465 instead (requires SSL)
4. Check if firewall is blocking SMTP port

### Issue 3: "Authentication failed"

**Problem:** Invalid Gmail credentials

**Solution:**
1. Verify `SMTP_USER` is correct Gmail address
2. Check `SMTP_PASSWORD` is the 16-character App Password (not Gmail password)
3. Ensure 2-Step Verification is enabled on Gmail account
4. Regenerate App Password from https://myaccount.google.com/apppasswords

### Issue 4: "Email not received"

**Problem:** Email sent but not in inbox

**Solution:**
1. Check spam/junk folder
2. Verify recipient email address is correct
3. Check `.env` has correct `ADMIN_EMAIL`
4. Verify email was sent (check console logs)

---

## Production Deployment

### For Production Use

1. **Use Environment Variables** - Never commit credentials to Git
   ```bash
   export SMTP_USER="your-email@gmail.com"
   export SMTP_PASSWORD="app-password"
   ```

2. **Secure Credentials** - Use secrets management:
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault
   - Docker Secrets

3. **Alternative Email Services**
   - SendGrid - `SMTP_HOST=smtp.sendgrid.net`
   - Mailgun - `SMTP_HOST=smtp.mailgun.org`
   - AWS SES - Use boto3 instead of SMTP

4. **Email Limits**
   - Gmail Free: 500 emails/day
   - Gmail Workspace: Higher limits
   - Consider dedicated email service for production

---

## Email Security Best Practices

✅ **DO:**
- Use App Passwords, not Gmail passwords
- Enable 2-Step Verification on Gmail account
- Store credentials in environment variables
- Use SMTP with TLS (port 587)
- Log email activities for audit trail
- Rate-limit OTP requests (1 per 60 seconds)
- Expire OTPs quickly (10 minutes)

❌ **DON'T:**
- Commit credentials to Git
- Use plain Gmail password for SMTP
- Send passwords in OTP emails
- Store credentials in code
- Use unencrypted email transmission
- Allow unlimited OTP requests

---

## Support & Documentation

**Email Service Code:** `backend/app/services/email_service.py`

**Configuration File:** `backend/.env`

**Backend Vendor API:** `backend/app/api/vendor.py`

**Admin API:** `backend/app/api/admin.py`

For more information, refer to:
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [Python smtplib Documentation](https://docs.python.org/3/library/smtplib.html)

---

**Status:** ✅ Email service fully implemented and configured

**Test Coverage:**
- Vendor OTP emails
- Admin approval notifications
- Vendor registration alerts
- Error handling and retry logic

**Next Steps:**
1. Configure `.env` with your Gmail credentials
2. Test email delivery
3. Deploy to production with secure credential management
