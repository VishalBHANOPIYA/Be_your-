from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.extensions import db

class Roadmap(db.Model):
    __tablename__ = 'roadmaps'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    target_role = db.Column(db.String(120), nullable=False)
    current_skills = db.Column(JSONB) # ["Python", "Flask"]
    steps = db.Column(JSONB) # [{"title": "Learn React", "resources": [], "status": "todo"}]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
