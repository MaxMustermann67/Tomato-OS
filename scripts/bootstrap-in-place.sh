#!/usr/bin/env bash
set -Eeuo pipefail
if [[ "$(id -u)" -ne 0 ]]; then
  echo "Bitte mit sudo in der bestehenden Tomaten-OS-VM ausführen." >&2
  exit 1
fi
if [[ ! -e /etc/debian_version ]]; then
  echo "Dieses Update benötigt eine Debian-basierte Tomaten-OS-VM." >&2
  exit 1
fi
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends git ca-certificates curl network-manager-gnome xfce4-power-manager xfce4-settings librsvg2-common python3-gi gir1.2-gtk-3.0
install -d -m 0755 /var/lib/tomaten-os
# The updater applies only files from the owner's main branch.
if [[ ! -d /var/lib/tomaten-os/source/.git ]]; then
  git clone --depth 1 --branch main https://github.com/MaxMustermann67/Tomato-OS.git /var/lib/tomaten-os/source
fi
install -Dm755 /var/lib/tomaten-os/source/guest/tomaten-source-update.sh /usr/local/sbin/tomaten-source-update
/usr/local/sbin/tomaten-source-update
echo "Tomaten OS ist aktualisiert. Bitte einmal abmelden oder neu starten."
