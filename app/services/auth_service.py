from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from app.models.user import User, Profile
from app.extensions import db
from flask_login import login_user, logout_user
from app.utils.validators import validate_email, validate_password, validate_name

class AuthService:
    @staticmethod
    def register_user(name, email, password, role='seeker'):
        # Apply validators
        ok, err = validate_name(name)
        if not ok: return None, err
        
        ok, err = validate_email(email)
        if not ok: return None, err
        
        ok, err = validate_password(password)
        if not ok: return None, err

        if User.query.filter_by(email=email).first():
            return None, "Email already registered"
            
        user = User(name=name, email=email, role=role, is_verified=False)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        profile = Profile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()
        
        AuthService.generate_and_send_otp(user)
        
        return user, None

    @staticmethod
    def login_user(email, password, remember=False):
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_active:
                return False, "Account is deactivated"
            if not user.is_verified:
                return False, "unverified"
            login_user(user, remember=remember)
            return True, None
        return False, "Invalid email or password"

    @staticmethod
    def generate_and_send_otp(user):
        import random
        from datetime import datetime, timedelta
        from app.utils.email import send_email
        
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()
        
        send_email(
            to=user.email,
            subject="Verify your Be Your account",
            template='otp_verification',
            name=user.name,
            otp=otp
        )
        return True

    @staticmethod
    def verify_otp(email, otp_code):
        from datetime import datetime
        user = User.query.filter_by(email=email).first()
        if not user:
            return False, "User not found"
        
        if user.is_verified:
            return True, None
            
        if user.otp != otp_code:
            return False, "Invalid OTP code"
            
        if not user.otp_expiry or user.otp_expiry < datetime.utcnow():
            return False, "OTP has expired"
            
        # OTP is valid
        user.is_verified = True
        user.otp = None
        user.otp_expiry = None
        db.session.commit()
        return True, None

    @staticmethod
    def logout_user():
        logout_user()

    @staticmethod
    def get_reset_token(email):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps(email, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            email = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
        except:
            return None
        return User.query.filter_by(email=email).first()

    @staticmethod
    def update_password(user, new_password):
        user.set_password(new_password)
        db.session.commit()
        return True

    @staticmethod
    def handle_oauth_user(email, name, provider='google'):
        user = User.query.filter_by(email=email).first()
        if not user:
            # Create new user
            user = User(name=name, email=email, role='seeker', oauth_provider=provider, is_verified=True)
            db.session.add(user)
            db.session.flush()
            profile = Profile(user_id=user.id)
            db.session.add(profile)
            db.session.commit()
        else:
            # Link to OAuth if not already linked
            if not user.oauth_provider:
                user.oauth_provider = provider
                db.session.commit()
        
        login_user(user)
        return user
