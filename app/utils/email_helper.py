from flask import url_for
from app.utils.email import send_email

def send_reset_email(user_email, token):
    """
    Sends a password reset email to the user.
    """
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    return send_email(
        to=user_email,
        subject="Password Reset Request | Be Your",
        template="password_reset",
        reset_url=reset_url
    )
