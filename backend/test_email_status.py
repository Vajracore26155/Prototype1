#!/usr/bin/env python3
"""
Check current email configuration status
"""
import os
from app.services.email_service import get_email_service

print("=" * 80)
print("EMAIL SERVICE CONFIGURATION STATUS")
print("=" * 80)
print()

email_service = get_email_service()

print("Current Configuration:")
print(f"  SMTP Host: {email_service.smtp_host}")
print(f"  SMTP Port: {email_service.smtp_port}")
print(f"  SMTP User: {email_service.smtp_user if email_service.smtp_user else '(not set)'}")
print(f"  SMTP Password: {'*' * 10 if email_service.smtp_password and email_service.smtp_password != 'your-app-password-here' else '(not set or placeholder)'}")
print(f"  From Email: {email_service.from_email}")
print(f"  From Name: {email_service.from_name}")
print()

print("Console Mode Status:")
print(f"  Enabled: {email_service.console_mode}")
print()

if email_service.console_mode:
    print("⚠️  EMAILS ARE PRINTING TO CONSOLE ONLY")
    print()
    print("To send real emails, you need to:")
    print("  1. Update .env file with real SMTP credentials")
    print("  2. Set SMTP_USER to a valid email address")
    print("  3. Set SMTP_PASSWORD to a valid app password (not placeholder)")
    print("  4. Restart the backend")
    print()
    print("See SETUP_EMAIL.md for detailed instructions")
else:
    print("✅ EMAIL SERVICE CONFIGURED FOR REAL SMTP SENDING")
    print()
    print("Testing email configuration...")
    
    # Test SMTP connection
    try:
        import smtplib
        server = smtplib.SMTP(email_service.smtp_host, email_service.smtp_port)
        server.starttls()
        server.login(email_service.smtp_user, email_service.smtp_password)
        server.quit()
        print("✅ SMTP connection test: PASSED")
    except Exception as e:
        print(f"❌ SMTP connection test: FAILED")
        print(f"   Error: {str(e)}")
