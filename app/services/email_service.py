"""
Email notification service for the AI Storytelling Assistant.
Uses IONOS SMTP for sending HTML email notifications.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader, Template
import os
from pathlib import Path
from datetime import datetime

# Load environment variables from project root
try:
    from dotenv import load_dotenv
    # Get the project root directory (go up from app/services/ to project root)
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / '.env'
    load_dotenv(env_path)
except ImportError:
    # dotenv not available, environment variables should be set by the system
    pass

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications via IONOS SMTP."""
    
    def __init__(self):
        """Initialize the email service with IONOS SMTP configuration."""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.ionos.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', 'notification@inkandquill.io')
        self.smtp_password = os.getenv('SMTP_PASSWORD', 'QuebecUsa1356!')
        self.from_email = os.getenv('FROM_EMAIL', 'notification@inkandquill.io')
        self.from_name = os.getenv('FROM_NAME', 'Ink & Quill')
        
        # Test mode configuration
        self.test_mode = os.getenv('EMAIL_TEST_MODE', 'false').lower() == 'true'
        self.test_email_address = os.getenv('EMAIL_TEST_ADDRESS', 'test@example.com')
        
        # Application details
        self.app_name = os.getenv('PROJECT_NAME', 'AI Storytelling Assistant')
        self.app_url = os.getenv('APP_URL', 'http://localhost:8000')
        
        # Initialize Jinja2 environment for email templates
        template_dir = Path(__file__).parent.parent / 'templates' / 'emails'
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        # Add custom filters
        self.jinja_env.filters['strftime'] = self._strftime_filter
        self.jinja_env.filters['replace'] = self._replace_filter
        
        # Log detailed configuration for debugging
        logger.info(f"SMTP DEBUG: Email service configuration:")
        logger.info(f"  - SMTP Server: {self.smtp_server}")
        logger.info(f"  - SMTP Port: {self.smtp_port}")
        logger.info(f"  - SMTP Username: {self.smtp_username}")
        logger.info(f"  - From Email: {self.from_email}")
        logger.info(f"  - From Name: {self.from_name}")
        logger.info(f"  - Test Mode: {self.test_mode}")
        logger.info(f"  - Test Email Address: {self.test_email_address}")
        logger.info(f"  - App Name: {self.app_name}")
        logger.info(f"  - App URL: {self.app_url}")
        logger.info(f"SMTP DEBUG: Email service initialized successfully")
    
    def _strftime_filter(self, value, format='%Y-%m-%d %H:%M:%S'):
        """Custom Jinja2 filter for datetime formatting."""
        if value == "now":
            return datetime.now().strftime(format)
        elif isinstance(value, datetime):
            return value.strftime(format)
        elif isinstance(value, str):
            try:
                # Try to parse the string as a datetime
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime(format)
            except:
                return value
        return str(value)
    
    def _replace_filter(self, value, old, new):
        """Custom Jinja2 filter for string replacement."""
        if isinstance(value, str):
            return value.replace(old, new)
        return str(value).replace(old, new)
    
    def _create_smtp_connection(self) -> smtplib.SMTP:
        """Create and configure SMTP connection with detailed debugging."""
        try:
            logger.info(f"SMTP DEBUG: Connecting to {self.smtp_server}:{self.smtp_port}")
            
            # Enable SMTP debugging
            smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
            smtp.set_debuglevel(1)  # Enable detailed SMTP debugging
            
            logger.info("SMTP DEBUG: Connection established, starting TLS...")
            smtp.starttls()  # Enable TLS encryption
            logger.info("SMTP DEBUG: TLS started successfully")
            
            logger.info(f"SMTP DEBUG: Logging in with username: {self.smtp_username}")
            smtp.login(self.smtp_username, self.smtp_password)
            logger.info("SMTP DEBUG: Login successful")
            
            return smtp
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP DEBUG: Connection failed to {self.smtp_server}:{self.smtp_port} - {e}")
            raise
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP DEBUG: Authentication failed for {self.smtp_username} - {e}")
            raise
        except smtplib.SMTPException as e:
            logger.error(f"SMTP DEBUG: SMTP error - {e}")
            raise
        except Exception as e:
            logger.error(f"SMTP DEBUG: Unexpected error creating SMTP connection: {e}")
            raise
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> tuple[str, str]:
        """Render email template with context data."""
        try:
            template = self.jinja_env.get_template(template_name)
            
            # Add common context variables
            context.update({
                'app_name': self.app_name,
                'app_url': self.app_url,
                'from_name': self.from_name
            })
            
            # Render HTML content
            html_content = template.render(**context)
            
            # Generate plain text version (basic fallback)
            # This is a simple HTML-to-text conversion
            import re
            text_content = re.sub('<[^<]+?>', '', html_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            return html_content, text_content
            
        except Exception as e:
            logger.error(f"Failed to render email template {template_name}: {e}")
            raise
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        context: Optional[Dict[str, Any]] = None,
        to_name: Optional[str] = None
    ) -> bool:
        """
        Send an email using the specified template.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            template_name: Name of the email template file (e.g., 'welcome.html')
            context: Dictionary of variables to pass to the template
            to_name: Optional recipient name
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if context is None:
            context = {}
        
        try:
            # In test mode, redirect to test email
            original_email = to_email
            if self.test_mode:
                to_email = self.test_email_address
                context['test_mode'] = True
                context['original_recipient'] = original_email
                logger.info(f"SMTP DEBUG: Test mode enabled - Redirecting email from {original_email} to {to_email}")
            
            logger.info(f"SMTP DEBUG: Preparing email - To: {to_email}, Subject: {subject}")
            
            # Render email template
            logger.info(f"SMTP DEBUG: Rendering template: {template_name}")
            html_content, text_content = self._render_template(template_name, context)
            logger.info(f"SMTP DEBUG: Template rendered successfully - HTML length: {len(html_content)}, Text length: {len(text_content)}")
            
            # Create email message
            logger.info("SMTP DEBUG: Creating MIME message...")
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = formataddr((self.from_name, self.from_email))
            msg['To'] = formataddr((to_name or to_email, to_email))
            
            # Add additional headers for better delivery
            msg['Reply-To'] = self.from_email
            msg['X-Mailer'] = f'{self.app_name} Email Service'
            msg['Precedence'] = 'bulk'
            msg['List-Unsubscribe'] = f'<mailto:{self.from_email}?subject=Unsubscribe>'
            
            logger.info(f"SMTP DEBUG: Message headers set - From: {self.from_email}, To: {to_email}")
            
            # Add plain text and HTML parts
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            logger.info("SMTP DEBUG: Message parts attached (text + HTML)")
            
            # Send email
            logger.info("SMTP DEBUG: Starting email transmission...")
            with self._create_smtp_connection() as smtp:
                logger.info("SMTP DEBUG: SMTP connection established, sending message...")
                
                # Get detailed send response
                send_errors = smtp.send_message(msg)
                
                if send_errors:
                    logger.error(f"SMTP DEBUG: Send errors occurred: {send_errors}")
                    return False
                else:
                    logger.info("SMTP DEBUG: Message sent without errors")
            
            logger.info(f"SMTP DEBUG: Email transmission completed successfully to {to_email} (Subject: {subject})")
            
            # Additional debugging info
            logger.info(f"SMTP DEBUG: Email details summary:")
            logger.info(f"  - SMTP Server: {self.smtp_server}:{self.smtp_port}")
            logger.info(f"  - From: {self.from_email} ({self.from_name})")
            logger.info(f"  - To: {to_email}")
            logger.info(f"  - Subject: {subject}")
            logger.info(f"  - Test Mode: {self.test_mode}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_welcome_email(self, user_email: str, user_name: str, is_test: bool = False) -> bool:
        """Send welcome email to new user."""
        context = {
            'user_name': user_name,
            'login_url': f"{self.app_url}/auth/login",
            'dashboard_url': f"{self.app_url}/",
            'support_email': self.from_email
        }
        
        # Override test mode if is_test is True
        original_test_mode = self.test_mode
        if is_test:
            self.test_mode = True
            # Keep the original test email address from environment
        
        success = await self.send_email(
            to_email=user_email,
            to_name=user_name,
            subject=f"Welcome to {self.app_name}!",
            template_name='welcome.html',
            context=context
        )
        
        # Restore original test mode
        if is_test:
            self.test_mode = original_test_mode
            
        return success
    
    async def send_password_reset_email(self, user_email: str, user_name: str, reset_token: str, is_test: bool = False) -> bool:
        """Send password reset email."""
        reset_url = f"{self.app_url}/auth/reset-password?token={reset_token}"
        
        context = {
            'user_name': user_name,
            'reset_url': reset_url,
            'reset_token': reset_token,
            'support_email': self.from_email,
            'expiry_hours': 24  # Assuming 24 hour expiry
        }
        
        # Override test mode if is_test is True
        original_test_mode = self.test_mode
        if is_test:
            self.test_mode = True
            # Keep the original test email address from environment
        
        success = await self.send_email(
            to_email=user_email,
            to_name=user_name,
            subject=f"{self.app_name} - Password Reset Request",
            template_name='password_reset.html',
            context=context
        )
        
        # Restore original test mode
        if is_test:
            self.test_mode = original_test_mode
            
        return success
    
    async def send_story_completion_email(
        self, 
        user_email: str, 
        user_name: str, 
        story_title: str,
        milestone_type: str = "completion",
        story_url: str = "#",
        is_test: bool = False
    ) -> bool:
        """Send story completion/milestone notification email."""
        context = {
            'user_name': user_name,
            'story_title': story_title,
            'story_url': story_url,
            'milestone_type': milestone_type,
            'dashboard_url': f"{self.app_url}/",
            'support_email': self.from_email
        }
        
        subject_prefix = {
            'completion': 'Story Completed',
            'milestone': 'Story Milestone Reached',
            'published': 'Story Published'
        }.get(milestone_type, 'Story Update')
        
        # Override test mode if is_test is True
        original_test_mode = self.test_mode
        if is_test:
            self.test_mode = True
            # Keep the original test email address from environment
        
        success = await self.send_email(
            to_email=user_email,
            to_name=user_name,
            subject=f"{self.app_name} - {subject_prefix}: {story_title}",
            template_name='story_completion.html',
            context=context
        )
        
        # Restore original test mode
        if is_test:
            self.test_mode = original_test_mode
            
        return success
    
    async def send_maintenance_email(
        self,
        user_email: str,
        user_name: str,
        maintenance_title: str,
        maintenance_message: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        is_test: bool = False
    ) -> bool:
        """Send system maintenance notification email."""
        context = {
            'user_name': user_name,
            'maintenance_title': maintenance_title,
            'maintenance_message': maintenance_message,
            'start_time': start_time,
            'end_time': end_time,
            'status_url': f"{self.app_url}/status",
            'support_email': self.from_email
        }
        
        # Override test mode if is_test is True
        original_test_mode = self.test_mode
        if is_test:
            self.test_mode = True
            # Keep the original test email address from environment
        
        success = await self.send_email(
            to_email=user_email,
            to_name=user_name,
            subject=f"{self.app_name} - System Maintenance: {maintenance_title}",
            template_name='maintenance.html',
            context=context
        )
        
        # Restore original test mode
        if is_test:
            self.test_mode = original_test_mode
            
        return success
    
    def test_email_configuration(self, test_email: str) -> Dict[str, Any]:
        """Test email configuration by sending a test email."""
        try:
            context = {
                'test_email': test_email,
                'smtp_server': self.smtp_server,
                'smtp_port': self.smtp_port,
                'smtp_username': self.smtp_username
            }
            
            success = self.send_email(
                to_email=test_email,
                subject=f"{self.app_name} - Email Configuration Test",
                template_name='test.html',
                context=context
            )
            
            return {
                'success': success,
                'message': 'Test email sent successfully' if success else 'Failed to send test email',
                'smtp_server': self.smtp_server,
                'smtp_port': self.smtp_port,
                'from_email': self.from_email,
                'test_mode': self.test_mode
            }
            
        except Exception as e:
            logger.error(f"Email configuration test failed: {e}")
            return {
                'success': False,
                'message': f'Email configuration test failed: {str(e)}',
                'error': str(e)
            }
    
    async def send_test_email(
        self,
        test_email: str,
        custom_subject: Optional[str] = None,
        custom_message: Optional[str] = None,
        is_test: bool = False
    ) -> bool:
        """Send a test email with optional custom subject and message."""
        try:
            context = {
                'test_email': test_email,
                'smtp_server': self.smtp_server,
                'smtp_port': self.smtp_port,
                'smtp_username': self.smtp_username,
                'custom_subject': custom_subject,
                'custom_message': custom_message
            }
            
            subject = custom_subject or f"{self.app_name} - Email Configuration Test"
            
            # Override test mode if is_test is True
            original_test_mode = self.test_mode
            if is_test:
                self.test_mode = True
                # Keep the original test email address from environment
            
            success = await self.send_email(
                to_email=test_email,
                to_name="Test User",
                subject=subject,
                template_name='test.html',
                context=context
            )
            
            # Restore original test mode
            if is_test:
                self.test_mode = original_test_mode
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send test email: {e}")
            return False


# Global email service instance
email_service = EmailService()


def get_email_service() -> EmailService:
    """Get the global email service instance."""
    return email_service