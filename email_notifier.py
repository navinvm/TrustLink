"""
TrustLink Email Notification System
Sends email notifications for user feedback and important events
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os


class EmailNotifier:
    """
    Email notification service for TrustLink
    Supports Gmail, Outlook, and custom SMTP servers
    """
    
    def __init__(self, config=None):
        """
        Initialize email notifier with configuration
        
        Config options:
        {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'your-email@gmail.com',
            'sender_password': 'your-app-password',
            'admin_email': 'admin@example.com',
            'enabled': True
        }
        """
        self.config = config or {}
        
        # Get config from environment variables if not provided
        self.smtp_server = self.config.get('smtp_server', os.environ.get('SMTP_SERVER', 'smtp.gmail.com'))
        self.smtp_port = self.config.get('smtp_port', int(os.environ.get('SMTP_PORT', 587)))
        self.sender_email = self.config.get('sender_email', os.environ.get('SENDER_EMAIL'))
        self.sender_password = self.config.get('sender_password', os.environ.get('SENDER_PASSWORD'))
        self.admin_email = self.config.get('admin_email', os.environ.get('ADMIN_EMAIL'))
        self.enabled = self.config.get('enabled', os.environ.get('EMAIL_NOTIFICATIONS_ENABLED', 'false').lower() == 'true')
        
    def is_configured(self):
        """Check if email is properly configured"""
        return bool(
            self.enabled and 
            self.sender_email and 
            self.sender_password and 
            self.admin_email
        )
    
    def send_email(self, to_email, subject, html_body, plain_body=None):
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            plain_body: Plain text fallback (optional)
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.is_configured():
            print("⚠️ Email not configured - skipping notification")
            return False
        
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = to_email
            
            # Add plain text version
            if plain_body:
                part1 = MIMEText(plain_body, 'plain')
                message.attach(part1)
            
            # Add HTML version
            part2 = MIMEText(html_body, 'html')
            message.attach(part2)
            
            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print(f"✅ Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def send_feedback_notification(self, feedback_data):
        """
        Send notification to admin about new user feedback
        
        Args:
            feedback_data: Dictionary with feedback information
                {
                    'url': str,
                    'original_prediction': str,
                    'correct_label': str,
                    'feedback_type': str,
                    'user_id': int (optional),
                    'username': str (optional),
                    'timestamp': str
                }
        """
        if not self.is_configured():
            return False
        
        url = feedback_data.get('url', 'Unknown')
        original = feedback_data.get('original_prediction', 'Unknown')
        correct = feedback_data.get('correct_label', 'Unknown')
        feedback_type = feedback_data.get('feedback_type', 'Unknown')
        username = feedback_data.get('username', 'Anonymous')
        timestamp = feedback_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Determine if this is a correction
        is_correction = original != correct
        icon = '⚠️' if is_correction else '✅'
        status = 'INCORRECT PREDICTION' if is_correction else 'Positive Feedback'
        
        subject = f"{icon} TrustLink: {status} - User Feedback"
        
        # HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px; }}
                .container {{ background: white; border-radius: 10px; padding: 30px; max-width: 600px; margin: 0 auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .status {{ padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; font-weight: bold; font-size: 18px; }}
                .status.correction {{ background: #ffebee; color: #c62828; border: 2px solid #ef5350; }}
                .status.positive {{ background: #e8f5e9; color: #2e7d32; border: 2px solid #66bb6a; }}
                .info-row {{ padding: 12px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }}
                .info-row:last-child {{ border-bottom: none; }}
                .info-label {{ font-weight: bold; color: #666; }}
                .info-value {{ color: #333; word-break: break-all; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
                .cta-button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; border-radius: 6px; text-decoration: none; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 TrustLink Feedback Alert</h1>
                </div>
                
                <div class="status {'correction' if is_correction else 'positive'}">
                    {icon} {status}
                </div>
                
                <div class="info-row">
                    <span class="info-label">URL:</span>
                    <span class="info-value">{url}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Original Prediction:</span>
                    <span class="info-value">{original}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">User Says:</span>
                    <span class="info-value">{correct}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Feedback Type:</span>
                    <span class="info-value">{feedback_type}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Submitted By:</span>
                    <span class="info-value">{username}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Timestamp:</span>
                    <span class="info-value">{timestamp}</span>
                </div>
                
                <div style="text-align: center;">
                    <a href="{{ dashboard_url }}" class="cta-button">View Dashboard</a>
                </div>
                
                <div class="footer">
                    <p>This feedback has been automatically added to the training dataset.</p>
                    <p>Consider retraining the model when enough feedback accumulates.</p>
                    <p><small>© 2026 TrustLink. NAVIN</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        plain_body = f"""
TrustLink Feedback Alert
{'='*50}

{status}

