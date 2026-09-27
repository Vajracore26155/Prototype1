"""
Email Service Module
Handles sending emails via SMTP for OTP and notifications
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP"""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@vajra-security.com')
        self.from_name = os.getenv('FROM_NAME', 'VAJRA Security System')
        
    def send_otp_email(self, to_email: str, otp_code: str, vendor_name: str) -> bool:
        """
        Send OTP via email
        
        Args:
            to_email: Recipient email address
            otp_code: 6-digit OTP code
            vendor_name: Vendor company name for personalization
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            subject = "Your VAJRA Security OTP Code"
            
            # HTML email template
            html_body = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #4F46E5; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                        .content {{ background-color: #F9FAFB; padding: 30px; border-radius: 0 0 8px 8px; }}
                        .otp-box {{ background-color: white; border: 2px solid #4F46E5; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0; }}
                        .otp-code {{ font-size: 32px; font-weight: bold; color: #4F46E5; letter-spacing: 5px; font-family: monospace; }}
                        .footer {{ color: #6B7280; font-size: 12px; text-align: center; margin-top: 20px; }}
                        .warning {{ color: #DC2626; font-size: 14px; margin-top: 15px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>VAJRA Security System</h1>
                            <p>One-Time Password (OTP) Verification</p>
                        </div>
                        <div class="content">
                            <p>Hello <strong>{vendor_name}</strong>,</p>
                            <p>You have requested to log in to your VAJRA vendor account. Please use the following OTP code to complete your authentication:</p>
                            
                            <div class="otp-box">
                                <p style="margin: 0; color: #6B7280; font-size: 12px;">Your OTP Code</p>
                                <p class="otp-code">{otp_code}</p>
                            </div>
                            
                            <p><strong>Important:</strong></p>
                            <ul>
                                <li>This OTP code will expire in <strong>10 minutes</strong></li>
                                <li>Do not share this code with anyone</li>
                                <li>VAJRA will never ask you for this code via email or phone</li>
                                <li>You have 5 attempts to enter the correct code</li>
                            </ul>
                            
                            <div class="warning">
                                ⚠️ If you did not request this OTP, please ignore this email and your account will remain secure.
                            </div>
                            
                            <p style="margin-top: 30px; font-size: 14px;">
                                Best regards,<br>
                                <strong>VAJRA Security Team</strong>
                            </p>
                        </div>
                        <div class="footer">
                            <p>This is an automated message. Please do not reply to this email.</p>
                            <p>&copy; 2026 VAJRA Network Security Auditor. All rights reserved.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            # Plain text fallback
            text_body = f"""
VAJRA Security System
One-Time Password (OTP) Verification

Hello {vendor_name},

You have requested to log in to your VAJRA vendor account. Please use the following OTP code to complete your authentication:

OTP Code: {otp_code}

Important:
- This OTP code will expire in 10 minutes
- Do not share this code with anyone
- VAJRA will never ask you for this code via email or phone
- You have 5 attempts to enter the correct code

If you did not request this OTP, please ignore this email and your account will remain secure.

Best regards,
VAJRA Security Team

---
This is an automated message. Please do not reply to this email.
© 2026 VAJRA Network Security Auditor. All rights reserved.
            """
            
            return self._send_email(to_email, subject, html_body, text_body)
            
        except Exception as e:
            logger.error(f"[EMAIL ERROR] Failed to prepare OTP email: {str(e)}")
            return False
    
    def send_vendor_approval_notification(self, to_email: str, vendor_name: str, organization_name: str = None, admin_name: str = None, approved: bool = True, notes: str = None) -> bool:
        """Send vendor approval/rejection notification"""
        try:
            if approved:
                subject = "Your VAJRA Vendor Account Has Been Approved"
                status_text = "approved"
                color = "#10B981"
            else:
                subject = "Your VAJRA Vendor Account Request Update"
                status_text = "requires attention"
                color = "#DC2626"
            
            html_body = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: {color}; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                        .content {{ background-color: #F9FAFB; padding: 30px; border-radius: 0 0 8px 8px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Account {status_text.title()}</h1>
                        </div>
                        <div class="content">
                            <p>Hello <strong>{vendor_name}</strong>,</p>
                            <p>Your VAJRA vendor account has been {status_text}.</p>
                            {f'<p><strong>Organization:</strong> {organization_name}</p>' if organization_name else ''}
                            {f'<p><strong>Reviewed by:</strong> {admin_name}</p>' if admin_name else ''}
                            {f'<p><strong>Notes:</strong> {notes}</p>' if notes else ''}
                            {'<p>You can now log in using OTP authentication.</p>' if approved else ''}
                            <p>Best regards,<br>VAJRA Security Team</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            text_body = f"""
Account {status_text.title()}

Hello {vendor_name},

Your VAJRA vendor account has been {status_text}.
{'Organization: ' + organization_name if organization_name else ''}
{'Reviewed by: ' + admin_name if admin_name else ''}
{'Notes: ' + notes if notes else ''}

{'You can now log in using OTP authentication.' if approved else ''}

Best regards,
VAJRA Security Team
            """
            
            return self._send_email(to_email, subject, html_body, text_body)
            
        except Exception as e:
            logger.error(f"[EMAIL ERROR] Failed to prepare approval notification: {str(e)}")
            return False

    def send_approval_notification(self, to_email: str, vendor_name: str, vendor_id: str) -> bool:
        """Send vendor approval notification"""
        try:
            subject = "Your VAJRA Vendor Account Has Been Approved"
            
            html_body = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #10B981; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                        .content {{ background-color: #F9FAFB; padding: 30px; border-radius: 0 0 8px 8px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Account Approved</h1>
                        </div>
                        <div class="content">
                            <p>Hello <strong>{vendor_name}</strong>,</p>
                            <p>Great news! Your VAJRA vendor account (ID: {vendor_id}) has been approved.</p>
                            <p>You can now log in using OTP authentication at any time.</p>
                            <p><a href="http://localhost:5173/vendor/login" style="display: inline-block; background-color: #10B981; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Login Now</a></p>
                            <p>Best regards,<br>VAJRA Security Team</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            text_body = f"""
Account Approved

Hello {vendor_name},

Great news! Your VAJRA vendor account (ID: {vendor_id}) has been approved.

You can now log in using OTP authentication at any time.

Best regards,
VAJRA Security Team
            """
            
            return self._send_email(to_email, subject, html_body, text_body)
            
        except Exception as e:
            logger.error(f"[EMAIL ERROR] Failed to prepare approval email: {str(e)}")
            return False
    
    def _send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        """
        Internal method to send email via SMTP
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: HTML email content
            text_body: Plain text email content
            
        Returns:
            bool: True if successful
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()  # Enable TLS encryption
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            logger.info(f"[EMAIL SUCCESS] OTP sent to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("[EMAIL ERROR] SMTP authentication failed. Check credentials.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"[EMAIL ERROR] SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"[EMAIL ERROR] Failed to send email: {str(e)}")
            return False


# Singleton instance
email_service = EmailService()


def get_email_service() -> EmailService:
    """Get the email service instance"""
    return email_service
