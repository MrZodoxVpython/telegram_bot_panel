from telegram_bot_panel import *
from telethon import Button
from telethon import events
import re
import os
import datetime as DT

@bot.on(events.CallbackQuery(data=b"trojan/read_trojan"))
async def read_trojan(event):
    sender = await event.get_sender()
    chat_id = event.chat_id

    if valid(str(sender.id)) != "true":
        await event.answer("Akses ditolak!", alert=True)
        return

    config_path = "/etc/xray/config.json"
    if not os.path.exists(config_path):
        await bot.send_message(chat_id, "❌ File konfigurasi tidak ditemukan.")
        return

    with open(config_path, "r") as f:
        lines = f.readlines()

    users = {}
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("#! "):
            try:
                username, expired = line[3:].rsplit(" ", 1)
                next_line = lines[i + 1].strip()
                match = re.search(r'"password":\s*"([^"]+)",\s*"email":\s*"([^"]+)"', next_line)
                if match and match.group(2) == username:
                    users[username] = {
                        "expired": expired,
                        "password": match.group(1)
                    }
            except Exception:
                continue

    if not users:
        await bot.send_message(chat_id, "❌ Tidak ada akun Trojan ditemukan.")
        return

    # Bikin output rapi
    msg = "📋 **Daftar Akun Trojan**\n━━━━━━━━━━━━━━━━━━━━━━━\n"
    for username, data in users.items():
        expired_fmt = DT.datetime.strptime(data["expired"], "%Y-%m-%d").strftime("%d %B %Y")
        msg += f"👤 `{username}`\n📆 *Expired:* `{expired_fmt}`\n🔑 *Password:* `{data['password']}`\n━━━━━━━━━━━━━━━━━━━━━━━\n"

    await bot.send_message(chat_id, msg, parse_mode="markdown")
    if msg:
        await bot.send_message(
            event.chat_id,
            msg,
            buttons=[Button.inline("🔙 Back to Menu", b"start")]
        )

    if count == 0:
        await bot.send_message(
            event.chat_id,
            "❌ Tidak ada akun Trojan ditemukan.",
            buttons=[Button.inline("🔙 Back to Menu", b"start")]
        )
