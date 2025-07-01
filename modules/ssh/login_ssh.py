from telegram_bot_panel import *
from telethon import events, Button
import subprocess
import re

@bot.on(events.CallbackQuery(data=b"login_ssh"))
async def login_ssh_handler(event):
    sender = await event.get_sender()
    if valid(str(sender.id)) != "true":
        await event.answer("Akses ditolak!", alert=True)
        return

    try:
        # Jalankan perintah ss untuk mendeteksi koneksi aktif ke port 22 (SSH)
        result = subprocess.run(
            ["ss", "-tnp"], capture_output=True, text=True
        )
        lines = result.stdout.splitlines()

        ssh_connections = []
        for line in lines:
            if ":22" in line and "ESTAB" in line:
                match = re.search(r"src\s+(\S+):(\d+)\s+dst\s+(\S+):22.*users:\(\("ssh[d]?",pid=(\d+),fd=\d+\)\)", line)
                if match:
                    ip = match.group(1)
                    port = match.group(2)
                    pid = match.group(4)
                    ssh_connections.append(f"🔐 IP: `{ip}` | Port: `{port}` | PID: `{pid}`")

        if not ssh_connections:
            message = "❌ Tidak ada koneksi SSH aktif saat ini."
        else:
            message = "📡 **Daftar Koneksi SSH Aktif:**\n\n" + "\n".join(ssh_connections)

        await bot.send_message(
            event.chat_id,
            message,
            parse_mode="markdown",
            buttons=[Button.inline("🔙 Back to Menu", b"menu")]
        )

    except Exception as e:
        await bot.send_message(
            event.chat_id,
            f"❌ Gagal membaca koneksi SSH aktif.\nError: `{str(e)}`",
            parse_mode="markdown",
            buttons=[Button.inline("🔙 Back to Menu", b"menu")]
        )

