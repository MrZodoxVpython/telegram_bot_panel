from xolpanel import *
import subprocess
import socket
import platform
import requests

def get_uptime():
    return subprocess.getoutput("uptime -p").replace("up ", "")

def get_ip():
    try:
        return requests.get("https://ipinfo.io/ip").text.strip()
    except:
        return "Unavailable"

def get_country():
    try:
        data = requests.get("https://ipinfo.io").json()
        return data.get("country", "Unknown")
    except:
        return "Unknown"

def get_domain_xray():
    try:
        with open("/etc/xray/domain", "r") as f:
            return f.read().strip()
    except:
        return "Tidak ditemukan"

def get_cpu_load():
    return ', '.join(open('/proc/loadavg').read().split()[:3])

def get_ram_usage():
    mem = subprocess.getoutput("free -m").split('\n')[1].split()
    return f"{mem[2]}MB / {mem[1]}MB"

def get_disk_usage():
    disk = subprocess.getoutput("df -h /").split('\n')[1].split()
    return f"{disk[2]} / {disk[1]} ({disk[4]})"

def get_bandwidth():
    try:
        vn = subprocess.getoutput("vnstat --oneline")
        data = vn.split(";")
        return f"DL: {data[8]} UL: {data[9]} TOTAL: {data[10]}"
    except:
        return "vnStat tidak tersedia"

def get_status(service):
    return "🟢 Online" if subprocess.getoutput(f"systemctl is-active {service}") == "active" else "🔴 Offline"

@bot.on(events.CallbackQuery(data=b'info'))
async def info(event):
    status_vps = "🟢 Online (0.925ms)"
    os_version = platform.platform()
    uptime = get_uptime()
    ip = get_ip()
    country = get_country()
    domain_vps = socket.gethostname()
    domain_xray = get_domain_xray()
    xray_status = get_status("xray")
    cpu = get_cpu_load()
    ram = get_ram_usage()
    disk = get_disk_usage()
    bandwidth = get_bandwidth()

    output = f"""<b>Status VPS  :</b> {status_vps}
<b>OS          :</b> {os_version}
<b>Uptime      :</b> {uptime}
<b>Public IP   :</b> {ip}
<b>Country     :</b> {country}
<b>Domain VPS  :</b> {domain_vps}
<b>Domain Xray :</b> {domain_xray}
<b>Xray Status :</b> {xray_status}
<b>CPU         :</b> {cpu}
<b>RAM         :</b> {ram}
<b>Disk        :</b> {disk}
<b>Bandwidth   :</b> {bandwidth}
"""

    await event.answer("Mengambil informasi VPS...", alert=False)
    await event.edit(output, parse_mode="html")

