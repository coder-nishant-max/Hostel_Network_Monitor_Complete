import platform
import subprocess
import socket
import re

def _run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        return result.stdout
    except (subprocess.TimeoutExpired, OSError):
        return ""

def get_local_ip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except OSError:
        return "Unavailable"

def get_gateway():
    if platform.system().lower() == "windows":
        output = _run_command(["ipconfig"])
        for line in output.splitlines():
            if "Default Gateway" in line:
                parts = line.split(":", 1)
                if len(parts) == 2 and parts[1].strip():
                    candidate = parts[1].strip()
                    if re.match(r"^\d+\.\d+\.\d+\.\d+$", candidate):
                        return candidate
    else:
        output = _run_command(["ip", "route"])
        for line in output.splitlines():
            if line.startswith("default"):
                parts = line.split()
                if len(parts) > 1:
                    return parts[1]
    return "Unavailable"

def collect_devices():
    system = platform.system().lower()
    command = ["arp", "-a"] if system == "windows" else ["ip", "neigh"]
    output = _run_command(command)
    devices = []
    local_ip = get_local_ip()
    local_mac = ""

    for line in output.splitlines():
        if system == "windows":
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F-]{17})\s+(\w+)", line)
            if not match:
                continue
            ip, mac, kind = match.groups()
            mac = mac.replace("-", ":").lower()
        else:
            match = re.search(r"(\d+\.\d+\.\d+\.\d+).*lladdr\s+([0-9a-fA-F:]{17})", line)
            if not match:
                continue
            ip, mac = match.groups()
            mac = mac.lower()
            kind = "dynamic"

        if ip == local_ip:
            local_mac = mac

        devices.append({
            "ip": ip,
            "mac": mac,
            "type": kind,
            "hostname": "This device" if ip == local_ip else "Unknown device",
            "status": "Detected"
        })

    # Add this computer to the list if it was not present in the ARP cache.
    if local_ip != "Unavailable" and not any(d["ip"] == local_ip for d in devices):
        devices.insert(0, {
            "ip": local_ip,
            "mac": local_mac or "Not available in ARP cache",
            "type": "local",
            "hostname": "This device",
            "status": "This device"
        })

    # Remove duplicate IP records.
    unique = {}
    for device in devices:
        unique[device["ip"]] = device
    return list(unique.values())

def get_network_status():
    return {
        "local_ip": get_local_ip(),
        "gateway": get_gateway(),
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "status": "Monitoring active"
    }
