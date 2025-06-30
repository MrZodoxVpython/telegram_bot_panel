from telegram_bot_panel import *
from telethon import events, Button
import datetime as DT
import os
import re
import subprocess

data_update = {}

CONFIG_PATH = "/etc/xray/config.json"

def parse_accounts_from_config():
    if not os.path.exists(CONFIG_PATH):
        return []

    with open(CONFIG_PATH, "r") as f:
        content = f.read()

    pattern = r"#\!\s+([^\s]+)\s+(\d{4}-\d{2}-\d{2})\n\},\{\s*\"password\":\s*\"([^\"]+)\",\s*\"email\":\s*\"([^\"]+)\""
    return list(re.finditer(pattern, content))


@bot.on(events.CallbackQuery(data=b"trojan/update_trojan"))
async def update_trojan(event):
    chat = event.chat_id
    sender = await event.get_sender()

    if valid(str(sender.id)) != "true":
        await event.answer("Akses ditolak!", alert=True)
        return

    accounts = parse_accounts_from_config()
    if not accounts:
        await event.respond("❌ Tidak ada akun Trojan ditemukan.")
        return

    msg = "🔧 Pilih akun yang ingin diperbarui:\n\n"
    buttons = []
    for match in accounts:
        uname = match.group(1)
        exp = match.group(2)
        buttons.append([Button.inline(f"{uname} (exp: {exp})", f"edit:{uname}".encode())])

    await bot.send_message(chat, msg, buttons=buttons)


@bot.on(events.CallbackQuery(pattern=b"edit:(.+)"))
async def edit_trojan(event):
    username = event.pattern_match.group(1).decode()
    chat = event.chat_id
    data_update[chat] = {"username": username}

    async with bot.conversation(chat) as conv:
        await conv.send_message("📆 Masukkan masa aktif tanggal baru (YYYY-MM-DD) atau renew(hari):")
        expired_raw = (await conv.wait_event(events.NewMessage(from_users=chat))).raw_text.strip()

        accounts = parse_accounts_from_config()
        old_expired = None
        for acc in accounts:
            if acc.group(1) == username:
                old_expired = DT.datetime.strptime(acc.group(2), "%Y-%m-%d")
                break

        try:
            if expired_raw.isdigit():
                if old_expired:
                    expired = (old_expired + DT.timedelta(days=int(expired_raw))).strftime("%Y-%m-%d")
                else:
                    expired = (DT.datetime.now() + DT.timedelta(days=int(expired_raw))).strftime("%Y-%m-%d")
            else:
                expired = expired_raw
            data_update[chat]["expired"] = expired
        except:
            await conv.send_message("❌ Format tidak valid.")
            return

        await conv.send_message("🔐 Masukkan password/UUID baru:")
        password = (await conv.wait_event(events.NewMessage(from_users=chat))).raw_text.strip()
        data_update[chat]["password"] = password

    await apply_update(event)


def update_account_in_config(old_username, new_username, new_expired, new_password):
    with open(CONFIG_PATH, "r") as f:
        lines = f.readlines()

    pattern_comment = f"#! {old_username} "
    new_comment = f"#! {new_username} {new_expired}"
    new_json_line = f'}},{{"password": "{new_password}", "email": "{new_username}"'

    updated_lines = []
    skip_next = False
    for i, line in enumerate(lines):
        if pattern_comment in line:
            updated_lines.append(new_comment + "\n")
            if i + 1 < len(lines):
                updated_lines.append(new_json_line + "\n")
                skip_next = True
        elif skip_next:
            skip_next = False
            continue
        else:
            updated_lines.append(line)

    with open(CONFIG_PATH, "w") as f:
        f.writelines(updated_lines)


async def apply_update(event):
    chat = event.chat_id
    data = data_update.get(chat)
    if not data:
        await event.respond("❌ Data tidak ditemukan.")
        return

    update_account_in_config(
        old_username=data["username"],
        new_username=data["username"],  # jika ingin ubah username juga, ganti di sini
        new_expired=data["expired"],
        new_password=data["password"]
    )

    subprocess.call("systemctl restart xray", shell=True)
    await event.respond(f"✅ Akun `{data['username']}` berhasil diperbarui.", parse_mode="markdown")

