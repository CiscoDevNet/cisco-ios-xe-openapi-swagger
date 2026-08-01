#!/usr/bin/env python3
"""SSH into C9300 and run show commands for each cli-reference.md section.
Outputs a JSON map: { "section_number": { "command": "output" } }
"""

import paramiko
import json
import re
import time
import sys
import os

# Device connection details are read from environment variables so no
# credentials are stored in the bundle. Set these before running:
#   export MDT_HOST=your-switch.example.com
#   export MDT_USER=admin
#   export MDT_PASS=...   (or leave unset to be prompted)
HOST = os.environ.get("MDT_HOST", "")
USER = os.environ.get("MDT_USER", "admin")
PASS = os.environ.get("MDT_PASS", "")
CLI_REF = "cli-reference.md"
OUTPUT_FILE = "cli-outputs.json"
MAX_LINES_PER_CMD = 60


def parse_show_commands(filepath):
    """Parse cli-reference.md and extract show commands per section."""
    sections = {}
    current_section = None
    in_cli_section = False
    in_code_block = False
    commands = []

    with open(filepath, "r") as f:
        for line in f:
            heading = re.match(r"^## (\d+)\.\s+(.+)", line)
            if heading:
                if current_section and commands:
                    sections[current_section] = list(commands)
                current_section = int(heading.group(1))
                commands = []
                in_cli_section = False
                in_code_block = False
                continue

            if "### CLI Show Commands" in line:
                in_cli_section = True
                in_code_block = False
                continue

            if in_cli_section and line.strip() == "```" and not in_code_block:
                in_code_block = True
                continue

            if in_cli_section and in_code_block:
                if line.strip() == "```":
                    in_code_block = False
                    in_cli_section = False
                    continue
                cmd = line.strip()
                if cmd and cmd.startswith("show "):
                    commands.append(cmd)
                continue

            if line.startswith("### ") and "CLI Show Commands" not in line:
                in_cli_section = False
                in_code_block = False

    if current_section and commands:
        sections[current_section] = list(commands)

    return sections


def send_command(shell, cmd, wait=3):
    """Send a command and collect output until prompt returns."""
    # Drain any leftover
    while shell.recv_ready():
        shell.recv(65536)

    shell.send(cmd + "\n")
    time.sleep(wait)

    # Collect output — keep reading until no more data
    output = b""
    retries = 0
    while retries < 4:
        if shell.recv_ready():
            chunk = shell.recv(65536)
            output += chunk
            retries = 0
            time.sleep(0.3)
        else:
            retries += 1
            time.sleep(0.5)

    decoded = output.decode("utf-8", errors="replace")
    lines = decoded.splitlines()

    # Remove command echo (first line) and trailing prompt (last line)
    if lines and cmd in lines[0]:
        lines = lines[1:]
    if lines and re.match(r"^[\w\-\.]+#\s*$", lines[-1]):
        lines = lines[:-1]

    return "\n".join(lines).strip()


def ssh_run_commands(host, user, password, sections):
    """SSH into device and run each show command."""
    results = {}

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"  Connecting to {host}...")
    client.connect(host, username=user, password=password, timeout=30,
                   look_for_keys=False, allow_agent=False)

    shell = client.invoke_shell(width=200, height=1000)
    time.sleep(2)
    shell.recv(65536)  # clear banner

    # Disable paging
    send_command(shell, "terminal length 0", wait=1)
    # Disable timestamps that could add noise
    send_command(shell, "terminal width 200", wait=1)

    total_commands = sum(len(cmds) for cmds in sections.values())
    done = 0

    for section_num in sorted(sections.keys()):
        commands = sections[section_num]
        results[str(section_num)] = {}

        for cmd in commands:
            done += 1
            sys.stdout.write(f"\r  [{done}/{total_commands}] §{section_num}: {cmd:<75}")
            sys.stdout.flush()

            # Longer commands like 'show ip cef' can take time
            wait_time = 4 if any(k in cmd for k in ["interfaces", "cef", "mac address",
                                                      "access-list", "ip route"]) else 3
            raw_output = send_command(shell, cmd, wait=wait_time)

            # Truncate to MAX_LINES_PER_CMD
            output_lines = raw_output.splitlines()
            if len(output_lines) > MAX_LINES_PER_CMD:
                raw_output = "\n".join(output_lines[:MAX_LINES_PER_CMD]) + \
                    f"\n... ({len(output_lines) - MAX_LINES_PER_CMD} more lines truncated)"

            results[str(section_num)][cmd] = raw_output

    print()  # newline after progress
    shell.close()
    client.close()
    return results


def main():
    global HOST, PASS
    if not HOST:
        HOST = input("Switch hostname/IP: ").strip()
    if not PASS:
        import getpass
        PASS = getpass.getpass(f"Password for {USER}@{HOST}: ")

    print("Parsing cli-reference.md for show commands...")
    sections = parse_show_commands(CLI_REF)
    total = sum(len(v) for v in sections.values())
    print(f"Found {len(sections)} sections with {total} commands total\n")

    print(f"Running commands on {HOST} via SSH...")
    results = ssh_run_commands(HOST, USER, PASS, sections)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved results to {OUTPUT_FILE}")

    # Summary
    empty = sum(1 for s in results.values() for o in s.values() if not o.strip())
    print(f"Sections: {len(results)} | Commands: {total} | Empty responses: {empty}")


if __name__ == "__main__":
    main()
