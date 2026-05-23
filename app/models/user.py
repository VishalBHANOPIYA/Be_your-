from datetime import datetime
import uuid
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import login_manager

# Use JSONB for Postgres, JSON for others (like SQLite in tests)
CompatibleJSON = JSON().with_variant(JSONB(), 'postgresql')

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(uuid.UUID(user_id))
    except (ValueError, TypeError):
        return None

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    # Use db.String(36) as a fallback for UUID if on SQLite, 
    # but SQLAlchemy's UUID type from postgresql usually works if treated as a type.
    # However, to be safe for tests, we can use a more generic approach.
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.Enum('seeker', 'recruiter', 'admin', name='user_roles'), default='seeker')
    avatar_url = db.Column(db.String(500))
    oauth_provider = db.Column(db.String(50))
    is_verified = db.Column(db.Boolean, default=False)
    otp = db.Column(db.String(6))
    otp_expiry = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Gamification and Streaks
    streak_count = db.Column(db.Integer, default=0)
    last_sprint_date = db.Column(db.Date)
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to Profile
    profile = db.relationship('Profile', backref='user', uselist=False, cascade="all, delete-orphan")
    # Relationship to Company (if recruiter)
    company = db.relationship('Company', backref='recruiter', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    headline = db.Column(db.String(255))
    bio = db.Column(db.Text)
    skills = db.Column(CompatibleJSON) # ["Python", "Flask"]
    experience = db.Column(CompatibleJSON) # [{company, role, years}]
    education = db.Column(CompatibleJSON) # [{college, degree, year}]
    location = db.Column(db.String(120))
    github_url = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))
    resume_path = db.Column(db.String(500))
    resume_text = db.Column(db.Text)
    resume_score = db.Column(db.Float)
    badges = db.Column(CompatibleJSON, default=[]) # [{"name": "Python Expert", "level": "Gold", "earned_at": "..."}]
    visibility = db.Column(db.Boolean, default=True)
    
    # Portfolio Customization
    portfolio_theme = db.Column(db.String(50), default='zinc_indigo')
    portfolio_projects = db.Column(CompatibleJSON, default=[])
    portfolio_socials = db.Column(CompatibleJSON, default={})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
