from telegram_bot_panel import *
from telethon import events, Button
import subprocess
import re

@bot.on(events.CallbackQuery(data=b"trojan/login_ssh"))
async def login_ssh(event):
    sender = await event.get_sender()
    if valid(str(sender.id)) != "true":
        await event.answer("Akses ditolak!", alert=True)
        return

    # Jalankan ss dan filter baris sshd ESTAB
    try:
        proc = subprocess.run(["ss", "-tnp"], capture_output=True, text=True, check=True)
        lines = [l for l in proc.stdout.splitlines() if "ESTAB" in l and "sshd" in l]
    except Exception as e:
        await bot.send_message(
            event.chat_id,
            f"❌ Gagal menjalankan ss: `{e}`",
            parse_mode="markdown",
            buttons=[Button.inline("🔙 Back to Menu", b"menu")]
        )
        return

    if not lines:
        await bot.send_message(
            event.chat_id,
            "❌ Tidak ada koneksi SSH aktif saat ini.",
            buttons=[Button.inline("🔙 Back to Menu", b"menu")]
        )
        return

    # Bangun pesan output
    msg = "🔐 **Koneksi SSH Aktif:**\n"
    msg += "`No │ User       │ IP             │ Port │ PID`\n"
    msg += "────────────────────────────────────────\n"

    for idx, line in enumerate(lines, 1):
        parts = line.split()
        # remote address ada di kolom ke-5 (indeks 4)
        remote = parts[4]
        # pisah IP dan port
        if ":" in remote:
            ip, port = remote.rsplit(":", 1)
        else:
            ip, port = remote, "?"
        # ambil PID
        pid_m = re.search(r"pid=(\d+)", line)
        pid = pid_m.group(1) if pid_m else "?"
        # ambil username via ps
        try:
            user = subprocess.check_output(["ps", "-o", "user=", "-p", pid], text=True).strip()
        except:
            user = "unknown"
        # format baris
        msg += f"`{idx:02d} │ {user:<9} │ {ip:<15} │ {port:<4} │ {pid}`\n"

    await bot.send_message(
        event.chat_id,
        msg,
        parse_mode="markdown",
        buttons=[Button.inline("🔙 Back to Menu", b"menu")]
    )

