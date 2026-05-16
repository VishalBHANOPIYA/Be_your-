from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db

class AdminLog(db.Model):
    __tablename__ = 'admin_logs'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(255))
    target_type = db.Column(db.String(50)) # 'user', 'job', 'recruiter'
    target_id = db.Column(UUID(as_uuid=True))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
