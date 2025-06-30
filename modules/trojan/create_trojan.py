from telegram_bot_panel import *
import uuid
import subprocess
import os
from datetime import datetime, timedelta
from telethon import events, Button

@bot.on(events.CallbackQuery(data=b"trojan/create_trojan"))
async def create_trojan(event):
    async def create_trojan_(event):
        chat = event.chat_id
        sender = await event.get_sender()

        # ── Input Username ──
        async with bot.conversation(chat) as conv:
            await event.respond("**Input Username:**")
            username = (await conv.wait_event(events.NewMessage(incoming=True, from_users=sender.id))).raw_text.strip()

        # ── Input Expired (via tombol) ──
        async with bot.conversation(chat) as conv:
            await event.respond("**Choose Expiry Days:**", buttons=[
                [Button.inline("3 Day", b"3"), Button.inline("7 Day", b"7")],
                [Button.inline("30 Day", b"30"), Button.inline("60 Day", b"60")]
            ])
            exp = (await conv.wait_event(events.CallbackQuery)).data.decode("utf-8")

        expired_date = (datetime.now() + timedelta(days=int(exp))).strftime("%Y-%m-%d")

        # ── UUID Manual / Otomatis ──
        async with bot.conversation(chat) as conv:
            await event.respond("**Gunakan password UUID otomatis?**", buttons=[
                [Button.inline("✅ Ya (Otomatis)", b"auto")],
                [Button.inline("✏️ Manual (Ketik Sendiri)", b"manual")]
            ])
            mode = (await conv.wait_event(events.CallbackQuery)).data.decode("utf-8")

        if mode == "manual":
            async with bot.conversation(chat) as conv:
                await event.respond("**Masukkan Password/UUID:**")
                password = (await conv.wait_event(events.NewMessage(incoming=True, from_users=sender.id))).raw_text.strip()
        else:
            password = str(uuid.uuid4())

        # ── Insert ke config.json ──
        config_path = "/etc/xray/config.json"
        tag_list = ["trojanws", "trojangrpc"]
        comment_line = f"#! {username} {expired_date}"
        entry_json = f'{{"password": "{password}", "email": "{username}"}}'
        success = False

        def insert_to_tag(cfg_path, tag, comment, entry):
            if not os.path.exists(cfg_path):
                return False
            with open(cfg_path, "r") as f:
                lines = f.readlines()

            new_lines = []
            inserted = False
            for line in lines:
                new_lines.append(line.rstrip())
                if f"#{tag}" in line and not inserted:
                    new_lines.append(comment)
                    new_lines.append(f'}},{{{entry[1:-1]}')  # Format benar
                    inserted = True

            if inserted:
                with open(cfg_path, "w") as f:
                    f.write("\n".join(new_lines) + "\n")
            return inserted

        success = all(insert_to_tag(config_path, tag, comment_line, entry_json) for tag in tag_list)

        # ── Restart Xray ──
        if success:
            subprocess.call("systemctl restart xray", shell=True)
            domain = open("/etc/xray/domain").read().strip() if os.path.exists("/etc/xray/domain") else "yourdomain.com"

            msg = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           TROJAN ACCOUNT          
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Remarks        : {username}
Host/IP        : {domain}
Wildcard       : (bug.com).{domain}
Port TLS       : 443
Port non-TLS   : 80
Port gRPC      : 443
Password       : {password}
Path           : /trojan-ws
ServiceName    : trojan-grpc
Expired On     : {expired_date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Link TLS       : trojan://{password}@{domain}:443?path=/trojan-ws&security=tls&type=ws#{username}
Link non-TLS   : trojan://{password}@{domain}:80?path=/trojan-ws&security=none&type=ws#{username}
Link gRPC      : trojan://{password}@{domain}:443?mode=gun&security=tls&type=grpc&serviceName=trojan-grpc#{username}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            await event.respond(msg)
        else:
            await event.respond("❌ Gagal menambahkan ke salah satu tag config.")

    sender = await event.get_sender()
    if valid(str(sender.id)) == "true":
        await create_trojan_(event)
    else:
        await event.answer("Akses Ditolak", alert=True)

