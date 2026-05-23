from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recruiter_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    website = db.Column(db.String(255))
    logo_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean, default=False)
    
    jobs = db.relationship('Job', backref='company', lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
