from telegram_bot_panel import *
from telethon import events, Button
import json
import re
import os

CONFIG_PATH = "/etc/xray/config.json"

def baca_data_trojan():
    if not os.path.exists(CONFIG_PATH):
        return []

    with open(CONFIG_PATH, 'r') as f:
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
                json_text = '{' + line.strip().strip(',') + '}'
                obj = json.loads(json_text)
                akun_list.append({
                    "username": obj.get("email", "-"),
                    "password": obj.get("password", "-"),
                    "expired": current_expired
                })
            except json.JSONDecodeError:
                continue

    return akun_list

@bot.on(events.CallbackQuery(data=b"trojan/read_trojan"))
async def read_trojan_handler(event):
    akun_list = baca_data_trojan()
    if not akun_list:
        await event.edit("❌ Tidak ada akun Trojan ditemukan.")
        return

    msg = "📄 **DAFTAR AKUN TROJAN**\n━━━━━━━━━━━━━━━━━━━━━━\n"
    for akun in akun_list:
        msg += (
            f"👤 User     : `{akun['username']}`\n"
            f"🔑 Password : `{akun['password']}`\n"
            f"📆 Expired  : `{akun['expired']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
        )

    buttons = [
        [Button.inline("🔄 Refresh", b"trojan/read_trojan")]
    ]

    await event.edit(msg, buttons=buttons, parse_mode="markdown")

