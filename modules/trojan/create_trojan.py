from telegram_bot_panel import *
import uuid
import os
import datetime as DT
import subprocess
from telethon import events, Button

data_trojan = {}

def hitung_expired(input_str):
    if input_str.isdigit():
        return (DT.datetime.now() + DT.timedelta(days=int(input_str))).strftime("%Y-%m-%d")
    return input_str

def insert_to_tag(config_path, tag, comment, entry):
    if not os.path.exists(config_path):
        return False

    with open(config_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    inserted = False

    for i, line in enumerate(lines):
        line = line.rstrip()
        new_lines.append(line)

        if f"#{tag}" in line and not inserted:
            new_lines.append(comment)
            new_lines.append(f'}},{{{entry}')  # <- betul json
            inserted = True

    if inserted:
        with open(config_path, 'w') as f:
            f.write('\n'.join(new_lines) + '\n')

    return inserted

@bot.on(events.CallbackQuery(data=b"trojan/create_trojan"))
async def create_trojan(event):
    sender = await event.get_sender()
    chat = event.chat_id

    if valid(str(sender.id)) != "true":
        await event.answer("Akses ditolak!", alert=True)
        return

    async with bot.conversation(chat) as conv:
        await conv.send_message("🧑 Masukkan Username:")
        username = (await conv.wait_event(events.NewMessage(from_users=sender.id))).raw_text.strip()

        await conv.send_message("📆 Masukkan Masa Aktif (hari):")
        expired_input = (await conv.wait_event(events.NewMessage(from_users=sender.id))).raw_text.strip()
        expired = hitung_expired(expired_input)

        data_trojan[chat] = {
            "username": username,
            "expired": expired
        }

        await conv.send_message("🔑 Gunakan UUID otomatis atau manual?", buttons=[
            [Button.inline("🔄 Otomatis", b"trojan_uuid_auto")],
            [Button.inline("✍️ Manual", b"trojan_uuid_manual")]
        ])

@bot.on(events.CallbackQuery(data=b"trojan_uuid_auto"))
async def trojan_uuid_auto(event):
    chat = event.chat_id
    data = data_trojan.get(chat)
    if not data:
        await event.edit("❌ Data tidak ditemukan.")
        return

    password = str(uuid.uuid4())
    await finish_trojan(event, data["username"], data["expired"], password)

@bot.on(events.CallbackQuery(data=b"trojan_uuid_manual"))
async def trojan_uuid_manual(event):
    chat = event.chat_id
    sender = await event.get_sender()
    data = data_trojan.get(chat)
    if not data:
        await event.edit("❌ Data tidak ditemukan.")
        return

    async with bot.conversation(chat) as conv:
        await conv.send_message("✍️ Kirimkan password/UUID manual:")
        msg = await conv.wait_event(events.NewMessage(from_users=sender.id))
        password = msg.raw_text.strip()

    await finish_trojan(event, data["username"], data["expired"], password)

async def finish_trojan(event, username, expired, password):
    config_path = "/etc/xray/config.json"
    domain_file = "/etc/xray/domain"
    comment_line = f"#! {username} {expired}"
    json_line = f'"password": "{password}", "email": "{username}"'

    tags = ["trojanws", "trojangrpc"]
    success = True
    for tag in tags:
        if not insert_to_tag(config_path, tag, comment_line, json_line):
            success = False

    if success:
        subprocess.call("systemctl restart xray", shell=True)

        try:
            with open(domain_file) as f:
                domain = f.read().strip()
        except:
            domain = "yourdomain.com"

        tls = "443"
        ntls = "80"
        path = "/trojan-ws"
        grpc_service = "trojan-grpc"
        expired_date = DT.datetime.strptime(expired, "%Y-%m-%d").strftime("%d %B %Y")

        msg = f"""```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           TROJAN ACCOUNT          
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Remarks        : {username}
Host/IP        : {domain}
Wildcard       : (bug.com).{domain}
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

        buttons = [
            [Button.url("🔧 Repository", "https://github.com/MrZodoxVpython"),
             Button.url("📢 Channel", "https://t.me/MrZodoxVpython")]
        ]
        await bot.send_message(event.chat_id, msg, buttons=buttons, parse_mode="markdown")
    else:
        await bot.send_message(event.chat_id, "❌ Gagal menambahkan akun ke Xray.")