URL: {url}
Original Prediction: {original}
User Says: {correct}
Feedback Type: {feedback_type}
Submitted By: {username}
Timestamp: {timestamp}

This feedback has been automatically added to the training dataset.
Consider retraining the model when enough feedback accumulates.

View Dashboard: {{ dashboard_url }}
        """
        
        return self.send_email(self.admin_email, subject, html_body, plain_body)
    
    def send_retrain_notification(self, retrain_data):
        """
        Send notification about model retraining
        
        Args:
            retrain_data: Dictionary with retraining information
                {
                    'version': str,
                    'accuracy': float,
                    'precision': float,
                    'recall': float,
                    'training_samples': int,
                    'timestamp': str
                }
        """
        if not self.is_configured():
            return False
        
        version = retrain_data.get('version', 'Unknown')
        accuracy = retrain_data.get('accuracy', 0) * 100
        precision = retrain_data.get('precision', 0) * 100
        recall = retrain_data.get('recall', 0) * 100
        samples = retrain_data.get('training_samples', 0)
        timestamp = retrain_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        subject = f"🧠 TrustLink: Model Retrained Successfully - {version}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px; }}
                .container {{ background: white; border-radius: 10px; padding: 30px; max-width: 600px; margin: 0 auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .metrics {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin: 20px 0; }}
                .metric {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
                .metric-value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
                .metric-label {{ font-size: 14px; color: #666; margin-top: 5px; }}
                .info {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196f3; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 Model Retrained Successfully!</h1>
                </div>
                
                <div class="info">
                    <strong>New Model Version:</strong> {version}<br>
                    <strong>Training Samples:</strong> {samples}<br>
                    <strong>Timestamp:</strong> {timestamp}
                </div>
                
                <h2 style="text-align: center; color: #333;">Performance Metrics</h2>
                
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">{accuracy:.1f}%</div>
                        <div class="metric-label">Accuracy</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{precision:.1f}%</div>
                        <div class="metric-label">Precision</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{recall:.1f}%</div>
                        <div class="metric-label">Recall</div>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <p style="color: #666;">The new model is now live and serving predictions!</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_body = f"""
TrustLink: Model Retrained Successfully
{'='*50}

New Model Version: {version}
Training Samples: {samples}
Timestamp: {timestamp}

Performance Metrics:
- Accuracy: {accuracy:.1f}%
- Precision: {precision:.1f}%
- Recall: {recall:.1f}%

The new model is now live and serving predictions!
        """
        
        return self.send_email(self.admin_email, subject, html_body, plain_body)
    
    def send_verification_email(self, user_email, username, verification_token, base_url='http://localhost:5000'):
        """
        Send email verification to new user
        
        Args:
            user_email: User's email address
            username: User's username
            verification_token: Unique verification token
            base_url: Base URL for verification link
        """
        if not self.is_configured():
            return False
        
        verification_link = f"{base_url}/verify-email?token={verification_token}"
        
        subject = "🔐 Verify Your TrustLink Account"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px; }}
                .container {{ background: white; border-radius: 10px; padding: 40px; max-width: 600px; margin: 0 auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; text-align: center; margin-bottom: 30px; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .content {{ color: #333; line-height: 1.8; font-size: 16px; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 16px 40px; border-radius: 8px; text-decoration: none; margin: 30px 0; font-size: 18px; font-weight: bold; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }}
                .cta-button:hover {{ box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6); }}
                .info-box {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; }}
                .warning {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107; color: #856404; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ Welcome to TrustLink!</h1>
                </div>
                
                <div class="content">
                    <h2 style="color: #333;">Hi {username},</h2>
                    
                    <p>Thank you for registering with TrustLink - your AI-powered phishing protection system!</p>
                    
                    <p>To complete your registration and start protecting yourself from phishing attacks, please verify your email address by clicking the button below:</p>
                    
                    <div style="text-align: center;">
                        <a href="{verification_link}" class="cta-button">Verify Email Address</a>
                    </div>
                    
                    <div class="info-box">
                        <strong>Can't click the button?</strong><br>
                        Copy and paste this link into your browser:<br>
                        <a href="{verification_link}" style="color: #667eea; word-break: break-all;">{verification_link}</a>
                    </div>
                    
                    <div class="warning">
                        ⏰ <strong>Important:</strong> This verification link will expire in 24 hours.
                    </div>
                    
                    <p>Once verified, you'll have access to:</p>
                    <ul style="color: #555; line-height: 2;">
                        <li>✅ Real-time phishing detection</li>
                        <li>📊 Personal dashboard with scan history</li>
                        <li>🔑 API keys for programmatic access</li>
                        <li>🌐 Browser extension integration</li>
                        <li>📈 Advanced analytics</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>If you didn't create this account, you can safely ignore this email.</p>
                    <p><small>© 2026 TrustLink. NAVIN</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_body = f"""
