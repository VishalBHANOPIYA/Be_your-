from app.models.notification import Notification
from app.extensions import db

def send_notification(user_id, message):
    """Create a notification for a user."""
    notif = Notification(user_id=user_id, message=message)
    db.session.add(notif)
    db.session.commit()
    return notif
