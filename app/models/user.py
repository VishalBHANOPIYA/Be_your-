from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.Enum('seeker', 'recruiter', 'admin', name='user_roles'), default='seeker')
    avatar_url = db.Column(db.String(500))
    oauth_provider = db.Column(db.String(50))
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
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

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    headline = db.Column(db.String(255))
    bio = db.Column(db.Text)
    skills = db.Column(JSONB) # ["Python", "Flask"]
    experience = db.Column(JSONB) # [{company, role, years}]
    education = db.Column(JSONB) # [{college, degree, year}]
    location = db.Column(db.String(120))
    github_url = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))
    resume_path = db.Column(db.String(500))
    resume_text = db.Column(db.Text)
    resume_score = db.Column(db.Float)
    visibility = db.Column(db.Boolean, default=True)
