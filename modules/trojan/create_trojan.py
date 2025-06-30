from telegram_bot_panel import *
import json, os, subprocess
from datetime import datetime, timedelta

@bot.on(events.CallbackQuery(data=b"trojan/create_trojan"))
async def create_trojan(event):
    async def create_trojan_(event):
        chat = event.chat_id

        # Minta Username
        async with bot.conversation(chat) as convo:
            await event.respond("**Username:**")
            username = (await convo.wait_event(events.NewMessage(incoming=True, from_users=sender.id))).raw_text.strip()

        # Minta Password / UUID
        async with bot.conversation(chat) as convo:
            await event.respond("**Password (UUID):**")
            password = (await convo.wait_event(events.NewMessage(incoming=True, from_users=sender.id))).raw_text.strip()

        # Pilih Masa Aktif
        async with bot.conversation(chat) as convo:
            await event.respond("**Choose Expiry Day**", buttons=[
                [Button.inline("• 3 Day •", b"3"), Button.inline("• 7 Day •", b"7")],
                [Button.inline("• 30 Day •", b"30"), Button.inline("• 60 Day •", b"60")]
            ])
            exp_event = await convo.wait_event(events.CallbackQuery)
            exp_days = int(exp_event.data.decode("ascii"))
            expired_date = (datetime.now() + timedelta(days=exp_days)).strftime("%Y-%m-%d")

        # Proses Tambah ke config.json
        config_path = "/etc/xray/config.json"
        domain_path = "/etc/xray/domain"
        domain = open(domain_path).read().strip() if os.path.exists(domain_path) else "yourdomain.com"

        tags = ["trojanws", "trojangrpc"]
        comment_line = f"#! {username} {expired_date}"
        json_entry = f'{{"password": "{password}", "email": "{username}"}}'

        def insert_to_tag(path, tag, comment, entry):
            if not os.path.exists(path):
                return False

            with open(path, 'r') as f:
                lines = f.readlines()

            new_lines = []
            inserted = False

            for i, line in enumerate(lines):
                stripped = line.strip()
                new_lines.append(line.rstrip())
                if f"#{tag}" in stripped and not inserted:
                    # Tambahkan komentar dan baris JSON dengan format yang benar
                    new_lines.append(comment)
                    new_lines.append(f'}},{entry[1:]}')
                    inserted = True

            if inserted:
                with open(path, 'w') as f:
                    f.write('\n'.join(new_lines) + '\n')
            return inserted

        success = True
        for tag in tags:
            if not insert_to_tag(config_path, tag, comment_line, json_entry):
                success = False

        if success:
            subprocess.call("systemctl restart xray", shell=True)

            tls = "443"
            ntls = "80"
            path = "/trojan-ws"
            grpc_service = "trojan-grpc"

            msg = f"""
**━━━━━━━━━━━━━━━━**
**⟨ TROJAN Account ⟩**
**━━━━━━━━━━━━━━━━**
**» Host:** `{domain}`
**» Username:** `{username}`
**» Password:** `{password}`
**» Port TLS:** `443`
**» Port non-TLS:** `80`
**» Port gRPC:** `443`
**» Path:** `{path}`
**» ServiceName:** `{grpc_service}`
**» Expired:** `{expired_date}`
**━━━━━━━━━━━━━━━━**
**⟨ Trojan Links ⟩**
🔗 TLS: `trojan://{password}@{domain}:443?path={path}&security=tls&type=ws#{username}`
🔗 non-TLS: `trojan://{password}@{domain}:80?path={path}&security=none&type=ws#{username}`
🔗 gRPC: `trojan://{password}@{domain}:443?mode=gun&security=tls&type=grpc&serviceName={grpc_service}#{username}`
**━━━━━━━━━━━━━━━━**
**🤖 @XolPanel**
"""
            inline = [
                [Button.url("[ GitHub Repo ]", "https://github.com/xolvaid/simplepanel"),
                 Button.url("[ Channel ]", "https://t.me/XolPanel")]
            ]
            await event.respond(msg, buttons=inline)
        else:
            await event.respond("❌ Gagal menambahkan akun ke salah satu tag.")

    sender = await event.get_sender()
    a = valid(str(sender.id))
    if a == "true":
        await create_trojan_(event)
    else:
        await event.answer("Access Denied", alert=True)

