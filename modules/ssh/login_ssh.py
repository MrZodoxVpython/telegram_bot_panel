from telegram_bot_panel import *
from telethon import events, Button
import subprocess
import re
import pwd

def parse_logged_ssh():
    try:
        output = subprocess.check_output(['ss', '-tnp']).decode()
    except Exception as e:
        print(f"[ERROR] Failed to run ss: {e}")
        return []

    results = []
    lines = output.strip().split('\n')
    count = 1
    for line in lines:
        if "sshd" in line and "ESTAB" in line:
            try:
                ip_port_match = re.search(r'src\s+\S+:(\d+)\s+dst\s+(\S+):(\d+)', line)
                user_pid_match = re.search(r'users:\(\("sshd",pid=(\d+),fd=\d+\)\)', line)
                if ip_port_match and user_pid_match:
                    local_port = ip_port_match.group(1)
                    remote_ip = ip_port_match.group(2)
                    remote_port = ip_port_match.group(3)
                    pid = user_pid_match.group(1)

                    # Get username by PID
                    try:
                        uid = int(subprocess.check_output(['ps', '-o', 'uid=', '-p', pid]).decode().strip())
                        user = pwd.getpwuid(uid).pw_name
                    except:
                        user = 'unknown'

                    results.append((count, user, remote_ip, remote_port, pid))
                    count += 1
            except:
                continue
    return results

@bot.on(events.CallbackQuery(data=b"trojan/login_ssh"))
async def login_ssh(event):
    sender = await event.get_sender()
    if valid(str(sender.id)) != "true":
        await event.answer("Akses ditolak!", alert=True)
        return

    entries = parse_logged_ssh()
    if not entries:
        await event.respond("❌ Tidak ada login SSH aktif.")
        return

    msg = "🔐 **Status Login SSH Aktif:**\n\n"
    for no, user, ip, port, pid in entries:
        msg += f"{no:02d}. 👤 `{user}` | 🌐 `{ip}:{port}` | 🆔 PID: `{pid}`\n"

    await bot.send_message(
        event.chat_id,
        msg,
        buttons=[Button.inline("🔙 Back to Menu", b"menu")],
        parse_mode="markdown"
    )

