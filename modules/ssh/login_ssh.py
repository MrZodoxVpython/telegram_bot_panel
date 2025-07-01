from telegram_bot_panel import bot
from telethon import events, Button
import subprocess
import pwd
import re

@bot.on(events.CallbackQuery(data=b"trojan/login_ssh"))
async def login_ssh(event):
    try:
        sender = await event.get_sender()
        if valid(str(sender.id)) != "true":
            await event.answer("Akses ditolak!", alert=True)
            return

        # Jalankan netstat untuk koneksi SSH (port 22)
        cmd = "ss -tnp | grep ':22 '"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if not result.stdout.strip():
            await bot.send_message(event.chat_id, "❌ Tidak ada koneksi SSH aktif saat ini.",
                                   buttons=[Button.inline("🔙 Back to Menu", b"menu")])
            return

        # Ambil user dari /etc/passwd
        uid_user_map = {p.pw_uid: p.pw_name for p in pwd.getpwall() if int(p.pw_uid) >= 1000 and "/home" in p.pw_dir}

        msg = "📡 **Login SSH Aktif Saat Ini**\n━━━━━━━━━━━━━━━━━━━━━━━\n"
        lines = result.stdout.strip().splitlines()
        seen = set()
        no = 1

        for line in lines:
            match = re.search(r'pid=(\d+),fd=\d+\)\)', line)
            if not match:
                continue
            pid = int(match.group(1))

            # Cek UID pemilik PID
            try:
                proc_uid = int(subprocess.check_output(["stat", "-c", "%u", f"/proc/{pid}"], text=True).strip())
                username = uid_user_map.get(proc_uid, "unknown")
            except Exception:
                username = "unknown"

            # Ambil IP sumber dan port
            match_info = re.search(r'src\s+(\S+):(\d+)\s+dst\s+(\S+):(\d+)', line)
            if match_info:
                src_ip, src_port, dst_ip, dst_port = match_info.groups()
            else:
                continue

            identifier = (username, src_ip, dst_port, pid)
            if identifier in seen:
                continue
            seen.add(identifier)

            msg += f"{no:02d}. `{username}` | IP: `{src_ip}` | Port: `{dst_port}` | PID: `{pid}`\n"
            no += 1

        msg += "━━━━━━━━━━━━━━━━━━━━━━━"
        await bot.send_message(
            event.chat_id,
            msg,
            parse_mode="markdown",
            buttons=[Button.inline("🔙 Back to Menu", b"menu")]
        )

    except Exception as e:
        await bot.send_message(event.chat_id, f"❌ Terjadi kesalahan:\n`{str(e)}`",
                               parse_mode="markdown",
                               buttons=[Button.inline("🔙 Back to Menu", b"menu")])
