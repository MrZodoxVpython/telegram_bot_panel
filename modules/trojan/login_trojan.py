from telegram_bot_panel import *
from telethon import Button
from telethon import events
import datetime as dt
import re
import os

CONFIG_PATH = "/etc/xray/config.json"
LOG_PATH = "/var/log/xray/access.log"
MAX_MSG_LENGTH = 4000

def parse_users():
    if not os.path.exists(CONFIG_PATH):
        return []
    with open(CONFIG_PATH) as f:
        raw = f.read()
    pattern = r"#\!\s+([^\s]+)\s+(\d{4}-\d{2}-\d{2})"
    all_matches = re.findall(pattern, raw)

    seen = set()
    unique = []
    for uname, exp in all_matches:
        if uname not in seen:
            unique.append((uname, exp))
            seen.add(uname)
    return unique

def is_user_active(user, since_minutes=1):
    try:
        start_time = (dt.datetime.now() - dt.timedelta(minutes=since_minutes)).strftime("%Y/%m/%d %H:%M:%S")
        if not os.path.exists(LOG_PATH):
            return False
        with open(LOG_PATH, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            offset = min(size, 1024 * 1000)
            f.seek(-offset, os.SEEK_END)
            lines = f.read().decode(errors="ignore").splitlines()
        for line in reversed(lines):
            if f"email: {user}" in line:
                parts = line.strip().split()
                if len(parts) >= 2:
                    timestamp = f"{parts[0]} {parts[1]}"
                    if timestamp > start_time:
                        return True
                break
    except Exception as e:
        print(f"[ERROR] Failed to read log: {e}")
    return False

@bot.on(events.CallbackQuery(data=b"trojan/login_trojan"))
async def login_trojan(event):
    sender = await event.get_sender()
    if valid(str(sender.id)) != "true":
        await event.answer("Akses ditolak!", alert=True)
        return

    users = parse_users()
    if not users:
        await bot.send_message(event.chat_id, "❌ Tidak ada user Trojan ditemukan.")
        return

    msg = "👤 Status Login Trojan (±1 menit terakhir):\n\n"
    count = 0

    for i, (uname, _) in enumerate(users, 1):
        status = "✅ Aktif" if is_user_active(uname) else "❌ Tidak Aktif"
        line = f"{i:02d}. `{uname}` → {status}\n"
        if len(msg) + len(line) > MAX_MSG_LENGTH:
            await bot.send_message(event.chat_id, msg)
            msg = ""
        msg += line
        count += 1

    if msg:
        await bot.send_message(
            event.chat_id,
            msg,
            buttons=[Button.inline("🔙 Back to Menu", b"menu")]
        )

    if count == 0:
        await bot.send_message(
            event.chat_id,
            "❌ Tidak ada akun Trojan ditemukan.",
            buttons=[Button.inline("🔙 Back to Menu", b"start")]
        )
