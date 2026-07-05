from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)


@app.route("/")
def home():
    return "Ambulance Cloud API Connected"


# ---------------------------------------------------
# Sensor Upload (Replacement for upload.php)
# ---------------------------------------------------
@app.route("/upload.php")
def upload():

    heartbeat = request.args.get("data1", type=int)
    spo2 = request.args.get("data2", type=int)
    temperature = request.args.get("data3", type=float)
    respiration = request.args.get("data4", type=int)

    query = """
    INSERT INTO sensor_table
    (heartbeat, temperature, spo2, respiration)
    VALUES
    (:heartbeat, :temperature, :spo2, :respiration)
    """

    db.session.execute(
        db.text(query),
        {
            "heartbeat": heartbeat,
            "temperature": temperature,
            "spo2": spo2,
            "respiration": respiration
        }
    )

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Sensor Data Stored"
    })


# ---------------------------------------------------
# ECG Upload (Replacement for ECG.php)
# ---------------------------------------------------
@app.route("/ECG.php")
def ecg():

    ecg = request.args.get("ecg", type=int)

    query = """
    INSERT INTO ecg_table
    (ecg)
    VALUES
    (:ecg)
    """

    db.session.execute(
        db.text(query),
        {
            "ecg": ecg
        }
    )

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "ECG Stored"
    })


# ---------------------------------------------------
# Latest Sensor
# ---------------------------------------------------
@app.route("/latest")
def latest():

    query = """
    SELECT *
    FROM sensor_table
    ORDER BY id DESC
    LIMIT 1
    """

    row = db.session.execute(db.text(query)).fetchone()

    if row is None:
        return jsonify({})

    return jsonify({
        "heartbeat": row.heartbeat,
        "temperature": row.temperature,
        "spo2": row.spo2,
        "respiration": row.respiration,
        "server_time": str(row.created_at)
    })


# ---------------------------------------------------
# Latest ECG
# ---------------------------------------------------
@app.route("/latest_ecg")
def latest_ecg():

    query = """
    SELECT *
    FROM ecg_table
    ORDER BY id DESC
    LIMIT 1
    """

    row = db.session.execute(db.text(query)).fetchone()

    if row is None:
        return jsonify({})

    return jsonify({
        "ecg": row.ecg,
        "server_time": str(row.created_at)
    })


# ---------------------------------------------------
# Last 10 ECG Values (for waveform)
# ---------------------------------------------------
@app.route("/ecg_history")
def ecg_history():

    query = """
    SELECT ecg
    FROM ecg_table
    ORDER BY id DESC
    LIMIT 10
    """

    rows = db.session.execute(db.text(query)).fetchall()

    values = [row.ecg for row in reversed(rows)]

    return jsonify({
        "ecg": values
    })


if __name__ == "__main__":
    app.run(debug=True)