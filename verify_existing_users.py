from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app('development')

with app.app_context():
    try:
        users = User.query.filter_by(is_verified=False).all()
        count = 0
        for user in users:
            user.is_verified = True
            count += 1
        
        db.session.commit()
        print(f"✅ Successfully marked {count} existing users as verified.")
    except Exception as e:
        print(f"❌ Error updating users: {e}")
        print("Please make sure you have run 'flask db upgrade' first so the 'otp' columns exist.")
