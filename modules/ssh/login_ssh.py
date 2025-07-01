from telegram_bot_panel import *
from telethon import events, Button
import os
import re
import datetime as dt

AUTH_LOG_PATH = "/var/log/auth.log"

@bot.on(events.CallbackQuery(data=b"ssh/login_ssh"))
async def login_ssh(event):
    sender = await event.get_sender()
    chat_id = event.chat_id

    if valid(str(sender.id)) != "true":
        await event.answer("Akses ditolak!", alert=True)
        return

    if not os.path.exists(AUTH_LOG_PATH):
        await bot.send_message(chat_id, "❌ File log SSH tidak ditemukan.")
        return

    try:
        with open(AUTH_LOG_PATH, "r") as f:
            log_data = f.readlines()[-1000:]  # Ambil 1000 baris terakhir untuk efisiensi
    except Exception as e:
        await bot.send_message(chat_id, f"❌ Gagal membaca log: {e}")
        return

    users = {}
    pattern = r"Accepted (\w+) for (\w+) from ([\d.]+)"
    for line in log_data:
        match = re.search(pattern, line)
        if match:
            method, username, ip = match.groups()
            users[username] = ip  # Simpan yang terakhir saja (tanpa duplikat)

    if not users:
        await bot.send_message(chat_id, "❌ Tidak ada login SSH ditemukan.")
        return

    msg = "🔐 **Login SSH Terakhir**\n━━━━━━━━━━━━━━━━━━━━━━━\n"
    for i, (user, ip) in enumerate(users.items(), 1):
        msg += f"{i:02d}. 👤 `{user}` dari `{ip}`\n"

    await bot.send_message(
        chat_id,
        msg,
        parse_mode="markdown",
        buttons=[Button.inline("🔙 Back to Menu", b"menu")]
    )

