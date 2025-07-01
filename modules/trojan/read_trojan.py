from telegram_bot_panel import *
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
    parsing_tag = None  # hanya aktif jika sedang berada di tag #trojanws

    for i, line in enumerate(lines):
        line = line.strip()
        
        if line == "#trojanws":
            parsing_tag = "trojanws"
            continue
        elif line == "#trojangrpc":
            parsing_tag = None
            continue

        if parsing_tag == "trojanws" and line.startswith("#! "):
            try:
                username_raw, expired = line[3:].rsplit(" ", 1)
                username = username_raw.strip().lower()
                next_line = lines[i + 1].strip()
                match = re.search(r'"password":\s*"([^"]+)",\s*"email":\s*"([^"]+)"', next_line)
                if match and match.group(2).strip().lower() == username:
                    users[username] = {
                        "expired": expired,
                        "password": match.group(1)
                    }
            except Exception:
                continue

    if not users:
        await bot.send_message(chat_id, "❌ Tidak ada akun Trojan ditemukan.")
        return

    msg = "📋 **Daftar Akun Trojan (WS)**\n━━━━━━━━━━━━━━━━━━━━━━━\n"
    for username, data in users.items():
        try:
            expired_fmt = DT.datetime.strptime(data["expired"], "%Y-%m-%d").strftime("%d %B %Y")
        except Exception:
            expired_fmt = data["expired"]
        msg += f"👤 `{username}`\n📆 *Expired:* `{expired_fmt}`\n🔑 *Password:* `{data['password']}`\n━━━━━━━━━━━━━━━━━━━━━━━\n"

    await bot.send_message(chat_id, msg, parse_mode="markdown")

