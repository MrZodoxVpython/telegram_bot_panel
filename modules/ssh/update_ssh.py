from xolpanel import *

@bot.on(events.CallbackQuery(data=b"ssh/update_ssh"))
async def update_ssh(event):
    async def update_ssh_(event):
        import datetime as DT
        chat = event.chat_id
        sender = await event.get_sender()

        # Minta username lama
        async with bot.conversation(chat) as conv:
            await event.respond("🧑💻 Masukkan username SSH yang ingin diupdate:")
            response = await conv.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
            old_user = response.raw_text.strip()

        # Cek apakah user ada
        check_cmd = f"getent passwd {old_user}"
        try:
            subprocess.check_output(check_cmd, shell=True)
        except subprocess.CalledProcessError:
            await event.respond(f"❌ User `{old_user}` tidak ditemukan.")
            return

        # Pilih mode update
        async with bot.conversation(chat) as conv:
            await event.respond("⚙️ Pilih jenis update:", buttons=[
                [Button.inline("🔁 Perpanjang (renew)", b"renew"), Button.inline("🛠 Update Total", b"update_total")]
            ])
            res = await conv.wait_event(events.CallbackQuery)
            mode = res.data.decode("utf-8")

        # Jika renew
        if mode == "renew":
            # Minta jumlah hari untuk ditambahkan
            async with bot.conversation(chat) as conv:
                await event.respond("📅 Masukkan jumlah hari untuk ditambahkan:")
                response = await conv.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
                tambah_hari = int(response.raw_text.strip())

            # Ambil expired saat ini dari /etc/shadow
            try:
                shadow_line = subprocess.check_output(f"grep '^{old_user}:' /etc/shadow", shell=True).decode().strip()
                current_day_number = int(shadow_line.split(":")[7])
                base_date = DT.date(1970, 1, 1)
                current_exp_date = base_date + DT.timedelta(days=current_day_number)
                new_exp_date = current_exp_date + DT.timedelta(days=tambah_hari)
                expire_date = new_exp_date.strftime("%Y-%m-%d")
            except Exception as e:
                await event.respond(f"❌ Gagal membaca expired user: `{str(e)}`")
                return

            # Set tanggal expired baru
            try:
                subprocess.check_output(f"chage -E {expire_date} {old_user}", shell=True)
            except Exception as e:
                await event.respond(f"❌ Gagal atur expired: `{str(e)}`")
                return

            # Sukses perpanjang
            await event.respond(f"""
✅ SSH account berhasil diperpanjang:

👤 Username: `{old_user}`
📅 Expired baru: `{expire_date}`
            """, buttons=[[Button.inline("‹ Main Menu ›", b"menu")]])
            return

        # Jika update total
        # Minta username baru
        async with bot.conversation(chat) as conv:
            await event.respond(f"🆕 Masukkan username baru untuk `{old_user}` (atau ketik sama jika tidak diganti):")
            response = await conv.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
            new_user = response.raw_text.strip()

        # Minta password baru
        async with bot.conversation(chat) as conv:
            await event.respond("🔑 Masukkan password baru:")
            response = await conv.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
            new_pass = response.raw_text.strip()

        # Minta expired (hari atau format YYYY-MM-DD)
        async with bot.conversation(chat) as conv:
            await event.respond("📅 Masukkan jumlah hari expired (misal: 7) atau langsung tanggal (contoh: 2025-01-01):")
            response = await conv.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
            expired_input = response.raw_text.strip()

        # Ubah expired ke format tanggal jika perlu
        try:
            if "-" in expired_input:
                expire_date = expired_input
            else:
                days = int(expired_input)
                expire_date = (DT.date.today() + DT.timedelta(days=days)).strftime("%Y-%m-%d")
        except Exception as e:
            await event.respond(f"❌ Format tanggal tidak valid: `{str(e)}`")
            return

        # Rename user jika beda
        if new_user != old_user:
            try:
                subprocess.check_output(f"usermod -l {new_user} {old_user}", shell=True)
                subprocess.check_output(f"usermod -d /home/{new_user} -m {new_user}", shell=True)
            except Exception as e:
                await event.respond(f"❌ Gagal ganti username: `{str(e)}`")
                return
        else:
            new_user = old_user

        # Set password baru
        try:
            subprocess.run(f"echo '{new_user}:{new_pass}' | chpasswd", shell=True, check=True)
        except Exception as e:
            await event.respond(f"❌ Gagal ubah password: `{str(e)}`")
            return

        # Set tanggal expired
        try:
            subprocess.check_output(f"chage -E {expire_date} {new_user}", shell=True)
        except Exception as e:
            await event.respond(f"❌ Gagal atur expired: `{str(e)}`")
            return

        # Sukses update total
        await event.respond(f"""
✅ SSH account berhasil diupdate:

👤 Username: `{new_user}`
🔐 Password: `{new_pass}`
📅 Expired: `{expire_date}`
        """, buttons=[[Button.inline("‹ Main Menu ›", b"menu")]])

    sender = await event.get_sender()
    if valid(str(sender.id)) == "true":
        await update_ssh_(event)
    else:
        await event.answer("Access Denied", alert=True)

