from telegram_bot_panel import *
from telethon import events, Button
import os
import re
import subprocess

CONFIG_PATH = "/etc/xray/config.json"

def parse_accounts():
    if not os.path.exists(CONFIG_PATH):
        return []

    with open(CONFIG_PATH, "r") as f:
        content = f.read()

    # Cocokkan komentar + akun json
    pattern = r"#\!\s+([^\s]+)\s+(\d{4}-\d{2}-\d{2})\n\},\{\s*\"password\":\s*\"([^\"]+)\",\s*\"email\":\s*\"([^\"]+)"
    return list(re.finditer(pattern, content))

def delete_account_from_config(username):
    with open(CONFIG_PATH, "r") as f:
        lines = f.readlines()

    new_lines = []
    skip_next = False
    deleted = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"#! {username} "):
            skip_next = True
            deleted = True
            continue
        if skip_next:
            skip_next = False
            continue
        new_lines.append(line)

    if deleted:
        with open(CONFIG_PATH, "w") as f:
            f.writelines(new_lines)
        subprocess.call("systemctl restart xray", shell=True)

    return deleted

@bot.on(events.CallbackQuery(data=b"trojan/delete_trojan"))
async def delete_trojan(event):
    chat = event.chat_id
    sender = await event.get_sender()

    if valid(str(sender.id)) != "true":
        await event.answer("Akses ditolak!", alert=True)
        return

    accounts = parse_accounts()
    if not accounts:
        await event.respond("❌ Tidak ada akun Trojan ditemukan.")
        return

    msg = "🗑 Pilih akun yang ingin dihapus:\n\n"
    buttons = []
    for acc in accounts:
        uname = acc.group(1)
        exp = acc.group(2)
        buttons.append([Button.inline(f"{uname} (exp: {exp})", f"hapus:{uname}".encode())])

    await bot.send_message(chat, msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"hapus:(.+)"))
async def confirm_delete(event):
    username = event.pattern_match.group(1).decode()
    chat = event.chat_id

    async with bot.conversation(chat) as conv:
        await conv.send_message(f"⚠️ Konfirmasi hapus akun `{username}`?\nKetik `YA` untuk konfirmasi.")
        msg = await conv.wait_event(events.NewMessage(from_users=chat))
        if msg.raw_text.strip().upper() == "YA":
            if delete_account_from_config(username):
                await conv.send_message(f"✅ Akun `{username}` berhasil dihapus.", parse_mode="markdown")
            else:
                await conv.send_message("❌ Gagal menghapus akun. Mungkin akun tidak ditemukan.")
        else:
            await conv.send_message("❎ Penghapusan dibatalkan.")

