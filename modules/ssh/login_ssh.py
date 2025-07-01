from telegram_bot_panel import *
from telethon import events, Button
import subprocess
import re

@bot.on(events.CallbackQuery(data=b"ssh/login_ssh"))
async def login_ssh(event):
    sender = await event.get_sender()
    if valid(str(sender.id)) != "true":
        await event.answer("Akses ditolak!", alert=True)
        return

    try:
        result = subprocess.run(
            ["ss", "-tnp"],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.strip().splitlines()
    except Exception as e:
        await bot.send_message(event.chat_id, f"❌ Gagal membaca koneksi SSH: {e}")
        return

    connections = []
    for line in lines:
        if "ESTAB" in line and ":22" in line:
            match = re.search(r"(\d+\.\d+\.\d+\.\d+):(\d+)\s+.*pid=(\d+)", line)
            if match:
                ip, port, pid = match.groups()
                connections.append(f"🔗 {ip}:{port} | PID: {pid}")
            else:
                connections.append(f"🔗 {line.strip()}")

    if connections:
        msg = "**📡 Koneksi SSH Aktif (Tunneling):**\n\n" + "\n".join(connections)
    else:
        msg = "🛑 Tidak ada koneksi SSH aktif ditemukan."

    await bot.send_message(
        event.chat_id,
        msg,
        parse_mode="markdown",
        buttons=[Button.inline("🔙 Back to Menu", b"menu")]
    )

