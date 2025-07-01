from telegram_bot_panel import *
from telethon import events, Button
import subprocess
import pwd
import os
import re

SSH_PORT = "22"

def get_username_from_pid(pid):
    try:
        uid = os.stat(f"/proc/{pid}").st_uid
        return pwd.getpwuid(uid).pw_name
    except:
        return "unknown"

def get_ssh_connections():
    try:
        output = subprocess.check_output(["ss", "-tnp"]).decode()
    except Exception as e:
        print(f"[ERROR] ss command failed: {e}")
        return []

    connections = []
    seen = set()
    for line in output.splitlines():
        if f":{SSH_PORT}" not in line or "ESTAB" not in line:
            continue

        match = re.search(r"(\d+\.\d+\.\d+\.\d+):(\d+)\s+.*pid=(\d+),.*\"(.*?)\"", line)
        if match:
            ip, port, pid, proc = match.groups()
            if ("sshd" in proc or "dropbear" in proc) and (ip, pid) not in seen:
                username = get_username_from_pid(int(pid))
                connections.append((username, ip, port, pid))
                seen.add((ip, pid))
    return connections

@bot.on(events.CallbackQuery(data=b"trojan/login_ssh"))
async def login_ssh(event):
    try:
        sender = await event.get_sender()
        if valid(str(sender.id)) != "true":
            await event.answer("Akses ditolak!", alert=True)
            return

        conn = get_ssh_connections()
        if not conn:
            await bot.send_message(
                event.chat_id,
                "🔒 Tidak ada user SSH yang aktif.",
                buttons=[Button.inline("🔙 Back to Menu", b"menu")]
            )
            return

        msg = "🔐 **Login SSH Aktif:**\n\n"
        msg += "`No  Nama         IP             Port  PID`\n"
        msg += "────────────────────────────────────────────\n"

        for i, (name, ip, port, pid) in enumerate(conn, 1):
            msg += f"`{i:02d}. {name:<12} {ip:<14} {port:<5} {pid}`\n"

        await bot.send_message(
            event.chat_id,
            msg,
            parse_mode="markdown",
            buttons=[Button.inline("🔙 Back to Menu", b"menu")]
        )

    except Exception as e:
        await bot.send_message(event.chat_id, f"❌ Error: {e}")
        print(f"[LOGIN SSH ERROR] {e}")