TrustLink - Verify Your Email Address
{'='*50}

Hi {username},

Thank you for registering with TrustLink!

To complete your registration, please verify your email address by visiting this link:

{verification_link}

This link will expire in 24 hours.

Once verified, you'll have access to:
- Real-time phishing detection
- Personal dashboard with scan history
- API keys for programmatic access
- Browser extension integration
- Advanced analytics

If you didn't create this account, you can safely ignore this email.

© 2026 TrustLink. NAVIN
        """
        
        return self.send_email(user_email, subject, html_body, plain_body)
    
    def send_password_reset_email(self, user_email, username, reset_token, base_url='http://localhost:5000'):
        """
        Send password reset email to user
        
        Args:
            user_email: User's email address
            username: User's username
            reset_token: Unique password reset token
            base_url: Base URL for reset link
        """
        if not self.is_configured():
            return False
        
        reset_link = f"{base_url}/reset-password?token={reset_token}"
        
        subject = "🔐 Reset Your TrustLink Password"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px; }}
                .container {{ background: white; border-radius: 10px; padding: 40px; max-width: 600px; margin: 0 auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; border-radius: 8px; text-align: center; margin-bottom: 30px; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .content {{ color: #333; line-height: 1.8; font-size: 16px; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 16px 40px; border-radius: 8px; text-decoration: none; margin: 30px 0; font-size: 18px; font-weight: bold; box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4); }}
                .info-box {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f5576c; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; }}
                .warning {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107; color: #856404; }}
                .security-notice {{ background: #ffebee; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ef5350; color: #c62828; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset Request</h1>
                </div>
                
                <div class="content">
                    <h2 style="color: #333;">Hi {username},</h2>
                    
                    <p>We received a request to reset your TrustLink account password.</p>
                    
                    <p>Click the button below to create a new password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="cta-button">Reset Password</a>
                    </div>
                    
                    <div class="info-box">
                        <strong>Can't click the button?</strong><br>
                        Copy and paste this link into your browser:<br>
                        <a href="{reset_link}" style="color: #f5576c; word-break: break-all;">{reset_link}</a>
                    </div>
                    
                    <div class="warning">
                        ⏰ <strong>Important:</strong> This reset link will expire in 1 hour for security reasons.
                    </div>
                    
                    <div class="security-notice">
                        🛡️ <strong>Security Notice:</strong><br>
                        If you didn't request this password reset, please ignore this email. Your password will remain unchanged.
                        <br><br>
                        For additional security, consider changing your password immediately if you suspect unauthorized access.
                    </div>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from TrustLink. Please do not reply.</p>
                    <p><small>© 2026 TrustLink. NAVIN</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_body = f"""
TrustLink - Password Reset Request
{'='*50}

Hi {username},

We received a request to reset your TrustLink account password.

To reset your password, visit this link:

{reset_link}

This link will expire in 1 hour for security reasons.

SECURITY NOTICE:
If you didn't request this password reset, please ignore this email. 
Your password will remain unchanged.

For additional security, consider changing your password immediately 
if you suspect unauthorized access.

© 2026 TrustLink. NAVIN
        """
        
        return self.send_email(user_email, subject, html_body, plain_body)


if __name__ == '__main__':
    print("=" * 60)
    print("📧 TrustLink Email Notification System")
    print("=" * 60)
    print("\nConfiguration Options:")
    print("\n1. Environment Variables (Recommended):")
    print("   - SMTP_SERVER (default: smtp.gmail.com)")
    print("   - SMTP_PORT (default: 587)")
    print("   - SENDER_EMAIL")
    print("   - SENDER_PASSWORD")
    print("   - ADMIN_EMAIL")
    print("   - EMAIL_NOTIFICATIONS_ENABLED (true/false)")
    
    print("\n2. Gmail Setup:")
    print("   a. Enable 2-Factor Authentication")
    print("   b. Generate App Password:")
    print("      Google Account → Security → App Passwords")
    print("   c. Use the 16-character app password")
    
    print("\n3. Example Usage:")
    print("""
    # In app.py
    from email_notifier import EmailNotifier
    
    notifier = EmailNotifier({
        'sender_email': 'your-email@gmail.com',
        'sender_password': 'your-app-password',
        'admin_email': 'admin@example.com',
        'enabled': True
    })
    
    # Send feedback notification
    notifier.send_feedback_notification({
        'url': 'http://phishing-site.com',
        'original_prediction': 'Safe',
        'correct_label': 'Phishing',
        'feedback_type': 'correction',
        'username': 'john_doe',
        'timestamp': '2026-02-05 14:30:00'
    })
    """)
    
    print("\n✅ Email system ready to use!")
