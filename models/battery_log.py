from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class BatteryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(128), nullable=False)
    level = db.Column(db.Float, nullable=False)
    charging = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)