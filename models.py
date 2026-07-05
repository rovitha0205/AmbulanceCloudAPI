from database import db

class LatestSensor(db.Model):

    __tablename__ = "latest_sensor"

    ambulance_id = db.Column(db.String, primary_key=True)

    heart_rate = db.Column(db.Integer)

    spo2 = db.Column(db.Integer)

    temperature = db.Column(db.Float)

    systolic = db.Column(db.Integer)

    diastolic = db.Column(db.Integer)

    respiration = db.Column(db.Integer)

    ecg = db.Column(db.Integer)