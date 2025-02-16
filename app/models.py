from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from app import db
from flask_bcrypt import generate_password_hash, check_password_hash

# User Model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    triggers = db.relationship('Trigger', backref='user', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check if the provided password matches the hashed password."""
        return check_password_hash(self.password, password)

# Trigger Model
class Trigger(db.Model):
    __tablename__ = 'triggers'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # "scheduled" or "api"
    schedule_time = db.Column(db.DateTime, nullable=True)  # For scheduled triggers
    interval = db.Column(db.Integer, nullable=True)  # Interval in minutes for recurring
    recurrence = db.Column(db.Boolean, nullable=True)  # Cron-like for recurring triggers
    api_endpoint = db.Column(db.Text, nullable=True)  # For API triggers
    api_payload = db.Column(db.JSON, nullable=True)  # For API triggers payload
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=True)

# Event Log Model
class EventLog(db.Model):
    __tablename__ = 'event_logs'
    id = db.Column(db.Integer, primary_key=True)
    trigger_id = db.Column(db.Integer, db.ForeignKey('triggers.id'), nullable=False)
    response = db.Column(db.JSON, nullable=True)
    status = db.Column(db.String(50), default="active")  # active, archived, deleted
    trigger = db.relationship('Trigger', backref='logs')
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    archived_at = db.Column(db.DateTime, nullable=True)
