from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
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
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
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
