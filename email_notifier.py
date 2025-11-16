"""
Email Notification System for TBBAS
Sends notifications for updates, errors, and status reports
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailNotifier:
    """
    Send email notifications for TBBAS updates

    Supports multiple email services:
    - Gmail SMTP
    - SendGrid
    - Mailgun
    - Any SMTP server
    """

    def __init__(self):
        # Email configuration from environment variables
        self.enabled = os.getenv('EMAIL_NOTIFICATIONS_ENABLED', 'True').lower() == 'true'
        self.to_email = os.getenv('NOTIFICATION_EMAIL', 'blood@teamarete.net')
        self.from_email = os.getenv('FROM_EMAIL', 'tbbas@teamarete.net')

        # SMTP configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')

        # Alternative: SendGrid API (if configured)
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY', '')

        if not self.enabled:
            logger.info("Email notifications are disabled")

    def send_email(self, subject, body, is_html=False):
        """
        Send an email notification

        Args:
            subject: Email subject
            body: Email body (plain text or HTML)
            is_html: If True, send as HTML email
        """
        if not self.enabled:
            logger.debug("Email notifications disabled - skipping")
            return False

        try:
            # Try SendGrid first if configured
            if self.sendgrid_api_key:
                return self._send_via_sendgrid(subject, body, is_html)

            # Fall back to SMTP
            return self._send_via_smtp(subject, body, is_html)

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def _send_via_smtp(self, subject, body, is_html=False):
        """Send email via SMTP"""
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured - cannot send email")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = self.to_email

            # Attach body
            mime_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, mime_type))

            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {self.to_email}")
            return True

        except Exception as e:
            logger.error(f"SMTP send failed: {e}")
            return False

    def _send_via_sendgrid(self, subject, body, is_html=False):
        """Send email via SendGrid API"""
        try:
            import requests

            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {self.sendgrid_api_key}",
                "Content-Type": "application/json"
            }

            content_type = "text/html" if is_html else "text/plain"

            data = {
                "personalizations": [{
                    "to": [{"email": self.to_email}]
                }],
                "from": {"email": self.from_email},
                "subject": subject,
                "content": [{
                    "type": content_type,
                    "value": body
                }]
            }

            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 202:
                logger.info(f"Email sent via SendGrid to {self.to_email}")
                return True
            else:
                logger.error(f"SendGrid failed: {response.status_code} - {response.text}")
                return False

        except ImportError:
            logger.warning("SendGrid configured but requests library not available")
            return False
        except Exception as e:
            logger.error(f"SendGrid send failed: {e}")
            return False

    def notify_daily_collection(self, games_collected, sources_summary, errors=None):
        """
        Send notification about daily box score collection

        Args:
            games_collected: Number of games collected
            sources_summary: Dict with breakdown by source
            errors: Optional list of errors
        """
        subject = f"TBBAS Daily Update - {games_collected} games collected"

        body = f"""
TBBAS Daily Box Score Collection Report
Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

========================================
SUMMARY
========================================
Total Games Collected: {games_collected}

Source Breakdown:
{self._format_sources(sources_summary)}

========================================
STATUS
========================================
"""

        if errors:
            body += f"⚠️ Errors encountered: {len(errors)}\n"
            for error in errors[:5]:  # Show first 5 errors
                body += f"  - {error}\n"
        else:
            body += "✓ Collection completed successfully\n"

        body += f"\nNext collection: Tomorrow at 6:00 AM\n"
        body += f"\nView rankings: https://web-production-0429a.up.railway.app/\n"

        self.send_email(subject, body)

    def notify_weekly_rankings_update(self, rankings_summary, errors=None):
        """
        Send notification about weekly rankings update

        Args:
            rankings_summary: Dict with rankings info by classification
            errors: Optional list of errors
        """
        subject = f"TBBAS Weekly Rankings Updated"

        body = f"""
TBBAS Weekly Rankings Update Report
Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

========================================
RANKINGS UPDATED
========================================
"""

        if rankings_summary:
            for league, classifications in rankings_summary.items():
                body += f"\n{league.upper()}:\n"
                for classification, count in classifications.items():
                    body += f"  {classification}: {count} teams\n"

        body += "\n========================================\n"
        body += "DATA SOURCES\n"
        body += "========================================\n"
        body += "1. Calculated from box score data\n"
        body += "2. MaxPreps rankings\n"
        body += "3. TABC rankings (backup)\n"
        body += "4. GASO rankings\n"

        if errors:
            body += f"\n⚠️ Errors encountered: {len(errors)}\n"
            for error in errors[:5]:
                body += f"  - {error}\n"
        else:
            body += "\n✓ Update completed successfully\n"

        body += f"\nNext update: Next Monday at 6:00 AM\n"
        body += f"\nView rankings: https://web-production-0429a.up.railway.app/\n"

        self.send_email(subject, body)

    def notify_error(self, error_type, error_message, traceback_info=None):
        """
        Send error notification

        Args:
            error_type: Type of error (e.g., "Box Score Collection", "Rankings Update")
            error_message: Error message
            traceback_info: Optional traceback information
        """
        subject = f"⚠️ TBBAS Error: {error_type}"

        body = f"""
TBBAS Error Report
Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

========================================
ERROR DETAILS
========================================
Type: {error_type}
Message: {error_message}

"""

        if traceback_info:
            body += f"Traceback:\n{traceback_info}\n"

        body += "\nPlease check the Railway logs for more details.\n"
        body += "Dashboard: https://railway.app\n"

        self.send_email(subject, body)

    def _format_sources(self, sources):
        """Format sources summary"""
        if not sources:
            return "  No data"

        lines = []
        for source, count in sources.items():
            lines.append(f"  - {source}: {count} games")
        return "\n".join(lines)

    def test_email(self):
        """Send a test email to verify configuration"""
        subject = "TBBAS Email Notifications - Test"
        body = f"""
This is a test email from TBBAS.

Email notifications are configured correctly!

Configuration:
- From: {self.from_email}
- To: {self.to_email}
- SMTP Server: {self.smtp_server}
- Port: {self.smtp_port}

If you received this email, notifications are working.

Test sent at: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
"""

        result = self.send_email(subject, body)
        if result:
            logger.info("Test email sent successfully!")
        else:
            logger.error("Test email failed to send")

        return result


def test_notifier():
    """Test the email notifier"""
    notifier = EmailNotifier()

    print("\nEmail Notifier Test")
    print("=" * 50)
    print(f"Enabled: {notifier.enabled}")
    print(f"To: {notifier.to_email}")
    print(f"From: {notifier.from_email}")
    print(f"SMTP Server: {notifier.smtp_server}:{notifier.smtp_port}")
    print("=" * 50)

    # Test daily collection notification
    print("\nTesting daily collection notification...")
    notifier.notify_daily_collection(
        games_collected=25,
        sources_summary={
            'MaxPreps': 20,
            'Newspapers': 5
        },
        errors=None
    )

    # Test weekly rankings notification
    print("\nTesting weekly rankings notification...")
    notifier.notify_weekly_rankings_update(
        rankings_summary={
            'uil': {
                'AAAAAA': 25,
                'AAAAA': 25,
                'AAAA': 25
            },
            'private': {
                'TAPPS_6A': 10,
                'TAPPS_5A': 10
            }
        },
        errors=None
    )


if __name__ == '__main__':
    test_notifier()
