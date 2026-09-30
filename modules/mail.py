"""Password reset delivery; local outbox is opt-in and never served as an asset."""
import smtplib
import ssl
import uuid
from email.message import EmailMessage
from pathlib import Path
from flask import current_app
from werkzeug.exceptions import ServiceUnavailable


def send_reset(recipient, token):
    config = current_app.config
    message = EmailMessage()
    message['Subject'] = 'Reset your AUDIA password'
    message['From'] = config['SMTP_FROM']
    message['To'] = recipient
    message.set_content('Use this link within 30 minutes to reset your password:\n\n'
                        f'{config["APP_URL"]}/#reset/{token}\n\n'
                        'If you did not request this, you can ignore this email.')
    backend = config['MAIL_BACKEND']
    if backend == 'memory' and current_app.testing:
        current_app.extensions.setdefault('outbox', []).append(message)
    elif backend == 'file':
        folder = Path(current_app.instance_path) / 'mail'
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f'{uuid.uuid4().hex}.eml').write_text(message.as_string(), encoding='utf-8')
    elif backend == 'smtp':
        try:
            with smtplib.SMTP(config['SMTP_HOST'], config['SMTP_PORT'], timeout=15) as server:
                server.starttls(context=ssl.create_default_context())
                if config['SMTP_USER']:
                    server.login(config['SMTP_USER'], config['SMTP_PASSWORD'])
                server.send_message(message)
        except (OSError, smtplib.SMTPException) as error:
            raise ServiceUnavailable('Password recovery is temporarily unavailable.') from error
    else:
        raise ServiceUnavailable('Password recovery is unavailable.')
