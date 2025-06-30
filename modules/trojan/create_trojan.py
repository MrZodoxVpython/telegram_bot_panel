#!/usr/bin/env python3

import os
import json
from datetime import datetime, timedelta

def hitung_expired(input_str):
    if input_str.isdigit():
        return (datetime.now() + timedelta(days=int(input_str))).strftime("%Y-%m-%d")
    return input_str

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

def main():
    print("=== CREATE TROJAN ACCOUNT ===")
    username = input("Username      : ").strip()
    expired_input = input("Expired (hari / yyyy-mm-dd): ").strip()
    password = input("Password (UUID): ").strip()

    config_path = "/etc/xray/config.json"
    domain_file = "/etc/xray/domain"
    tags = ["trojanws", "trojangrpc"]
    comment_prefix = "#! "
    expired = hitung_expired(expired_input)
    comment_line = f"{comment_prefix}{username} {expired}"
    json_line = f'{{"password": "{password}", "email": "{username}"}}'

    success = True
    for tag in tags:
        if not insert_to_tag(config_path, tag, comment_line, json_line):
            success = False

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

        output = f"""
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
        """
        print(output)
    else:
        print("❌ Gagal menambahkan akun ke salah satu tag.")

if __name__ == "__main__":
    main()

