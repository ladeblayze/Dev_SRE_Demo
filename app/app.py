from flask import Flask, jsonify, request
import os
import random
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)

REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
ERRORS = Counter('demo_errors_total', 'Total simulated errors')
LATENCY = Histogram('http_request_duration_seconds', 'Latency', buckets=(0.01,0.05,0.1,0.2,0.5,1,2,5))

@app.route('/')
def hello():
    start = time.time()
    # 10% error to simulate incidents
    if random.random() < 0.10:
        ERRORS.inc()
        REQUESTS.labels('GET','/', '500').inc()
        return jsonify({'ok': False, 'error': 'simulated'}), 500
    time.sleep(random.uniform(0.01, 0.2))  # simulate work
    REQUESTS.labels('GET','/', '200').inc()
    LATENCY.observe(time.time() - start)
    return jsonify({'ok': True, 'message': 'Hello from demo app!'})

@app.route('/healthz')
def healthz():
    return 'ok', 200

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8080'))
    app.run(host='0.0.0.0', port=port)
