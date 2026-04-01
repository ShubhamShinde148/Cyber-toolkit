"""
Feedback Email Notification System
Dark Web Leak Monitor

Sends email notifications when users submit feedback.
Uses Gmail SMTP with TLS encryption.
"""

import os
import smtplib
from email.message import EmailMessage
from email.utils import formatdate
from datetime import datetime
from typing import Optional, Dict, Any
import html


class FeedbackMailer:
    """
    Handles sending feedback notification emails via Gmail SMTP.
    
    Environment Variables Required:
        FEEDBACK_EMAIL_ADDRESS: Gmail address for sending/receiving feedback
        FEEDBACK_EMAIL_PASSWORD: Gmail App Password (not regular password)
    
    Setup Instructions:
        1. Enable 2-Factor Authentication on your Google Account
        2. Generate an App Password at: https://myaccount.google.com/apppasswords
        3. Set environment variables in .env file
    """
    
    # Gmail SMTP Configuration
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    
    def __init__(self):
        """Initialize the mailer with environment variables."""
        self.email_address = os.getenv('FEEDBACK_EMAIL_ADDRESS')
        self.email_password = os.getenv('FEEDBACK_EMAIL_PASSWORD')
        self.recipient_email = os.getenv('FEEDBACK_RECIPIENT_EMAIL', self.email_address)
        self._is_configured = bool(self.email_address and self.email_password)
    
    def is_configured(self) -> bool:
        """Check if email credentials are properly configured."""
        return self._is_configured
    
    def _get_star_rating_html(self, rating: int) -> str:
        """Generate HTML star rating display."""
        filled_star = '★'
        empty_star = '☆'
        stars = filled_star * rating + empty_star * (5 - rating)
        return f'<span style="color: #FFD700; font-size: 24px;">{stars}</span>'
    
    def _get_star_rating_text(self, rating: int) -> str:
        """Generate text star rating display."""
        return '★' * rating + '☆' * (5 - rating)
    
    def _create_email_content(self, feedback_data: Dict[str, Any]) -> tuple[str, str]:
        """
        Create both HTML and plain text email content.
        
        Returns:
            Tuple of (html_content, text_content)
        """
        rating = feedback_data.get('rating', 0)
        message = html.escape(feedback_data.get('feedback', 'No message provided'))
        page = html.escape(feedback_data.get('page', 'Unknown'))
        ip_address = feedback_data.get('ip', 'Unknown')
        timestamp = feedback_data.get('timestamp', datetime.now().isoformat())
        user_agent = html.escape(feedback_data.get('user_agent', 'Unknown'))
        
        # Parse timestamp for display
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%B %d, %Y at %I:%M %p')
            else:
                formatted_time = str(timestamp)
        except:
            formatted_time = str(timestamp)
        
        # Rating color based on value
        rating_colors = {
            1: '#FF4444',  # Red
            2: '#FF8844',  # Orange
            3: '#FFCC00',  # Yellow
            4: '#88CC00',  # Light Green
            5: '#00CC44'   # Green
        }
        rating_color = rating_colors.get(rating, '#888888')
        
        # Rating descriptions
        rating_texts = {
            1: 'Poor - Needs improvement',
            2: 'Fair - Could be better',
            3: 'Good - Met expectations',
            4: 'Great - Above average',
            5: 'Excellent - Outstanding!'
        }
        rating_text = rating_texts.get(rating, 'Unknown')
        
        # HTML Email Template
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0a0e17;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0a0e17;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background: linear-gradient(145deg, #1a1f2e, #0d1117); border: 1px solid #00ff88; border-radius: 16px; overflow: hidden;">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #00ff88, #00cc6a); padding: 30px; text-align: center;">
                            <h1 style="margin: 0; color: #0a0e17; font-size: 24px; font-weight: 700;">
                                🔒 New Feedback Received
                            </h1>
                            <p style="margin: 10px 0 0; color: #0a0e17; opacity: 0.8;">
                                Dark Web Leak Monitor
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Rating Section -->
                    <tr>
                        <td style="padding: 30px; text-align: center; border-bottom: 1px solid #2d3548;">
                            <div style="font-size: 48px; letter-spacing: 8px; color: #FFD700;">
                                {self._get_star_rating_text(rating)}
                            </div>
                            <p style="margin: 15px 0 0; color: {rating_color}; font-size: 18px; font-weight: 600;">
                                {rating}/5 - {rating_text}
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Feedback Message -->
                    <tr>
                        <td style="padding: 30px;">
                            <h3 style="margin: 0 0 15px; color: #00ff88; font-size: 16px; text-transform: uppercase; letter-spacing: 1px;">
                                📝 Feedback Message
                            </h3>
                            <div style="background: #0d1117; border-left: 4px solid #00ff88; padding: 20px; border-radius: 8px;">
                                <p style="margin: 0; color: #e6edf3; font-size: 16px; line-height: 1.6;">
                                    {message if message else '<em style="color: #888;">No message provided</em>'}
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Details Section -->
                    <tr>
                        <td style="padding: 0 30px 30px;">
                            <h3 style="margin: 0 0 15px; color: #00ff88; font-size: 16px; text-transform: uppercase; letter-spacing: 1px;">
                                📊 Details
                            </h3>
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background: #0d1117; border-radius: 8px; overflow: hidden;">
                                <tr>
                                    <td style="padding: 15px 20px; border-bottom: 1px solid #2d3548;">
                                        <span style="color: #888; font-size: 14px;">Page</span><br>
                                        <span style="color: #e6edf3; font-size: 16px;">{page}</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 15px 20px; border-bottom: 1px solid #2d3548;">
                                        <span style="color: #888; font-size: 14px;">IP Address</span><br>
                                        <span style="color: #e6edf3; font-size: 16px;">{ip_address}</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 15px 20px; border-bottom: 1px solid #2d3548;">
                                        <span style="color: #888; font-size: 14px;">Timestamp</span><br>
                                        <span style="color: #e6edf3; font-size: 16px;">{formatted_time}</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 15px 20px;">
                                        <span style="color: #888; font-size: 14px;">User Agent</span><br>
                                        <span style="color: #e6edf3; font-size: 12px; word-break: break-all;">{user_agent}</span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background: #0d1117; padding: 20px; text-align: center; border-top: 1px solid #2d3548;">
                            <p style="margin: 0; color: #666; font-size: 12px;">
                                This is an automated notification from Dark Web Leak Monitor.<br>
                                &copy; 2026 Dark Web Leak Monitor. All rights reserved.
                                shubhuu❤️‍🩹
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
'''
        
        # Plain Text Email Template
        text_content = f'''
═══════════════════════════════════════════════════════════
          🔒 NEW FEEDBACK RECEIVED
          Dark Web Leak Monitor
═══════════════════════════════════════════════════════════

RATING: {self._get_star_rating_text(rating)} ({rating}/5)
        {rating_text}

───────────────────────────────────────────────────────────
📝 FEEDBACK MESSAGE
───────────────────────────────────────────────────────────

{message if message else '(No message provided)'}

───────────────────────────────────────────────────────────
📊 DETAILS
───────────────────────────────────────────────────────────

Page:       {page}
IP Address: {ip_address}
Timestamp:  {formatted_time}
User Agent: {user_agent}

═══════════════════════════════════════════════════════════
This is an automated notification from Dark Web Leak Monitor.
© 2026 Dark Web Leak Monitor. All rights reserved.
═══════════════════════════════════════════════════════════
'''
        
        return html_content, text_content
    
    def send_feedback_notification(self, feedback_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Send feedback notification email.
        
        Args:
            feedback_data: Dictionary containing feedback information
                - rating: int (1-5)
                - feedback: str (optional message)
                - page: str (page URL)
                - ip: str (user IP address)
                - timestamp: str (ISO format timestamp)
                - user_agent: str (browser user agent)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_configured():
            return False, 'Email not configured. Please set FEEDBACK_EMAIL_ADDRESS and FEEDBACK_EMAIL_PASSWORD environment variables.'
        
        try:
            # Create email message
            msg = EmailMessage()
            rating = feedback_data.get('rating', 0)
            page = feedback_data.get('page', 'Unknown')
            
            # Set email headers
            msg['Subject'] = f'[Dark Web Leak Monitor] New Feedback - {self._get_star_rating_text(rating)} ({rating}/5) from {page}'
            msg['From'] = f'Dark Web Leak Monitor <{self.email_address}>'
            msg['To'] = self.recipient_email
            msg['Date'] = formatdate(localtime=True)
            msg['X-Priority'] = '1' if rating <= 2 else '3'  # High priority for low ratings
            
            # Generate email content
            html_content, text_content = self._create_email_content(feedback_data)
            
            # Set content (plain text as fallback, HTML as primary)
            msg.set_content(text_content)
            msg.add_alternative(html_content, subtype='html')
            
            # Send email via Gmail SMTP
            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.starttls()  # Enable TLS encryption
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            return True, 'Feedback email sent successfully'
            
        except smtplib.SMTPAuthenticationError:
            return False, 'SMTP authentication failed. Please check your email credentials.'
        except smtplib.SMTPException as e:
            return False, f'SMTP error: {str(e)}'
        except Exception as e:
            return False, f'Failed to send email: {str(e)}'


# Module-level instance for easy import
_mailer_instance: Optional[FeedbackMailer] = None

def get_feedback_mailer() -> FeedbackMailer:
    """Get or create the singleton FeedbackMailer instance."""
    global _mailer_instance
    if _mailer_instance is None:
        print("[FeedbackMailer] Creating new instance...")
        _mailer_instance = FeedbackMailer()
        print(f"[FeedbackMailer] Email: {_mailer_instance.email_address}")
        print(f"[FeedbackMailer] Configured: {_mailer_instance.is_configured()}")
    return _mailer_instance

def send_feedback_email(feedback_data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Convenience function to send feedback email.
    
    Args:
        feedback_data: Dictionary containing feedback information
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    print(f"[FeedbackMailer] send_feedback_email called with rating: {feedback_data.get('rating')}")
    mailer = get_feedback_mailer()
    if not mailer.is_configured():
        print("[FeedbackMailer] WARNING: Email not configured!")
        return False, "Email not configured"
    print(f"[FeedbackMailer] Sending to: {mailer.recipient_email}")
    result = mailer.send_feedback_notification(feedback_data)
    print(f"[FeedbackMailer] Result: {result}")
    return result

def is_email_configured() -> bool:
    """Check if feedback email is configured."""
    mailer = get_feedback_mailer()
    configured = mailer.is_configured()
    print(f"[FeedbackMailer] is_email_configured: {configured}")
    return configured
