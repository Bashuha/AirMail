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
    if settings.DEBUG:
        log.warning("DEBUG mode: redirecting all recipients to 'admins' group")
        return get_recipients_from_groups(["admins"])

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

            content_type = 'html' if notification.is_html else 'plain'
            msg.attach(MIMEText(notification.body, content_type, 'utf-8'))

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

