from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app, session
from app.services.auth_service import AuthService
from app.utils.email_helper import send_reset_email
from app.extensions import oauth, limiter
from flask_login import login_required, logout_user, current_user

auth_bp = Blueprint('auth', __name__)

def get_redirect_target(user):
    if user.role == 'admin':
        return url_for('admin.dashboard')
    elif user.role == 'recruiter':
        return url_for('recruiter.dashboard')
    else:
        return url_for('user.dashboard')

@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per hour", methods=["POST"])
def register():
    if current_user.is_authenticated:
        return redirect(get_redirect_target(current_user))
    if request.method == 'POST':
        data = request.form
        user, error = AuthService.register_user(
            data.get('name'), data.get('email'),
            data.get('password'), data.get('role', 'seeker')
        )
        if error:
            flash(error, 'danger')
            return render_template('auth/register.html')
        session['verify_email'] = data.get('email')
        flash('Registration successful! Please check your email for the verification code.', 'success')
        return redirect(url_for('auth.verify_otp'))
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(get_redirect_target(current_user))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        success, error = AuthService.login_user(email, password, remember)
        if success:
            from app.models.user import User
            user = User.query.filter_by(email=email).first()
            return redirect(get_redirect_target(user))
        
        if error == "unverified":
            session['verify_email'] = email
            from app.models.user import User
            user = User.query.filter_by(email=email).first()
            if user:
                AuthService.generate_and_send_otp(user)
            flash('Your account is not verified. A new verification code has been sent to your email.', 'warning')
            return redirect(url_for('auth.verify_otp'))
            
        flash(error, 'danger')
        
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    AuthService.logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("5 per hour", methods=["POST"])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        from app.models.user import User
        user = User.query.filter_by(email=email).first()
        if user:
            token = AuthService.get_reset_token(email)
            if send_reset_email(email, token):
                flash('An email has been sent with instructions to reset your password.', 'info')
            else:
                flash('Error sending email. Please try again later.', 'danger')
        else:
            flash('No account found with that email address.', 'warning')
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = AuthService.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html')
            
        AuthService.update_password(user, new_password)
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html')

@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = session.get('verify_email')
    if not email:
        flash('Session expired or invalid. Please log in again.', 'warning')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        otp_code = request.form.get('otp')
        success, error = AuthService.verify_otp(email, otp_code)
        if success:
            flash('Your account has been verified! You can now log in.', 'success')
            session.pop('verify_email', None)
            return redirect(url_for('auth.login'))
        else:
            flash(error, 'danger')
            
    return render_template('auth/verify_otp.html', email=email)

@auth_bp.route('/resend-otp', methods=['POST'])
@limiter.limit("3 per 10 minutes")
def resend_otp():
    email = session.get('verify_email')
    if not email:
        return redirect(url_for('auth.login'))
        
    from app.models.user import User
    user = User.query.filter_by(email=email).first()
    if user and not user.is_verified:
        AuthService.generate_and_send_otp(user)
        flash('A new verification code has been sent to your email.', 'success')
    else:
        flash('Account already verified or not found.', 'warning')
        
    return redirect(url_for('auth.verify_otp'))

# Google OAuth2 Routes
@auth_bp.route('/login/google')
def google_login():
    redirect_uri = url_for('auth.google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/authorize/google')
def google_authorize():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    if user_info:
        user = AuthService.handle_oauth_user(user_info['email'], user_info['name'])
        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(get_redirect_target(user))
    
    flash('Google authentication failed.', 'danger')
    return redirect(url_for('auth.login'))
