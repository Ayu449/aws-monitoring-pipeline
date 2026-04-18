# AWS Real-Time Server Monitoring Pipeline

A production-style distributed monitoring system built on AWS that collects, processes, and visualizes server metrics in real-time.

## Architecture
Prod Servers (x3) → Kafka Broker → Consumer → RDS MySQL → Flask API → Live Dashboard

## AWS Infrastructure
- 3 Prod Servers (EC2) - servers being monitored
- 1 Kafka Broker (EC2) - message queue in KRaft mode
- 1 Backend Server (EC2) - runs Kafka consumer and Flask API
- 1 Frontend Server (EC2) - serves the live dashboard
- RDS MySQL with Primary + Read Replica

## Files
- producer.py - collects CPU, RAM, Disk, Load and sends to Kafka (runs on each Prod Server)
- consumer.py - reads from Kafka and writes to RDS (runs on Backend Server)
- api.py - Flask API that reads from RDS Read Replica (runs on Backend Server)
- app.py - live dashboard with Chart.js graphs (runs on Frontend Server)

## Tech Stack
Python, Flask, Apache Kafka 3.7.0 (KRaft mode), MySQL, Chart.js, AWS EC2, AWS RDS