#Initilize the database for the Flask app
from app import app, db

with app.app_context():
    db.create_all()
    print("✅ Database initialized")
    