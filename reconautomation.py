import subprocess
import ipaddress
import re
import socket
from pathlib import Path

# User inputs site/ip address. The script cleans the specified url into the host port so it can be scanned

target = input("Enter a website or IP address: ").strip()

target = target.replace("https://", "").replace("http://", "").split("/")[0].strip()

# Validates that the target only has the specified character parameters, reducing bad inputs and shell issues

if not re.match(r'^[a-zA-Z0-9.\-]+$', target):
    print("[-] Invalid target.")
    raise SystemExit

is_ip = False
try:
    ipaddress.ip_address(target)
    is_ip = True
except ValueError:
    is_ip = False

output_dir = Path(target.replace(":", "_"))
output_dir.mkdir(exist_ok=True)

print(f"[+] Target: {target}")
print(f"[+] Output folder: {output_dir}")

#If target is an ip, try reverse DNS to find hostname. Resolves domains to an IP.

if is_ip:
    try:
        hostname = socket.gethostbyaddr(target)[0]
        print(f"[+] Reverse DNS: {hostname}")
    except socket.herror:
        print("[-] No reverse DNS found")
else:
    try:
        resolved_ip = socket.gethostbyname(target)
        print(f"[+] Resolved IP: {resolved_ip}")
    except socket.gaierror:
        print("[-] Could not resolve domain")

# Runs a full TCP port scan with Nmap and captures the output so open ports can be extracted.print(f"\n[+] Stage 1: full TCP port sweep on {target}\n")
stage1_cmd = f"nmap -p- --min-rate 1000 -T4 {target} -oG - | tee {output_dir / 'full_tcp_scan.txt'}"
stage1 = subprocess.run(stage1_cmd, shell=True, capture_output=True, text=True)

grepable_output = stage1.stdout
open_ports = []

for line in grepable_output.splitlines():
    if "Ports:" in line:
        ports_section = line.split("Ports: ", 1)[1]
        entries = ports_section.split(", ")
        for entry in entries:
            parts = entry.split("/")
            if len(parts) >= 2 and parts[1] == "open":
                open_ports.append(parts[0])

open_ports = sorted(set(open_ports), key=int)

if not open_ports:
    print("\n[-] No open TCP ports found.")
    raise SystemExit

ports_str = ",".join(open_ports)
print(f"\n[+] Open ports found: {ports_str}")

print(f"\n[+] Stage 2: service/version detection on open ports\n")
stage2_cmd = f"nmap -sC -sV -p {ports_str} {target} | tee {output_dir / 'detailed_scan.txt'}"
subprocess.run(stage2_cmd, shell=True)

# Runs enumeration steps for common services like SMB and HTTP if the ports are open

if "445" in open_ports:
    print(f"\n[+] Port 445 detected, running SMB enumeration\n")
    smb_cmd = f"smbclient -N -L {target} | tee {output_dir / 'smbclient.txt'}"
    subprocess.run(smb_cmd, shell=True)
else:
    print("\n[-] Port 445 not open, skipping SMB enumeration")

if "80" in open_ports or "443" in open_ports:
    http_ports = [p for p in open_ports if p in {"80", "443"}]
    http_str = ",".join(http_ports)
    print(f"\n[+] Web ports detected ({http_str}), running HTTP NSE scripts\n")
    http_cmd = f"nmap --script http-title,http-headers -p {http_str} {target} | tee {output_dir / 'http_info.txt'}"
    subprocess.run(http_cmd, shell=True)
else:
    print("\n[-] No web ports detected, skipping HTTP scripts")

print(f"\n[+] Finished scanning {target}")