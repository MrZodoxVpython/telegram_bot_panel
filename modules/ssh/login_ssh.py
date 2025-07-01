from telegram_bot_panel import *
from telethon import events, Button
import subprocess
import re

@bot.on(events.CallbackQuery(pattern=b".*login_ssh"))
async def login_ssh(event):
    # Hilangkan spinner Telegram
    await event.answer()

    sender = await event.get_sender()
    if valid(str(sender.id)) != "true":
        # Jika tidak valid, kasih alert
        await event.answer("Akses ditolak!", alert=True)
        return

    # Ambil baris ssd yang ESTAB
    try:
        proc = subprocess.run(["ss", "-tnp"], capture_output=True, text=True, check=True)
        lines = [l for l in proc.stdout.splitlines() if "ESTAB" in l and "sshd" in l]
    except Exception as e:
        await event.edit(f"❌ Gagal menjalankan ss: `{e}`", parse_mode="markdown")
        return

    if not lines:
        await event.edit(
            "❌ Tidak ada koneksi SSH aktif saat ini.",
            buttons=[Button.inline("🔙 Back to Menu", b"menu")]
        )
        return

    # Build message
    msg = "🔐 **Koneksi SSH Aktif:**\n"
    msg += "`No │ User       │ IP             │ Port │ PID`\n"
    msg += "────────────────────────────────────────\n"

    for idx, line in enumerate(lines, 1):
        parts = line.split()
        remote = parts[4]  # dst address
        ip, port = remote.rsplit(":", 1)
        pid_m = re.search(r"pid=(\d+)", line)
        pid = pid_m.group(1) if pid_m else "?"
        # ambil user via ps
        try:
            user = subprocess.check_output(
                ["ps", "-o", "user=", "-p", pid],
                text=True
            ).strip()
        except:
            user = "unknown"

        msg += f"`{idx:02d} │ {user:<9} │ {ip:<15} │ {port:<4} │ {pid}`\n"

    await event.edit(
        msg,
        parse_mode="markdown",
        buttons=[Button.inline("🔙 Back to Menu", b"menu")]
    )

