from telegram_bot_panel import *
from telethon import events, Button
import subprocess
import re

SSH_PORT = "22"  # ganti kalau pakai port custom

def get_ssh_connections():
    try:
        result = subprocess.check_output(["ss", "-tnp"], stderr=subprocess.DEVNULL).decode()
    except Exception:
        return []

    lines = result.splitlines()
    connections = []
    seen = set()

    for line in lines:
        if "ESTAB" not in line or f":{SSH_PORT}" not in line:
            continue
        match = re.search(r"(\d+\.\d+\.\d+\.\d+):(\d+)\s+.*pid=(\d+),.*\"(.*?)\"", line)
        if match:
            ip, port, pid, process = match.groups()
            if ("sshd" in process or "dropbear" in process) and (ip, pid) not in seen:
                # Temukan user via /proc/<pid>/status
                try:
                    username = subprocess.check_output(["ps", "-o", "user=", "-p", pid]).decode().strip()
                except:
                    username = "unknown"
                connections.append((username, ip, port, pid))
                seen.add((ip, pid))

    return connections

@bot.on(events.CallbackQuery(data=b"trojan/login_ssh"))
async def login_ssh(event):
    sender = await event.get_sender()
    if valid(str(sender.id)) != "true":
        await event.answer("Akses ditolak!", alert=True)
        return

    conn = get_ssh_connections()
    if not conn:
        await bot.send_message(event.chat_id, "🔒 Tidak ada user SSH yang aktif saat ini.", buttons=[Button.inline("🔙 Back to Menu", b"menu")])
        return

    msg = "🔐 **Status Login SSH Aktif:**\n\n"
    msg += "`No  Nama         IP             Port  PID`\n"
    msg += "─────────────────────────────────────────────\n"
    for i, (name, ip, port, pid) in enumerate(conn, 1):
        msg += f"`{i:02d}. {name:<12} {ip:<14} {port:<5} {pid}`\n"

    await bot.send_message(
        event.chat_id,
        msg,
        parse_mode="markdown",
        buttons=[Button.inline("🔙 Back to Menu", b"menu")]
    )

