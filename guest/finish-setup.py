#!/usr/bin/env python3
"""Privileged, one-time local account creation for the first boot wizard."""
import json
import os
import pwd
import re
import subprocess
import sys
from pathlib import Path

AUTLOGIN = Path("/etc/lightdm/lightdm.conf.d/51-tomato-firstboot.conf")
SUDOERS = Path("/etc/sudoers.d/tomato-firstboot")

def main():
    if os.geteuid() != 0 or os.environ.get("SUDO_USER") != "tomato-setup":
        raise ValueError("Nur die Tomato-Ersteinrichtung darf ein Konto anlegen.")
    if not AUTLOGIN.exists():
        raise ValueError("Die Ersteinrichtung ist bereits abgeschlossen.")
    data = json.load(sys.stdin)
    name = data.get("username", "")
    password = data.get("password", "")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{2,31}", name):
        raise ValueError("Benutzername: 3–32 Kleinbuchstaben, Ziffern, _ oder -.")
    if not isinstance(password, str) or len(password) < 8 or "\n" in password or "\r" in password:
        raise ValueError("Das Passwort braucht mindestens 8 Zeichen.")
    try:
        pwd.getpwnam(name)
    except KeyError:
        pass
    else:
        raise ValueError("Dieser Benutzername ist bereits vergeben.")
    subprocess.run(["useradd", "--create-home", "--shell", "/bin/bash",
                    "--groups", "sudo,adm,audio,video,plugdev", name], check=True)
    try:
        subprocess.run(["chpasswd"], input=f"{name}:{password}\n",
                       text=True, check=True, capture_output=True)
    except Exception:
        subprocess.run(["userdel", "--remove", name], check=False)
        raise
    AUTLOGIN.unlink()
    SUDOERS.unlink()
    subprocess.run(["usermod", "--lock", "--shell", "/usr/sbin/nologin",
                    "tomato-setup"], check=True)
    subprocess.run(["systemctl", "reboot"], check=True)

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)