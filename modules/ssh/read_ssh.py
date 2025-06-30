from telegram_bot_panel import *

@bot.on(events.CallbackQuery(data=b"ssh/read_ssh"))
async def show_ssh(event):
    async def show_ssh_(event):
        cmd = "awk -F: '($3>=1000)&&($1!=\"nobody\"){print $1}' /etc/passwd"
        try:
            output = subprocess.check_output(cmd, shell=True).decode("utf-8").strip().splitlines()
        except Exception as e:
            await event.respond(f"❌ Error membaca user SSH:\n`{str(e)}`")
            return

        accounts = [f"`{u.strip()}`" for u in output if u.strip()]
        userlist = "\n".join(accounts)
        total = len(accounts)

        msg = f"""
**📋 Showing All SSH Users**

{userlist}
`
**Total SSH Account:** `{total}`
"""

        await event.respond(msg, buttons=[[Button.inline("‹ Main Menu ›", b"menu")]])

    sender = await event.get_sender()
    if valid(str(sender.id)) == "true":
        await show_ssh_(event)
    else:
        await event.answer("Access Denied", alert=True)

