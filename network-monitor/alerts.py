from datetime import datetime

def generate_alerts():
    return [{
        "title": "Monitoring started",
        "message": "The dashboard is collecting visible ARP neighbor information from this computer's network.",
        "severity": "info",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }]
