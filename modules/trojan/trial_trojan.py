from telegram_bot_panel import *
from telethon import events, Button
import uuid
import os
import random
import string
import datetime as DT
import subprocess
import asyncio

TRIAL_TAGS = ["trojanws", "trojangrpc"]
CONFIG_PATH = "/etc/xray/config.json"
DOMAIN_FILE = "/etc/xray/domain"

def generate_trial_username():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"trial{suffix}"

def get_expired_time(option: str):
    now = DT.datetime.now()
    if option == "1jam":
        return (now + DT.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    else:
        return (now + DT.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

def insert_to_config(tag, comment, entry):
    if not os.path.exists(CONFIG_PATH):
        return False

    with open(CONFIG_PATH, 'r') as f:
        lines = f.readlines()

    new_lines = []
    inserted = False

    for line in lines:
        new_lines.append(line.rstrip())
        if f"#{tag}" in line and not inserted:
            new_lines.append(comment)
            new_lines.append(f'}},{{{entry}')
            inserted = True

    if inserted:
        with open(CONFIG_PATH, 'w') as f:
            f.write('\n'.join(new_lines) + '\n')

    return inserted

async def auto_delete_trial(username, expired_at_str):
    await asyncio.sleep(2)  # delay untuk pastikan config disimpan
    expired_at = DT.datetime.strptime(expired_at_str, "%Y-%m-%d %H:%M:%S")
    now = DT.datetime.now()
    delay = (expired_at - now).total_seconds()

    if delay > 0:
        await asyncio.sleep(delay)

    # Hapus akun dari semua tag
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            lines = f.readlines()

        new_lines = []
        skip = False
        deleted = False

        for line in lines:
            if line.strip().startswith(f"#! {username} "):
                skip = True
                deleted = True
                continue
            if skip:
                skip = False
                continue
            new_lines.append(line)

        if deleted:
            with open(CONFIG_PATH, "w") as f:
                f.writelines(new_lines)
            subprocess.call("systemctl restart xray", shell=True)

@bot.on(events.CallbackQuery(data=b"trojan/trial_trojan"))
async def trial_trojan(event):
    sender = await event.get_sender()
    chat_id = event.chat_id

    if valid(str(sender.id)) != "true":
        await event.answer("Akses ditolak!", alert=True)
        return

    buttons = [
        [Button.inline("🕐 1 Jam", b"trial:1jam")],
        [Button.inline("📅 1 Hari", b"trial:1hari")]
    ]
    await event.respond("⏳ Pilih durasi trial:", buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"trial:(.+)"))
async def trial_duration_selected(event):
    option = event.pattern_match.group(1).decode()
    chat_id = event.chat_id
    username = generate_trial_username()
    password = str(uuid.uuid4())
    expired_at = get_expired_time(option)
    expired_date = DT.datetime.strptime(expired_at, "%Y-%m-%d %H:%M:%S").strftime("%d %B %Y %H:%M")

    comment_line = f"#! {username} {expired_at}"
    json_line = f'"password": "{password}", "email": "{username}"'

    success = True
    for tag in TRIAL_TAGS:
        if not insert_to_config(tag, comment_line, json_line):
            success = False

    if success:
        subprocess.call("systemctl restart xray", shell=True)
        try:
            with open(DOMAIN_FILE) as f:
                domain = f.read().strip()
        except:
            domain = "yourdomain.com"

        tls = "443"
        ntls = "80"
        path = "/trojan-ws"
        grpc_service = "trojan-grpc"

        msg = f"""```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          TRIAL TROJAN ACCOUNT     
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Remarks        : {username}
Host/IP        : {domain}
Port TLS       : {tls}
Port non-TLS   : {ntls}
Port gRPC      : {tls}
Password       : {password}
Path           : {path}
ServiceName    : {grpc_service}
Expired On     : {expired_date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Link TLS       : trojan://{password}@{domain}:{tls}?path={path}&security=tls&type=ws#{username}
Link non-TLS   : trojan://{password}@{domain}:{ntls}?path={path}&security=none&type=ws#{username}
Link gRPC      : trojan://{password}@{domain}:{tls}?mode=gun&security=tls&type=grpc&serviceName={grpc_service}#{username}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```"""

        await bot.send_message(chat_id, msg, parse_mode="markdown")

        # Jalankan auto delete di background
        asyncio.create_task(auto_delete_trial(username, expired_at))
    else:
        await bot.send_message(chat_id, "❌ Gagal membuat akun trial.")

