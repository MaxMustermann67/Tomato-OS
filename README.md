# Tomaten OS

Tomaten OS ist ein Linux-basiertes Desktop-System für VirtualBox auf Windows mit AMD/Intel x86-64. Die Oberfläche ist vom dunklen Rot-Schwarz-Stil der Referenz inspiriert: Statusleiste, seitliche Programmstarter, Dock und geometrischer Hintergrund. Ein Willkommensfenster startet nicht. Bei der ersten Nutzung wird lediglich ein Benutzerkonto mit Passwort angelegt.

Brave ist Standardbrowser; Firefox ESR ist ebenfalls installiert. Netzwerk läuft über DHCP und VirtualBox-NAT.

## Auf Windows starten

1. Unter **Actions** das neueste erfolgreiche Artefakt **Tomaten-OS-OVA** herunterladen.
2. Die ZIP-Datei vollständig entpacken.
3. **Tomaten-OS-installieren.cmd** per Doppelklick starten. Die Datei importiert **Tomaten-OS.ova** als eigene VM mit einer Versionskennung und öffnet sie. Vorhandene VMs bleiben erhalten.
4. Beim ersten Start Benutzernamen und Passwort anlegen.

VirtualBox muss bereits installiert sein. Falls die Startdatei nicht ausgeführt werden kann, in VirtualBox **Datei → Appliance importieren → Tomaten-OS.ova** wählen. Der Import ist auf 4 GB RAM, 2 CPU-Kerne und ein dynamisch wachsendes Laufwerk mit maximal 16 GB ausgelegt.

## Updates

Ein Systemd-Timer prüft nach dem Start und danach etwa alle zwölf Stunden Debian- und Brave-Pakete. Sicherheitsupdates werden zusätzlich über Debian unattended-upgrades geprüft. Ein erforderlicher Neustart erfolgt nicht ohne den Benutzer.

Der GitHub-Actions-Workflow baut bei Änderungen und montags ein aktuelles OVA-Artefakt. GitHub-Artefakte verfallen nach 14 Tagen. Änderungen an der Tomaten-Oberfläche in einer neuen OVA werden nicht automatisch in eine bereits importierte VM übertragen; für diese Version muss die neue OVA importiert werden. Eine vorhandene VM und ihre Daten werden nicht überschrieben.

## Lokal bauen

Ein x86-64-Debian/Ubuntu-Buildhost mit Root-Rechten, Internet und etwa 20 GB freiem Speicher benötigt:

    sudo apt-get install debootstrap parted qemu-utils grub-pc-bin grub2-common e2fsprogs
    sudo bash scripts/build-ova.sh

Die OVA und ihre SHA-256-Prüfsumme entstehen im Verzeichnis dist. Der Build installiert Debian Stable (Trixie), Brave, Firefox ESR und die Tomaten-Sitzung auf einer BIOS/MBR-Festplatte. Der CI-Lauf prüft Syntax, den GTK-Start unter Xvfb, die OVA-Prüfsumme und den Linux-Boot in QEMU.

## Technische Grenze

Tomaten OS nutzt XFWM und xfdesktop als Fensterverwaltung und Desktop-Unterbau. Die Leisten und Starter sind eine eigene GTK-Oberfläche. Die Windows-Startdatei wurde nicht auf dem Rechner des Nutzers ausgeführt; ein manueller Importtest in dessen VirtualBox steht aus.