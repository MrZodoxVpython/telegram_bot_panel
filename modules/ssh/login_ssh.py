from telegram_bot_panel import *
from telethon import events, Button
import subprocess
import pwd
import re

def get_user_by_pid(pid):
    try:
        uid = int(subprocess.check_output(["stat", "-c", "%u", f"/proc/{pid}"]).decode().strip())
        return pwd.getpwuid(uid).pw_name
    except:
        return "unknown"

def get_active_ssh_sessions():
    try:
        result = subprocess.run(
            ["ss", "-tunap"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        sessions = []
        for line in result.stdout.splitlines():
            if ":22" not in line or "ESTAB" not in line:
                continue

            ip_match = re.search(r"\[::ffff:([\d\.]+)\]:\d+", line)
            if not ip_match:
                continue
            ip = ip_match.group(1)

            pid_match = re.search(r"pid=(\d+)", line)
            pid = pid_match.group(1) if pid_match else "?"
            user = get_user_by_pid(pid) if pid != "?" else "unknown"

            port_match = re.search(r":22\s+\[::ffff:([\d\.]+)\]:(\d+)", line)
            port = port_match.group(2) if port_match else "?"

            sessions.append({
                "user": user,
                "ip": ip,
                "port": port,
                "pid": pid
            })

        return sessions
    except Exception as e:
        print(f"[ERROR] get_active_ssh_sessions: {e}")
        return []

@bot.on(events.CallbackQuery(data=b"trojan/login_ssh"))
async def login_ssh(event):
    sender = await event.get_sender()
    if valid(str(sender.id)) != "true":
        await event.answer("Akses ditolak!", alert=True)
        return

    sessions = get_active_ssh_sessions()

    if not sessions:
        await bot.send_message(
            event.chat_id,
            "❌ Tidak ada koneksi SSH aktif ditemukan.",
            buttons=[Button.inline("🔙 Back to Menu", b"menu")]
        )
        return

    msg = "📡 **Koneksi SSH Aktif**\n━━━━━━━━━━━━━━━━━━━━━━━\n"
    for i, s in enumerate(sessions, 1):
        msg += f"{i:02d}. 👤 `{s['user']}` | 🌐 `{s['ip']}:{s['port']}` | 🔢 PID: `{s['pid']}`\n"

    await bot.send_message(
        event.chat_id,
        msg,
        parse_mode="markdown",
        buttons=[Button.inline("🔙 Back to Menu", b"menu")]
    )

