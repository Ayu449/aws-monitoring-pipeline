from flask import Flask, render_template_string
import requests

app = Flask(__name__)

API_URL = "http://10.0.1.102:5000/api/metrics"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Server Monitoring</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial; background: #1a1a2e; color: white; padding: 20px; }
        h1 { text-align: center; color: #00d4ff; }
        .server-block { background: #16213e; border-radius: 10px; padding: 20px; margin: 20px 0; }
        .server-title { font-size: 20px; color: #00d4ff; margin-bottom: 15px; }
        .charts-row { display: flex; gap: 20px; }
        .chart-box { flex: 1; background: #0f3460; border-radius: 8px; padding: 10px; }
        canvas { max-height: 200px; }
    </style>
</head>
<body>
    <h1>Live Server Monitoring</h1>
    <div id="dashboard"></div>

<script>
const charts = {};

async function fetchAndUpdate() {
    const res = await fetch('/api/metrics');
    const data = await res.json();

    const dashboard = document.getElementById('dashboard');

    for (const [ip, points] of Object.entries(data)) {
        const timestamps = points.map(p => p.timestamp.split(' ')[1].substring(0,8));
        const ramValues = points.map(p => p.ram);
        const cpuValues = points.map(p => p.cpu);
        const diskValues = points.map(p => p.disk);

        if (!charts[ip]) {
            const block = document.createElement('div');
            block.className = 'server-block';
            block.id = 'block-' + ip.replace(/\./g, '-');
            block.innerHTML = `
                <div class="server-title">Server: ${ip}</div>
                <div class="charts-row">
                    <div class="chart-box"><canvas id="ram-${ip.replace(/\./g,'-')}"></canvas></div>
                    <div class="chart-box"><canvas id="cpu-${ip.replace(/\./g,'-')}"></canvas></div>
                    <div class="chart-box"><canvas id="disk-${ip.replace(/\./g,'-')}"></canvas></div>
                </div>`;
            dashboard.appendChild(block);

            charts[ip] = {
                ram: new Chart(document.getElementById('ram-' + ip.replace(/\./g,'-')), {
                    type: 'line',
                    data: { labels: timestamps, datasets: [{ label: 'RAM (MB)', data: ramValues, borderColor: '#00d4ff', tension: 0.3, fill: false }] },
                    options: { animation: false, plugins: { legend: { labels: { color: 'white' } } }, scales: { x: { ticks: { color: 'white' } }, y: { ticks: { color: 'white' } } } }
                }),
                cpu: new Chart(document.getElementById('cpu-' + ip.replace(/\./g,'-')), {
                    type: 'line',
                    data: { labels: timestamps, datasets: [{ label: 'CPU %', data: cpuValues, borderColor: '#ff6b6b', tension: 0.3, fill: false }] },
                    options: { animation: false, plugins: { legend: { labels: { color: 'white' } } }, scales: { x: { ticks: { color: 'white' } }, y: { ticks: { color: 'white' } } } }
                }),
                disk: new Chart(document.getElementById('disk-' + ip.replace(/\./g,'-')), {
                    type: 'line',
                    data: { labels: timestamps, datasets: [{ label: 'Disk %', data: diskValues, borderColor: '#ffd93d', tension: 0.3, fill: false }] },
                    options: { animation: false, plugins: { legend: { labels: { color: 'white' } } }, scales: { x: { ticks: { color: 'white' } }, y: { ticks: { color: 'white' } } } }
                })
            };
        } else {
            charts[ip].ram.data.labels = timestamps;
            charts[ip].ram.data.datasets[0].data = ramValues;
            charts[ip].ram.update();
            charts[ip].cpu.data.labels = timestamps;
            charts[ip].cpu.data.datasets[0].data = cpuValues;
            charts[ip].cpu.update();
            charts[ip].disk.data.labels = timestamps;
            charts[ip].disk.data.datasets[0].data = diskValues;
            charts[ip].disk.update();
        }
    }
}

fetchAndUpdate();
setInterval(fetchAndUpdate, 5000);
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/metrics')
def metrics():
    response = requests.get(API_URL)
    return response.json()

app.run(host="0.0.0.0", port=8080)
