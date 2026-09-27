"""
Test email sending directly via SMTP
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to path
sys.path.insert(0, os.getcwd())

from app.services.email_service import email_service

print("="*60)
print("TESTING EMAIL SERVICE")
print("="*60)

print("\n1. Email Configuration:")
print(f"   SMTP Host: {email_service.smtp_host}")
print(f"   SMTP Port: {email_service.smtp_port}")
print(f"   From Email: {email_service.from_email}")
print(f"   From Name: {email_service.from_name}")

print("\n2. Sending Test OTP Email to kingpml42@gmail.com...")
result = email_service.send_otp_email(
    to_email="kingpml42@gmail.com",
    otp_code="123456",
    vendor_name="King PML Company"
)

if result:
    print("   ✓ Email sent successfully!")
else:
    print("   ✗ Email failed to send")

print("\n" + "="*60)
