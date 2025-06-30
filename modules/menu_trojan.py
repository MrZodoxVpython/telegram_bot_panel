from telegram_bot_panel import *
import requests

@bot.on(events.CallbackQuery(data=b'trojan'))
async def trojan(event):
    async def trojan_(event):
        inline = [
            [Button.inline("[ Trial Trojan ]", b"trojan/trial_trojan"),
             Button.inline("[ Create Trojan ]", b"trojan/create_trojan")],
            [Button.inline("[ Daftar User Trojan ]", b"trojan/read_trojan")],
            [Button.inline("[ Update Akun Trojan ]", b"trojan/update_trojan")],
            [Button.inline("[ Delete Trojan ]", b"trojan/delete_trojan"),
             Button.inline("[ Check Login Trojan ]", b"trojan/login_trojan")],
            [Button.inline("‹ Main Menu ›", b"menu")]
        ]

        z = requests.get("http://ip-api.com/json/?fields=country,region,city,timezone,isp").json()
        msg = f"""
**━━━━━━━━━━━━━━━━**
**⟨ TROJAN Menu ⟩**
**━━━━━━━━━━━━━━━━**
**» Service:** `Trojan`
**» Hostname/IP:** `{DOMAIN}`
**» ISP:** `{z["isp"]}`
**» Country:** `{z["country"]}`
**» 🤖@MrZodoxVpython**
**━━━━━━━━━━━━━━━━**
"""
        await event.edit(msg, buttons=inline)

    sender = await event.get_sender()
    a = valid(str(sender.id))
    if a == "true":
        await trojan_(event)
    else:
        await event.answer("Access Denied", alert=True)

