from flask import url_for, current_app
from flask_mail import Message
from app.extensions import mail

def send_reset_email(user_email, token):
    """
    Sends a password reset email to the user.
    """
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    msg = Message(
        "Password Reset Request | Be Your",
        sender=current_app.config.get('MAIL_USERNAME'),
        recipients=[user_email]
    )
    
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email and no changes will be made.
This link will expire in 30 minutes.
'''
    
    msg.html = f'''
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
        <h2 style="color: #6366f1; text-align: center;">Reset Your Password</h2>
        <p>Hello,</p>
        <p>We received a request to reset your password for your <b>Be Your</b> account. Click the button below to proceed:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background: #6366f1; color: white; padding: 15px 25px; text-decoration: none; border-radius: 8px; font-weight: bold;">Reset Password</a>
        </div>
        <p>If the button doesn't work, copy and paste this link into your browser:</p>
        <p style="color: #6366f1; font-size: 12px;">{reset_url}</p>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="font-size: 12px; color: #999;">If you didn't request this, you can safely ignore this email.</p>
    </div>
    '''
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
