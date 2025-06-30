#!/usr/bin/env python3

import json
import os
import sys
from datetime import datetime, timedelta

# === Cek argumen ===
if len(sys.argv) < 4:
    print("❌ Gunakan: create_trojan.py username expired key")
    sys.exit(1)

username = sys.argv[1]
expired_input = sys.argv[2]
password = sys.argv[3]
config_path = "/etc/xray/config.json"
domain_file = "/etc/xray/domain"
tags = ["trojanws", "trojangrpc"]
comment_prefix = "#! "
comment_line = f"{comment_prefix}{username} {expired_input}"

# === Hitung tanggal expired ===
def hitung_expired(input_str):
    if input_str.isdigit():
        return (datetime.now() + timedelta(days=int(input_str))).strftime("%Y-%m-%d")
    return input_str

expired = hitung_expired(expired_input)

# === Fungsi untuk menyisipkan user ke config.json berdasarkan tag ===
def insert_to_tag(config_path, tag, comment, entry):
    if not os.path.exists(config_path):
        return False
    with open(config_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    inserted = False
    for i, line in enumerate(lines):
        new_lines.append(line.rstrip())
        if f"#{tag}" in line and not inserted:
            new_lines.append(comment)
            new_lines.append(entry)
            inserted = True

    if inserted:
        with open(config_path, 'w') as f:
            f.write('\n'.join(new_lines) + '\n')
    return inserted

# === JSON line untuk trojan ===
json_line = f'{{"password": "{password}", "email": "{username}"}}'

# === Tambahkan ke config.json ===
success = True
for tag in tags:
    if not insert_to_tag(config_path, tag, comment_line, json_line):
        success = False

# === Restart Xray dan tampilkan hasil ===
if success:
    os.system("systemctl restart xray")

    try:
        with open(domain_file) as f:
            domain = f.read().strip()
    except:
        domain = "yourdomain.com"

    tls = "443"
    ntls = "80"
    path = "/trojan-ws"
    grpc_service = "trojan-grpc"

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           TROJAN ACCOUNT          
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Remarks        : {username}
Host/IP        : {domain}
Wildcard       : (bug.com).{domain}
Port TLS       : {tls}
Port non-TLS   : {ntls}
Port gRPC      : {tls}
Password       : {password}
Path           : {path}
ServiceName    : {grpc_service}
Expired On     : {expired}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Link TLS       : trojan://{password}@{domain}:{tls}?path={path}&security=tls&type=ws#{username}
Link non-TLS   : trojan://{password}@{domain}:{ntls}?path={path}&security=none&type=ws#{username}
Link gRPC      : trojan://{password}@{domain}:{tls}?mode=gun&security=tls&type=grpc&serviceName={grpc_service}#{username}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
else:
    print("❌ Gagal menambahkan akun ke salah satu tag.")

