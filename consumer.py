import json
import mysql.connector
from datetime import datetime, timezone
from kafka import KafkaConsumer

KAFKA_BROKER = "10.0.1.143:9092"
TOPIC = "server-metrics"

DB_WRITE_HOST = "monitoring-db.cnmuomi6yetg.ap-south-1.rds.amazonaws.com"
DB_USER = "admin"
DB_PASS = "Monitor12345"
DB_NAME = "monitoring"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='latest',
    group_id='monitoring-group'
)

print("Consumer started. Waiting for messages...")

for message in consumer:
    data = message.value
    print(f"Received: {data}")

    conn = mysql.connector.connect(
        host=DB_WRITE_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO metrics (timestamp, ram, cpu, disk, load_1m, load_5m, load_15m, server_ip) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (
            datetime.now(timezone.utc),
            data['ram'],
            data['cpu'],
            data['disk'],
            data['load_1m'],
            data['load_5m'],
            data['load_15m'],
            data['server_ip']
        )
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Saved to DB: server={data['server_ip']} ram={data['ram']}")
