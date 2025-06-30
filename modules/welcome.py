from telegram_bot_panel import *
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
	await event.reply("Selamat datang di Bot Tokomard!")
