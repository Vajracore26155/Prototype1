"""
Email Service for sending OTPs and notifications
Uses SMTP for production, console logging for development
"""
import smtplib
import os
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

# Ensure .env is loaded with correct path
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class EmailService:
    """
    Email service for sending OTPs and notifications
    """
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@vajra-security.com")
        self.from_name = os.getenv("FROM_NAME", "VAJRA Security System")
        
        # Use console mode if SMTP not configured
        self.console_mode = not (self.smtp_user and self.smtp_password)
        
        if self.console_mode:
            print("\n" + "="*70)
            print("[⚠️  WARNING] Email service in CONSOLE MODE (SMTP not configured)")
            print("="*70)
            print("Emails will print to console instead of being sent to recipients.")
            print("To enable real email sending:")
            print("  1. Go to https://myaccount.google.com/apppasswords")
            print("  2. Enable 2FA and generate an app password")
            print("  3. Update SMTP_PASSWORD in .env with the 16-character password")
            print("  4. Restart the backend")
            print("See FIX_OTP_EMAIL.md for detailed instructions")
            print("="*70 + "\n")
    
    def send_vendor_otp(
        self,
        to_email: str,
        vendor_name: str,
        otp_code: str,
        organization_name: str,
        expires_minutes: int = 10
    ) -> bool:
        """
        Send OTP email to vendor
        
        Args:
            to_email: Vendor email address
            vendor_name: Vendor contact name
            otp_code: 6-digit OTP code
            organization_name: Organization name
            expires_minutes: OTP expiration time
            
        Returns:
            True if sent successfully
        """
        subject = f"Your VAJRA Upload Verification Code: {otp_code}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 5px; margin: 20px 0; }}
                .otp-code {{ 
                    font-size: 32px; 
                    font-weight: bold; 
                    color: #2c3e50; 
                    text-align: center; 
                    padding: 20px; 
                    background-color: #ecf0f1; 
                    border-radius: 5px; 
                    letter-spacing: 5px;
                    margin: 20px 0;
                }}
                .warning {{ color: #e74c3c; font-weight: bold; }}
                .footer {{ text-align: center; color: #7f8c8d; font-size: 12px; margin-top: 30px; }}
                .info-box {{ background-color: #e8f4f8; padding: 15px; border-left: 4px solid #3498db; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ VAJRA Security System</h1>
                    <p>Configuration Upload Verification</p>
                </div>
                
                <div class="content">
                    <h2>Hello {vendor_name},</h2>
                    
                    <p>You have requested to upload network device configurations to the VAJRA Security System for:</p>
                    
                    <div class="info-box">
                        <strong>Organization:</strong> {organization_name}
                    </div>
                    
                    <p>Your verification code is:</p>
                    
                    <div class="otp-code">
                        {otp_code}
                    </div>
                    
                    <p><strong>Important:</strong></p>
                    <ul>
                        <li>This code expires in <strong>{expires_minutes} minutes</strong></li>
                        <li>Do not share this code with anyone</li>
                        <li>Only use this code if you initiated this request</li>
                        <li>This code can only be used once</li>
                    </ul>
                    
                    <div class="info-box">
                        <p class="warning">⚠️ Security Notice</p>
                        <p>If you did not request this code, please ignore this email and contact your system administrator immediately.</p>
                    </div>
                    
                    <p>After verification, you will have 24 hours to upload your configuration files.</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from VAJRA Security System</p>
                    <p>Time: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC</p>
                    <p>© 2024 VAJRA - Network Security Compliance Platform</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        VAJRA Security System - Configuration Upload Verification
        
        Hello {vendor_name},
        
        You have requested to upload network device configurations for:
        Organization: {organization_name}
        
        Your verification code is: {otp_code}
        
        IMPORTANT:
        - This code expires in {expires_minutes} minutes
        - Do not share this code with anyone
        - Only use this code if you initiated this request
        - This code can only be used once
        
        SECURITY NOTICE:
        If you did not request this code, please ignore this email and contact 
        your system administrator immediately.
        
        After verification, you will have 24 hours to upload your configuration files.
        
        ---
        This is an automated message from VAJRA Security System
        Time: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC
        © 2024 VAJRA - Network Security Compliance Platform
        """
        
        return self._send_email(to_email, subject, html_body, text_body)
    
    def send_vendor_approval_notification(
        self,
        to_email: str,
        vendor_name: str,
        organization_name: str,
        approved: bool,
        admin_name: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Notify vendor of approval/rejection
        
        Args:
            to_email: Vendor email
            vendor_name: Vendor contact name
            organization_name: Organization name
            approved: True if approved, False if rejected
            admin_name: Admin who made decision
            notes: Optional notes from admin
            
        Returns:
            True if sent successfully
        """
        status = "APPROVED" if approved else "REJECTED"
        status_color = "#27ae60" if approved else "#e74c3c"
        status_icon = "✅" if approved else "❌"
        
        subject = f"Vendor Access {status} - VAJRA Security System"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 5px; margin: 20px 0; }}
                .status {{ 
                    font-size: 24px; 
                    font-weight: bold; 
                    color: {status_color}; 
                    text-align: center; 
                    padding: 20px; 
                    background-color: #ecf0f1; 
                    border-radius: 5px; 
                    margin: 20px 0;
                }}
                .info-box {{ background-color: #e8f4f8; padding: 15px; border-left: 4px solid #3498db; margin: 15px 0; }}
                .notes-box {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0; }}
                .footer {{ text-align: center; color: #7f8c8d; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ VAJRA Security System</h1>
                    <p>Vendor Access Decision</p>
                </div>
                
                <div class="content">
                    <h2>Hello {vendor_name},</h2>
                    
                    <p>Your vendor access request has been reviewed:</p>
                    
                    <div class="status">
                        {status_icon} ACCESS {status}
                    </div>
                    
                    <div class="info-box">
                        <strong>Organization:</strong> {organization_name}<br>
                        <strong>Reviewed by:</strong> {admin_name}<br>
                        <strong>Date:</strong> {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC
                    </div>
                    """
        
        if notes:
            html_body += f"""<div class='notes-box'><strong>Administrator Notes:</strong><p>{notes}</p></div>"""
        
        if approved:
            html_body += """<p><strong>Next Steps:</strong></p><ul><li>You can now request OTP codes to upload configurations</li><li>Each upload session requires OTP verification</li><li>Upload sessions are valid for 24 hours</li><li>Contact your administrator if you have questions</li></ul>"""
        else:
            html_body += """<p>If you believe this decision was made in error, please contact your system administrator.</p>"""
        
        html_body += """
                </div>
                
                <div class="footer">
                    <p>This is an automated message from VAJRA Security System</p>
                    <p>© 2024 VAJRA - Network Security Compliance Platform</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""VAJRA Security System - Vendor Access Decision

Hello {vendor_name},

Your vendor access request has been reviewed:

STATUS: {status}

Organization: {organization_name}
Reviewed by: {admin_name}
Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

"""
        
        if notes:
            text_body += f"Administrator Notes:\n{notes}\n\n"
        
        if approved:
            text_body += """Next Steps:
- You can now request OTP codes to upload configurations
- Each upload session requires OTP verification
- Upload sessions are valid for 24 hours
- Contact your administrator if you have questions
"""
        else:
            text_body += "If you believe this decision was made in error, please contact your system administrator.\n"
        
        text_body += """
---
This is an automated message from VAJRA Security System
© 2024 VAJRA - Network Security Compliance Platform
"""
        
        return self._send_email(to_email, subject, html_body, text_body)
    
    def send_admin_approval_request(
        self,
        admin_email: str,
        admin_name: str,
        vendor_name: str,
        vendor_email: str,
        company_name: str,
        organization_name: str,
        request_id: str
    ) -> bool:
        """
        Notify admin of new vendor approval request
        
        Args:
            admin_email: Admin email address
            admin_name: Admin name
            vendor_name: Vendor contact name
            vendor_email: Vendor email
            company_name: Vendor company
            organization_name: Organization name
            request_id: Request ID for tracking
            
        Returns:
            True if sent successfully
        """
        subject = f"New Vendor Access Request - {company_name}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #e67e22; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 5px; margin: 20px 0; }}
                .alert-box {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0; }}
                .vendor-details {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .action-button {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    margin: 10px 5px; 
                    background-color: #3498db; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    font-weight: bold;
                }}
                .footer {{ text-align: center; color: #7f8c8d; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 VAJRA Security System</h1>
                    <p>Vendor Approval Request</p>
                </div>
                
                <div class="content">
                    <h2>Hello {admin_name},</h2>
                    
                    <div class="alert-box">
                        <strong>⚠️ Action Required:</strong> A new vendor has requested access to upload device configurations.
                    </div>
                    
                    <h3>Vendor Details:</h3>
                    <div class="vendor-details">
                        <strong>Company:</strong> {company_name}<br>
                        <strong>Contact Name:</strong> {vendor_name}<br>
                        <strong>Email:</strong> {vendor_email}<br>
                        <strong>Organization:</strong> {organization_name}<br>
                        <strong>Request ID:</strong> {request_id}<br>
                        <strong>Request Date:</strong> {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC
                    </div>
                    
                    <p><strong>Required Actions:</strong></p>
                    <ol>
                        <li>Verify the vendor's identity and legitimacy</li>
                        <li>Confirm they should have access to upload configurations</li>
                        <li>Review their company information</li>
                        <li>Approve or reject the request through the admin portal</li>
                    </ol>
                    
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="#" class="action-button">Review Request in Admin Portal</a>
                    </p>
                    
                    <p><small>Note: Approved vendors will be able to request OTP codes to upload device configurations. Each upload session requires verification.</small></p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from VAJRA Security System</p>
                    <p>© 2024 VAJRA - Network Security Compliance Platform</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        VAJRA Security System - Vendor Approval Request
        
        Hello {admin_name},
        
        ACTION REQUIRED: A new vendor has requested access to upload device configurations.
        
        Vendor Details:
        - Company: {company_name}
        - Contact Name: {vendor_name}
        - Email: {vendor_email}
        - Organization: {organization_name}
        - Request ID: {request_id}
        - Request Date: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC
        
        Required Actions:
        1. Verify the vendor's identity and legitimacy
        2. Confirm they should have access to upload configurations
        3. Review their company information
        4. Approve or reject the request through the admin portal
        
        Note: Approved vendors will be able to request OTP codes to upload device 
        configurations. Each upload session requires verification.
        
        ---
        This is an automated message from VAJRA Security System
        © 2024 VAJRA - Network Security Compliance Platform
        """
        
        return self._send_email(admin_email, subject, html_body, text_body)
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str
    ) -> bool:
        """
        Internal method to send email via SMTP or console
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: HTML body
            text_body: Plain text body
            
        Returns:
            True if sent successfully
        """
        if self.console_mode:
            # Console mode for development
            print("\n" + "="*70)
            print("📧 EMAIL (CONSOLE MODE)")
            print("="*70)
            print(f"To: {to_email}")
            print(f"From: {self.from_name} <{self.from_email}>")
            print(f"Subject: {subject}")
            print("-"*70)
            print(text_body)
            print("="*70 + "\n")
            return True
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            message["Subject"] = subject
            
            # Attach parts
            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            print(f"[SUCCESS] Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to send email to {to_email}: {str(e)}")
            return False


# Singleton instance
_email_service = None

def get_email_service() -> EmailService:
    """Get email service singleton"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
