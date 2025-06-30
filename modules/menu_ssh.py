from xolpanel import *

@bot.on(events.CallbackQuery(data=b'ssh'))
async def ssh(event):
	async def ssh_(event):
		inline = [
[Button.inline("[ Trial SSH ]", b"ssh/trial_ssh"),
Button.inline("[ Create SSH ]", b"ssh/create_ssh")],
[Button.inline("[ Daftar User SSH ]", b"ssh/read_ssh")],
[Button.inline("[ Update Akun SSH ]", b"ssh/update_ssh")],
[Button.inline("[ Delete SSH ]", b"ssh/delete_ssh"),
Button.inline("[ Check Login SSH ]", b"ssh/login_ssh")],
[Button.inline("‹ Main Menu ›", b"menu")]]
		z = requests.get(f"http://ip-api.com/json/?fields=country,region,city,timezone,isp").json()
		msg = f"""
**━━━━━━━━━━━━━━━━**
**⟨ SSH Menu ⟩**
**━━━━━━━━━━━━━━━━**
**» Service:** `SSH`
**» Hostname/IP:** `{DOMAIN}`
**» ISP:** `{z["isp"]}`
**» Country:** `{z["country"]}`
**» 🤖@MrZodoxVpython**
**━━━━━━━━━━━━━━━━**
"""
		await event.edit(msg,buttons=inline)
	sender = await event.get_sender()
	a = valid(str(sender.id))
	if a == "true":
		await ssh_(event)
	else:
		await event.answer("Access Denied",alert=True)
