from flask import Flask, render_template, jsonify
from collectors import collect_devices, get_network_status
from database import init_db, save_devices, get_history
from alerts import generate_alerts

app = Flask(__name__)

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/devices")
def api_devices():
    devices = collect_devices()
    save_devices(devices)
    return jsonify(devices)

@app.route("/api/status")
def api_status():
    return jsonify(get_network_status())

@app.route("/api/alerts")
def api_alerts():
    return jsonify(generate_alerts())

@app.route("/api/history")
def api_history():
    return jsonify(get_history())

if __name__ == "__main__":
    print("Hostel Network Monitor")
    print("Open http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
