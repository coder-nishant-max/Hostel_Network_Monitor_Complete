import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "data" / "network_monitor.db"

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS device_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                ip TEXT NOT NULL,
                mac TEXT NOT NULL,
                hostname TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)

def save_devices(devices):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        for device in devices:
            conn.execute("""
                INSERT INTO device_history (timestamp, ip, mac, hostname, status)
                VALUES (?, ?, ?, ?, ?)
            """, (now, device.get("ip", ""), device.get("mac", ""),
                  device.get("hostname", "Unknown"), device.get("status", "Detected")))

def get_history(limit=100):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT timestamp, ip, mac, hostname, status
            FROM device_history ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
    return [dict(row) for row in rows]
