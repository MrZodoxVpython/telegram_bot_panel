from telegram_bot_panel import *
import os
import json
import re
from telethon import events, Button

@bot.on(events.CallbackQuery(data=b"trojan/read_trojan"))
async def read_trojan(event):
    sender = await event.get_sender()
    chat = event.chat_id

    if valid(str(sender.id)) != "true":
        await event.answer("Akses ditolak!", alert=True)
        return

    config_path = "/etc/xray/config.json"
    if not os.path.exists(config_path):
        await event.respond("❌ File config.json tidak ditemukan.")
        return

    with open(config_path, 'r') as f:
        lines = f.readlines()

    akun_list = []
    current_expired = ""
    current_username = ""

    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("#!"):
            match = re.match(r"#!\s*(\S+)\s+(\d{4}-\d{2}-\d{2})", line)
            if match:
                current_username = match.group(1)
                current_expired = match.group(2)

        elif '"password"' in line and '"email"' in line:
            try:
                # Hilangkan koma di akhir
                cleaned = line.rstrip(',').strip()
                obj = json.loads(cleaned)
                akun_list.append({
                    "username": obj.get("email", "-"),
                    "password": obj.get("password", "-"),
                    "expired": current_expired
                })
            except Exception as e:
                continue

    if not akun_list:
        await event.respond("❌ Tidak ada akun Trojan ditemukan.")
        return

    msg = "**📄 Daftar Akun Trojan:**\n\n"
    for i, akun in enumerate(akun_list, 1):
        msg += f"""`{i}. {akun['username']} | {akun['password']} | {akun['expired']}`\n"""

    await bot.send_message(chat, msg, parse_mode="markdown")

