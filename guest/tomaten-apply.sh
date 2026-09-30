#!/usr/bin/env bash
set -Eeuo pipefail
source_dir="${1:?Repository path required}"
test "$(id -u)" -eq 0
test -f "$source_dir/guest/tomaten-shell.py"
install -Dm755 "$source_dir/guest/tomaten-shell.py" /usr/local/bin/tomaten-shell
install -Dm755 "$source_dir/guest/tomaten-session" /usr/local/bin/tomaten-session
install -Dm644 "$source_dir/guest/tomaten.desktop" /usr/share/xsessions/tomaten.desktop
install -Dm755 "$source_dir/guest/tomato-desktop-init.sh" /usr/local/bin/tomato-desktop-init
install -Dm644 "$source_dir/guest/tomato-desktop-init.desktop" /etc/xdg/autostart/tomato-desktop-init.desktop
install -Dm644 "$source_dir/guest/mimeapps.list" /etc/xdg/mimeapps.list
install -Dm644 "$source_dir/guest/wallpaper.svg" /usr/share/backgrounds/tomato.svg
install -Dm644 "$source_dir/guest/lightdm.conf" /etc/lightdm/lightdm.conf.d/50-tomato.conf
install -Dm644 "$source_dir/guest/greeter.conf" /etc/lightdm/lightdm-gtk-greeter.conf
install -Dm644 "$source_dir/guest/gtk.css" /etc/skel/.config/gtk-3.0/gtk.css
install -Dm755 "$source_dir/guest/tomaten-source-update.sh" /usr/local/sbin/tomaten-source-update
install -Dm644 "$source_dir/guest/tomaten-source-update.service" /etc/systemd/system/tomaten-source-update.service
install -Dm644 "$source_dir/guest/tomaten-source-update.timer" /etc/systemd/system/tomaten-source-update.timer
install -Dm755 "$source_dir/guest/tomaten-update.sh" /usr/local/sbin/tomaten-update
install -Dm644 "$source_dir/guest/tomaten-update.service" /etc/systemd/system/tomaten-update.service
install -Dm644 "$source_dir/guest/tomaten-update.timer" /etc/systemd/system/tomaten-update.timer
# Select the new session for accounts already created in older images.
while IFS=: read -r name _ uid _ _ home _; do
  if (( uid >= 1000 )) && [[ "$name" != "tomato-setup" && -d "$home" ]]; then
    printf '[Desktop]\nSession=tomaten\n' > "$home/.dmrc"
    chown "$name:$name" "$home/.dmrc"
    chmod 0644 "$home/.dmrc"
  fi
done < /etc/passwd
systemctl daemon-reload
systemctl enable --now tomaten-source-update.timer
systemctl enable --now tomaten-update.timer
