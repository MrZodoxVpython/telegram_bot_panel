from telegram_bot_panel import *
from telethon import events, Button
import subprocess
import os
import pwd
import re

SSH_PORT = "22"  # ubah jika pakai port SSH custom

def get_username_from_pid(pid):
    try:
        stat_info = os.stat(f"/proc/{pid}")
        uid = stat_info.st_uid
        return pwd.getpwuid(uid).pw_name
    except:
        return "unknown"

def get_ssh_connections():
    try:
        output = subprocess.check_output(["ss", "-tnp"], stderr=subprocess.DEVNULL).decode()
    except Exception:
        return []

    lines = output.splitlines()
    results = []
    seen = set()

    for line in lines:
        if f":{SSH_PORT}" not in line or "ESTAB" not in line:
            continue

        match = re.search(r"(\d+\.\d+\.\d+\.\d+):(\d+)\s+.*pid=(\d+),.*\"(.*?)\"", line)
        if match:
            ip, port, pid, process = match.groups()
            if ("sshd" in process or "dropbear" in process) and (ip, pid) not in seen:
                username = get_username_from_pid(int(pid))
                results.append((username, ip, port, pid))
                seen.add((ip, pid))
    return results

@bot.on(events.CallbackQuery(data=b"trojan/login_ssh"))
async def login_ssh(event):
    sender = await event.get_sender()
    if valid(str(sender.id)) != "true":
        await event.answer("Akses ditolak!", alert=True)
        return

    connections = get_ssh_connections()
    if not connections:
        await bot.send_message(
            event.chat_id,
            "🔒 Tidak ada user SSH yang aktif.",
            buttons=[Button.inline("🔙 Back to Menu", b"menu")]
        )
        return

    msg = "🔐 **Login SSH Aktif:**\n\n"
    msg += "`No  Nama         IP             Port  PID`\n"
    msg += "─────────────────────────────────────────────\n"
    for i, (user, ip, port, pid) in enumerate(connections, 1):
        msg += f"`{i:02d}. {user:<12} {ip:<14} {port:<5} {pid}`\n"

    await bot.send_message(
        event.chat_id,
        msg,
        parse_mode="markdown",
        buttons=[Button.inline("🔙 Back to Menu", b"menu")]
    )

