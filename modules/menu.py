from telegram_bot_panel import *

@bot.on(events.NewMessage(pattern=r"(?:/menu)$"))
@bot.on(events.CallbackQuery(data=b'menu'))
async def menu(event):
	inline = [
[Button.inline("[ XRAY Menu ]","xray"),
Button.inline("[ Check VPS Info ]","info")],
[Button.url("[ GitHub Repo ]","https://github.com/MrZodoxVpython"),
Button.url("[ Telegram Channel ]","https://t.me/MrZodoxVpython")]]
	sender = await event.get_sender()
	val = valid(str(sender.id))
	if val == "false":
		try:
			await event.answer("Akses Ditolak", alert=True)
		except:
			await event.reply("Akses Ditolak")
	elif val == "true":
		msg = f"""
**━━━━━━━━━━━━━━━━**
**⟨ 👨‍💻Admin Panel Menu ⟩**
**━━━━━━━━━━━━━━━━**
**» 🤖Bot Version:** `v2.0`
**» 🤖Running Since:** `{uptime}`
**━━━━━━━━━━━━━━━━**
"""
		x = await event.edit(msg,buttons=inline)
		if not x:
			await event.reply(msg,buttons=inline)
