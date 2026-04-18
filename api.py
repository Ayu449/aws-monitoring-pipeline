from flask import Flask, jsonify
import mysql.connector
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

DB_READ_HOST = "monitoring-db-replica.cnmuomi6yetg.ap-south-1.rds.amazonaws.com"
DB_USER = "admin"
DB_PASS = "Monitor12345"
DB_NAME = "monitoring"

@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    conn = mysql.connector.connect(host=DB_READ_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
    cursor = conn.cursor()
    one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
    cursor.execute("""
        SELECT timestamp, ram, cpu, disk, load_1m, server_ip
        FROM metrics
        WHERE timestamp >= %s AND server_ip IS NOT NULL
        ORDER BY timestamp ASC
    """, (one_minute_ago,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    result = {}
    for row in rows:
        ip = row[5]
        if ip not in result:
            result[ip] = []
        result[ip].append({
            "timestamp": str(row[0]),
            "ram": row[1],
            "cpu": row[2],
            "disk": row[3],
            "load_1m": row[4]
        })

    return jsonify(result)

app.run(host="0.0.0.0", port=5000)
