import json
import subprocess
from kafka import KafkaProducer

KAFKA_BROKER = "10.0.1.143:9092"
TOPIC = "server-metrics"
SERVER_IP = "10.0.1.232"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def collect_metrics():
    ram = int(run_command("free -m | awk 'NR==2{print $3}'"))
    cpu = float(run_command("top -bn2 | grep 'Cpu(s)' | tail -1 | awk '{print $2}'"))
    disk = int(run_command("df / | awk 'NR==2{print $5}' | tr -d '%'"))
    load = run_command("cat /proc/loadavg").split()
    return {
        "server_ip": SERVER_IP,
        "ram": ram,
        "cpu": cpu,
        "disk": disk,
        "load_1m": float(load[0]),
        "load_5m": float(load[1]),
        "load_15m": float(load[2])
    }

metrics = collect_metrics()
producer.send(TOPIC, value=metrics)
producer.flush()
print(f"Sent: {metrics}")
