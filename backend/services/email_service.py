"""
Email Service - Handle email sending with Jinja templates
"""
import os
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails with Jinja templates"""
    _instance: Optional["EmailService"] = None
    
    def __init__(self):
        """Initialize email service with configuration from environment variables"""
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "Dev Impact")
        
        # Setup Jinja2 environment
        templates_dir = Path(__file__).parent.parent / "templates" / "emails"
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        template_vars: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send an email using a Jinja template
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            template_name: Name of the Jinja template file (e.g., "waitlist_confirmation.html")
            template_vars: Dictionary of variables to pass to the template
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured, skipping email send")
            return False
        
        try:
            # Render template
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(**(template_vars or {}))
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            # Port 587 uses STARTTLS, port 465 uses SSL/TLS directly
            if self.smtp_port == 465:
                # Port 465 uses SSL/TLS directly
                smtp = aiosmtplib.SMTP(
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    use_tls=True,
                )
            else:
                # Port 587 and others use STARTTLS
                smtp = aiosmtplib.SMTP(
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    start_tls=True,
                )
            
            async with smtp:
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    @staticmethod
    def get_instance() -> "EmailService":
        """Get singleton instance of EmailService"""
        if EmailService._instance is None:
            EmailService._instance = EmailService()
        return EmailService._instance

