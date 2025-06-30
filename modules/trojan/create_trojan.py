from telegram_bot_panel import *
import uuid, os
import datetime as DT
from telethon import events, Button

data_session = {}

@bot.on(events.CallbackQuery(data=b"trojan/create_trojan"))
async def start_create_trojan(event):
    chat = event.chat_id
    sender = await event.get_sender()

    async with bot.conversation(chat) as conv:
        await conv.send_message("🧑 Masukkan Username:")
        username = (await conv.wait_event(events.NewMessage(from_users=sender.id))).raw_text.strip()

        await conv.send_message("📆 Masukkan masa aktif (hari):")
        hari = (await conv.wait_event(events.NewMessage(from_users=sender.id))).raw_text.strip()
        expired = (DT.datetime.now() + DT.timedelta(days=int(hari))).strftime("%Y-%m-%d")

        # Simpan ke session sementara
        data_session[chat] = {
            "username": username,
            "expired": expired
        }

        await conv.send_message("🔑 Pilih UUID:", buttons=[
            [Button.inline("🔄 Otomatis", b"trojan_uuid_auto")],
            [Button.inline("✍️ Manual", b"trojan_uuid_manual")]
        ])

@bot.on(events.CallbackQuery(data=b"trojan_uuid_auto"))
async def trojan_uuid_auto(event):
    chat = event.chat_id
    sender = await event.get_sender()

    data = data_session.get(chat)
    if not data:
        await event.edit("❌ Data sesi tidak ditemukan.")
        return

    password = str(uuid.uuid4())
    await finish_trojan(event, data["username"], data["expired"], password)

@bot.on(events.CallbackQuery(data=b"trojan_uuid_manual"))
async def trojan_uuid_manual(event):
    chat = event.chat_id
    sender = await event.get_sender()

    data = data_session.get(chat)
    if not data:
        await event.edit("❌ Data sesi tidak ditemukan.")
        return

    await event.edit("✍️ Masukkan Password/UUID manual:")

    msg = await bot.wait_for(events.NewMessage(from_users=sender.id))
    password = msg.raw_text.strip()

    await finish_trojan(event, data["username"], data["expired"], password)

async def finish_trojan(event, username, expired, password):
    domain = open("/etc/xray/domain").read().strip()
    tls = "443"
    grpc_service = "trojan-grpc"
    path = "/trojan-ws"

    reply = f"""
TROJAN ACCOUNT
━━━━━━━━━━━━━━━━
User       : {username}
Password   : {password}
Expired    : {expired}

Link TLS   : trojan://{password}@{domain}:{tls}?type=ws&security=tls&path={path}#{username}
Link gRPC  : trojan://{password}@{domain}:{tls}?type=grpc&security=tls&serviceName={grpc_service}#{username}
━━━━━━━━━━━━━━━━
"""
    await bot.send_message(event.chat_id, reply)

