# ReconPilot

ReconPilot is a Python-based reconnaissance automation tool that streamlines the early stages of network enumeration for authorized lab, CTF, and educational environments.

It accepts a domain or IP address as input, performs target validation and cleanup, runs a full TCP port sweep with Nmap, identifies open ports, and automatically launches follow-up enumeration steps based on detected services.

The goal of this project is to reduce repetitive manual recon steps and create a more structured, repeatable workflow for beginner network enumeration.

---

## Features

- Cleans and validates user-provided targets (domain or IP)
- Supports both hostname and IP-based targets
- Resolves:
  - **Forward DNS** for domains
  - **Reverse DNS** for IP addresses
- Runs a **full TCP port sweep** using Nmap
- Parses grepable Nmap output to extract open ports
- Automatically runs **service/version detection** on discovered ports
- Performs **conditional service-specific enumeration**:
  - **SMB enumeration** when port `445` is open
  - **HTTP title/header enumeration** when ports `80` or `443` are open
- Saves scan outputs into a dedicated folder per target for organized reporting

---

## How It Works

ReconPilot follows a staged recon workflow:

1. **Input & Validation**
   - Accepts a domain or IP address from the user
   - Removes protocol prefixes such as `http://` or `https://`
   - Validates the cleaned target to reduce malformed input and shell issues

2. **Target Resolution**
   - If the target is an IP:
     - Attempts reverse DNS lookup
   - If the target is a domain:
     - Resolves the domain to an IP address

3. **Stage 1 – Full TCP Port Sweep**
   - Runs a full TCP scan with Nmap:
     ```bash
     nmap -p- --min-rate 1000 -T4 <target>
     ```
   - Captures grepable output and extracts open ports automatically

4. **Stage 2 – Detailed Enumeration**
   - Runs:
     ```bash
     nmap -sC -sV -p <open_ports> <target>
     ```
   - Uses default NSE scripts and version detection for identified ports

5. **Conditional Follow-Up Enumeration**
   - If port `445` is open:
     - Runs SMB share enumeration with:
       ```bash
       smbclient -N -L <target>
       ```
   - If ports `80` or `443` are open:
     - Runs HTTP-focused NSE scripts:
       ```bash
       nmap --script http-title,http-headers -p 80,443 <target>
       ```

---

## Requirements

Make sure the following tools are installed on your system:

- Python 3.8+
- Nmap
- smbclient (for SMB enumeration)

### Python Standard Library Modules Used

No external Python packages are required. This script uses:

- `subprocess`
- `ipaddress`
- `re`
- `socket`
- `pathlib`

---

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/reconpilot.git
cd reconpilot
