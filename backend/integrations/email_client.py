"""
Email integration client.
Handles email sending with Jinja templates via SMTP.
"""

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from pathlib import Path
import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape
import aiosmtplib
from backend.core.config import EmailConfig

logger = logging.getLogger(__name__)


class EmailClient:
    """Client for sending emails with Jinja templates."""

    def __init__(self, config: EmailConfig):
        """
        Initialize email client with configuration.

        Args:
            config: Email configuration object
        """
        self.config = config

        # Setup Jinja2 environment for email templates
        templates_dir = Path(__file__).parent.parent / "templates" / "emails"
        templates_dir.mkdir(parents=True, exist_ok=True)

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        template_vars: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send an email using a Jinja template.

        Args:
            to_email: Recipient email address
            subject: Email subject
            template_name: Name of the Jinja template file (e.g., "waitlist_confirmation.html")
            template_vars: Dictionary of variables to pass to the template

        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.config.user or not self.config.password:
            logger.warning("SMTP credentials not configured, skipping email send")
            return False

        try:
            # Render template
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(**(template_vars or {}))

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.config.from_name} <{self.config.from_email}>"
            message["To"] = to_email

            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Send email
            # Port 587 uses STARTTLS, port 465 uses SSL/TLS directly
            if self.config.port == 465:
                # Port 465 uses SSL/TLS directly
                smtp = aiosmtplib.SMTP(
                    hostname=self.config.host,
                    port=self.config.port,
                    use_tls=True,
                )
            else:
                # Port 587 and others use STARTTLS
                smtp = aiosmtplib.SMTP(
                    hostname=self.config.host,
                    port=self.config.port,
                    start_tls=True,
                )

            async with smtp:
                await smtp.login(self.config.user, self.config.password)
                await smtp.send_message(message)

            logger.info("Email sent successfully to %s", to_email)
            return True

        except Exception as e: # pylint: disable=broad-exception-caught
            logger.error("Failed to send email to %s: %s", to_email, e)
            return False
