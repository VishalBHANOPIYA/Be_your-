from flask_mail import Message
from flask import current_app, render_template
from app.extensions import mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            app.logger.info(f"Email sent successfully to {msg.recipients}")
        except Exception as e:
            app.logger.error(f"Failed to send email to {msg.recipients}: {e}")

def send_email(to, subject, template, **kwargs):
    """
    Sends an email asynchronously using Flask-Mail.
    
    :param to: Recipient email address
    :param subject: Email subject
    :param template: Name of the template in app/templates/email/ (without .html)
    :param kwargs: Variables to pass to the template
    """
    sender = current_app.config.get('MAIL_USERNAME')
    if not sender:
        current_app.logger.warning("MAIL_USERNAME is not set. Emails cannot be sent via SMTP.")
        # Development Fallback: Log and write to dev_emails.txt for easy developer access
        otp = kwargs.get('otp', 'N/A')
        log_msg = f"\n=== DEVELOPMENT EMAIL FALLBACK ===\nTo: {to}\nSubject: {subject}\nOTP Code: {otp}\n==================================\n"
        current_app.logger.info(log_msg)
        try:
            with open("dev_emails.txt", "a") as f:
                import datetime
                f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] To: {to} | OTP: {otp} | Subject: {subject}\n")
        except Exception as e:
            current_app.logger.error(f"Failed to write to dev_emails.txt: {e}")
        return True
        
    msg = Message(
        subject,
        sender=("Be Your Platform", sender),
        recipients=[to]
    )
    
    # Try to render HTML body
    try:
        msg.html = render_template(f"email/{template}.html", **kwargs)
    except Exception as e:
        current_app.logger.error(f"Failed to render email template {template}: {e}")
        return False
    
    app = current_app._get_current_object()
    thread = Thread(target=send_async_email, args=(app, msg))
    thread.start()
    return True
