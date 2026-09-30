# Tomato OS

Tomato OS ist ein Debian-basiertes Desktop-System für VirtualBox auf x86-64. Die erste Version enthält eine deutschsprachige XFCE-Oberfläche im Tomato-Design, Netzwerk über DHCP, Brave als Standardbrowser, Firefox ESR, Sicherheitsupdates und eine Ersteinrichtung für ein persönliches Benutzerkonto.

## OVA herunterladen und starten

1. Öffne unter **Actions** den neuesten erfolgreichen Lauf von **Build Tomato OS OVA**.
2. Lade das Artefakt **Tomato-OS-OVA** herunter und entpacke die ZIP-Datei.
3. Starte unter Windows per Doppelklick **Tomato-OS-installieren.cmd**. Das Skript importiert die OVA mit VBoxManage, aktiviert NAT-Netzwerk und startet die VM. VirtualBox muss auf dem PC installiert sein.
4. Beim ersten Start legst du deinen Benutzernamen und dein Passwort fest. Danach startet das System neu und zeigt die Anmeldung.

Falls das Skript nicht ausgeführt werden kann, öffne VirtualBox und wähle **Datei → Appliance importieren → Tomato-OS.ova**. Die VM ist für 4 GB RAM und 2 CPU-Kerne ausgelegt; die virtuelle Festplatte hat maximal 16 GB.

VirtualBox sollte NAT als Netzwerkadapter verwenden. Brave und Firefox ESR findest du im Anwendungsmenü. Die OVA enthält absichtlich kein vorgegebenes dauerhaftes Benutzerpasswort.

## OVA lokal bauen

Benötigt wird ein x86-64-Debian/Ubuntu-Buildhost mit Root-Rechten, Internet, etwa 20 GB freiem Speicher und den Paketen:

    sudo apt-get install debootstrap parted qemu-utils grub-pc-bin grub2-common e2fsprogs
    sudo bash scripts/build-ova.sh

Das Ergebnis liegt in dist/Tomato-OS.ova, die SHA-256-Prüfsumme in dist/Tomato-OS.ova.sha256. Das Build-Skript erzeugt eine MBR/ext4-Festplatte, installiert Debian Stable (Trixie), richtet die Oberfläche und Programme ein und verpackt eine OVF-Beschreibung mit VMDK als OVA.

## Grenzen der ersten Version

Die Oberfläche nutzt XFCE als Fensterverwaltung und Desktop-Unterbau. Tomato OS bringt ein eigenes Branding, eine angepasste Leiste, eine GTK-Ersteinrichtung und eine gestaltete Anmeldung mit. Eine vollständig neu geschriebene Desktop-Shell ist noch nicht enthalten. Die OVA wird im GitHub-Actions-Workflow gebaut; ein erfolgreicher Workflow ersetzt keinen manuellen Funktionstest in VirtualBox.