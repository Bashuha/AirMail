import logging
import smtplib
from typing import List

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from config import settings
from app.schemas import Notification
from app.db import Session, Group, Staff, StaffContact

from sqlalchemy import select


log = logging.getLogger(__name__)


def get_recipients_from_groups(groups: List[str]):
    with Session() as session:
        query = (
            select(StaffContact.value)
            .join(Staff, StaffContact.staff_id == Staff.id)
            .join(Staff.groups)
            .where(Group.name.in_(groups))
            .where(Staff.is_active == True)
        )
        return session.execute(query).scalars().unique().all()


def prepare_data_for_mail(notification: Notification):
    recipients = notification.recipients
    if groups := notification.groups:
        recipients.extend(get_recipients_from_groups(groups))
    return recipients


def send_email(notification: Notification) -> bool:
    recipients = prepare_data_for_mail(notification)
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        for recipient in recipients:
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_FROM
            msg['To'] = recipient
            msg['Subject'] = notification.subject

            msg.attach(MIMEText(notification.body, 'plain'))

            for attachment in notification.attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.content)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{attachment.filename}"',
                )
                msg.attach(part)

            server.send_message(msg)
            log.debug(f"Email successfully sent to {recipient}")

    return True


def send_email_with_links(notification: Notification) -> bool:
    recipients = prepare_data_for_mail(notification)
    
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        for recipient in recipients:
            msg = MIMEMultipart('alternative')
            msg['From'] = settings.SMTP_FROM
            msg['To'] = recipient
            msg['Subject'] = notification.subject

            links_html = "<ul>"
            links_text = ""

            for attachment in notification.attachments:
                links_html += f'<li><a href="{attachment.url}">Download {attachment.filename}</a></li>'
                links_text += f"- {attachment.filename}: {attachment.url}\n"

            links_html += "</ul>"

            text_body = f"{notification.body}\n\nLinks to documents:\n{links_text}"
            
            html_body = f"""
            <html>
              <body>
                <p>{notification.body}</p>
                <p><b>Your documents:</b></p>
                {links_html}
              </body>
            </html>
            """

            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)

            server.send_message(msg)
            
    return True