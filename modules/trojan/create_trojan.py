from telegram_bot_panel import *
import uuid
import subprocess
import os
import datetime as DT

@bot.on(events.CallbackQuery(data=b"trojan/create_trojan"))
async def create_trojan(event):
    async def create_trojan_flow(event):
        sender = await event.get_sender()
        chat = event.chat_id

        # 1. Username
        async with bot.conversation(chat) as conv:
            await event.respond("**Masukkan Username:**")
            response = await conv.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
            user = response.raw_text.strip()

        # 2. Expired
        async with bot.conversation(chat) as conv:
            await event.respond("**Masa aktif (hari):**")
            response = await conv.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
            exp_day = int(response.raw_text.strip())

        # 3. Pilih UUID otomatis atau manual
        await event.respond("**Gunakan UUID otomatis atau manual?**", buttons=[
            [Button.inline("🔄 Otomatis (UUID)", b"uuid_auto")],
            [Button.inline("✍️ Manual", b"uuid_manual")]
        ])
        uuid_choice = await bot.wait_event(events.CallbackQuery)
        if uuid_choice.data == b"uuid_auto":
            password = str(uuid.uuid4())
        else:
            async with bot.conversation(chat) as conv:
                await event.respond("**Masukkan Password/UUID manual:**")
                response = await conv.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
                password = response.raw_text.strip()

        # 4. Proses expired
        today = DT.date.today()
        expired = today + DT.timedelta(days=exp_day)
        expired_str = expired.strftime("%Y-%m-%d")

        # 5. Masukkan ke config
        config_path = "/etc/xray/config.json"
        domain_path = "/etc/xray/domain"
        comment = f"#! {user} {expired_str}"
        entry = f'{{"password": "{password}", "email": "{user}"}}'

        def insert_to_tag(tag):
            if not os.path.exists(config_path):
                return False
            with open(config_path, "r") as f:
                lines = f.readlines()
            new_lines = []
            inserted = False
            for line in lines:
                new_lines.append(line.rstrip())
                if f"#{tag}" in line and not inserted:
                    new_lines.append(comment)
                    new_lines.append(f"}},\n{entry}")
                    inserted = True
            if inserted:
                with open(config_path, "w") as f:
                    f.write("\n".join(new_lines) + "\n")
            return inserted

        success_ws = insert_to_tag("trojanws")
        success_grpc = insert_to_tag("trojangrpc")

        if not (success_ws and success_grpc):
            await event.respond("❌ Gagal menambahkan akun ke config.json")
            return

        subprocess.call(["systemctl", "restart", "xray"])

        # 6. Ambil domain
        try:
            with open(domain_path, "r") as f:
                domain = f.read().strip()
        except:
            domain = "yourdomain.com"

        tls = "443"
        ntls = "80"
        grpc = "trojan-grpc"
        path = "/trojan-ws"

        # 7. Kirim hasil
        msg = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           TROJAN ACCOUNT          
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Remarks        : {user}
Host/IP        : {domain}
Wildcard       : (bug.com).{domain}
Port TLS       : {tls}
Port non-TLS   : {ntls}
Port gRPC      : {tls}
Password       : {password}
Path           : {path}
ServiceName    : {grpc}
Expired On     : {expired_str}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Link TLS       : trojan://{password}@{domain}:{tls}?path={path}&security=tls&type=ws#{user}
Link non-TLS   : trojan://{password}@{domain}:{ntls}?path={path}&security=none&type=ws#{user}
Link gRPC      : trojan://{password}@{domain}:{tls}?mode=gun&security=tls&type=grpc&serviceName={grpc}#{user}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        buttons = [
            [Button.url("[ GitHub Repo ]", "https://github.com/xolvaid/simplepanel"),
             Button.url("[ Channel ]", "https://t.me/XolPanel")]
        ]
        await event.respond(msg, buttons=buttons)

    sender = await event.get_sender()
    a = valid(str(sender.id))
    if a == "true":
        await create_trojan_flow(event)
    else:
        await event.answer("Akses ditolak", alert=True)

