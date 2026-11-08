function safe(value) {
  return String(value ?? "").replace(/[&<>"']/g, character => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[character]));
}

async function getJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Request failed: ${url} (${response.status})`);
  return response.json();
}

async function refreshDashboard() {
  const button = document.getElementById("refresh-button");
  button.disabled = true;
  button.textContent = "Refreshing…";
  try {
    const [devices, status, alerts] = await Promise.all([
      getJSON("/api/devices"), getJSON("/api/status"), getJSON("/api/alerts")
    ]);

    document.getElementById("device-count").textContent = devices.length;
    document.getElementById("local-ip").textContent = status.local_ip || "Unavailable";
    document.getElementById("gateway").textContent = status.gateway || "Unavailable";
    document.getElementById("hostname").textContent = status.hostname || "Unavailable";

    const table = document.getElementById("device-table");
    if (!devices.length) {
      table.innerHTML = '<tr><td colspan="5">No ARP devices found yet. Try using your network, then refresh.</td></tr>';
    } else {
      table.innerHTML = devices.map(device => `<tr>
        <td>${safe(device.ip)}</td><td>${safe(device.mac)}</td><td>${safe(device.type)}</td>
        <td>${safe(device.hostname)}</td><td>${safe(device.status)}</td>
      </tr>`).join("");
    }

    const alertBox = document.getElementById("alerts-list");
    alertBox.innerHTML = alerts.map(alert => `<div class="alert">
      <strong>${safe(alert.title)} · ${safe(alert.timestamp)}</strong>
      <p>${safe(alert.message)}</p>
    </div>`).join("") || "No alerts.";
  } catch (error) {
    document.getElementById("device-table").innerHTML =
      `<tr><td colspan="5">Could not load data: ${safe(error.message)}</td></tr>`;
  } finally {
    button.disabled = false;
    button.textContent = "Refresh";
  }
}

refreshDashboard();
setInterval(refreshDashboard, 10000);
