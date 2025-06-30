from telegram_bot_panel import *

@bot.on(events.CallbackQuery(data=b'xray'))
async def xray_menu(event):
    sender = await event.get_sender()
    val = valid(str(sender.id))

    if val == "false":
        try:
            await event.answer("Akses Ditolak", alert=True)
        except:
            await event.reply("Akses Ditolak")
    elif val == "true":
        inline = [
            [Button.inline("[ SSH menu ]", b"ssh")],
            [Button.inline("[ TROJAN menu ]", b"trojan")],
            [Button.inline("← Back to Menu", b"menu")]
        ]

        msg = f"""
**━━━━━━━━━━━━━━━━**
**⟨ 👨‍💻Xray Menu ⟩**
**━━━━━━━━━━━━━━━━**
**» 🤖Bot Version:** `v2.0`
**» 🤖Running Since:** `{uptime}`
**━━━━━━━━━━━━━━━━**
"""
        x = await event.edit(msg, buttons=inline)
        if not x:
            await event.reply(msg, buttons=inline)
