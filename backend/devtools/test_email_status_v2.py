#!/usr/bin/env python3
"""
Check current email configuration status
"""
import os
from app.services.email_service import get_email_service

print("=" * 80)
print("EMAIL SERVICE CONFIGURATION STATUS (AFTER RESTART)")
print("=" * 80)
print()

email_service = get_email_service()

print("Current Configuration:")
print(f"  SMTP Host: {email_service.smtp_host}")
print(f"  SMTP Port: {email_service.smtp_port}")
print(f"  SMTP User: {email_service.smtp_user if email_service.smtp_user else '(not set)'}")
print(f"  SMTP Password: {'***' + email_service.smtp_password[-5:] if email_service.smtp_password and len(email_service.smtp_password) > 5 else '(not set)'}")
print(f"  From Email: {email_service.from_email}")
print(f"  From Name: {email_service.from_name}")
print()

print("Console Mode Status:")
print(f"  Enabled: {email_service.console_mode}")
print()

if email_service.console_mode:
    print("⚠️  EMAILS ARE PRINTING TO CONSOLE ONLY")
    print()
    print("SMTP credentials missing or invalid:")
    print(f"  SMTP_USER: {'✓' if email_service.smtp_user else '✗ EMPTY'}")
    print(f"  SMTP_PASSWORD: {'✓' if email_service.smtp_password else '✗ EMPTY'}")
else:
    print("✅ EMAIL SERVICE CONFIGURED FOR REAL SMTP SENDING")
    print()
    print("Testing SMTP connection...")
    
    # Test SMTP connection
    try:
        import smtplib
        server = smtplib.SMTP(email_service.smtp_host, email_service.smtp_port, timeout=10)
        server.starttls()
        server.login(email_service.smtp_user, email_service.smtp_password)
        server.quit()
        print("✅ SMTP connection test: PASSED")
        print()
        print("READY TO SEND EMAILS!")
    except Exception as e:
        print(f"❌ SMTP connection test: FAILED")
        print(f"   Error: {str(e)}")
