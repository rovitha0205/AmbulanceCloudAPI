from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)


@app.route("/")
def home():
    return "Ambulance Cloud API Connected"

@app.route("/monitor")
def monitor():
    return render_template("monitor.html")

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



from datetime import date, datetime


# ---------------------------------------------------
# Spark Analytics API
# ---------------------------------------------------

def get_latest_spark_run_id():

    query = """
    SELECT run_id
    FROM spark_risk_results
    ORDER BY id DESC
    LIMIT 1
    """

    row = db.session.execute(db.text(query)).fetchone()

    if row is None:
        return None

    return row.run_id


def serialize_spark_rows(rows):

    result = []

    for row in rows:
        record = dict(row._mapping)

        # Convert timestamps into clean ISO format
        for key, value in record.items():
            if isinstance(value, (datetime, date)):
                record[key] = value.isoformat()

        result.append(record)

    return result


def get_spark_table_data(table_name, run_id):

    # Only allow the four known Spark tables
    allowed_tables = {
        "spark_risk_results",
        "spark_combined_summary",
        "spark_hourly_trend",
        "spark_dashboard_summary"
    }

    if table_name not in allowed_tables:
        raise ValueError("Invalid Spark table")

    order_clause = ""

    if table_name == "spark_risk_results":
        order_clause = "ORDER BY id ASC"

    elif table_name == "spark_hourly_trend":
        order_clause = 'ORDER BY "time" ASC'

    query = f"""
    SELECT *
    FROM {table_name}
    WHERE run_id = :run_id
    {order_clause}
    """

    rows = db.session.execute(
        db.text(query),
        {"run_id": run_id}
    ).fetchall()

    return serialize_spark_rows(rows)


def spark_api_response(table_name):

    run_id = get_latest_spark_run_id()

    if run_id is None:
        return jsonify({
            "status": "success",
            "message": "No Spark results available",
            "run_id": None,
            "data": []
        })

    data = get_spark_table_data(table_name, run_id)

    return jsonify({
        "status": "success",
        "run_id": run_id,
        "data": data
    })


# ---------------------------------------------------
# Individual Spark API Endpoints
# ---------------------------------------------------

@app.route("/api/spark/risk-results", methods=["GET"])
def spark_risk_results():

    return spark_api_response("spark_risk_results")


@app.route("/api/spark/combined-summary", methods=["GET"])
def spark_combined_summary():

    return spark_api_response("spark_combined_summary")


@app.route("/api/spark/hourly-trend", methods=["GET"])
def spark_hourly_trend():

    return spark_api_response("spark_hourly_trend")


@app.route("/api/spark/dashboard-summary", methods=["GET"])
def spark_dashboard_summary():

    return spark_api_response("spark_dashboard_summary")


# ---------------------------------------------------
# Combined Spark API Endpoint
# ---------------------------------------------------

@app.route("/api/spark/latest", methods=["GET"])
def spark_latest():

    run_id = get_latest_spark_run_id()

    if run_id is None:
        return jsonify({
            "status": "success",
            "message": "No Spark results available",
            "run_id": None,
            "risk_results": [],
            "combined_summary": [],
            "hourly_trend": [],
            "dashboard_summary": []
        })

    return jsonify({
        "status": "success",
        "run_id": run_id,

        "risk_results": get_spark_table_data(
            "spark_risk_results", run_id
        ),

        "combined_summary": get_spark_table_data(
            "spark_combined_summary", run_id
        ),

        "hourly_trend": get_spark_table_data(
            "spark_hourly_trend", run_id
        ),

        "dashboard_summary": get_spark_table_data(
            "spark_dashboard_summary", run_id
        )
    })


if __name__ == "__main__":
    app.run(debug=True)