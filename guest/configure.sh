#!/usr/bin/env bash
set -Eeuo pipefail
export DEBIAN_FRONTEND=noninteractive
cat > /etc/apt/sources.list <<'EOF'
deb http://deb.debian.org/debian trixie main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security trixie-security main contrib non-free non-free-firmware
deb http://deb.debian.org/debian trixie-updates main contrib non-free non-free-firmware
EOF
echo tomato-os > /etc/hostname
cat > /etc/hosts <<'EOF'
127.0.0.1 localhost
127.0.1.1 tomato-os
::1 localhost ip6-localhost ip6-loopback
EOF
apt-get update
apt-get install -y --no-install-recommends \
  systemd-sysv linux-image-amd64 grub-pc initramfs-tools \
  locales sudo ca-certificates curl gnupg \
  xorg xfce4 xfce4-terminal xfce4-whiskermenu-plugin thunar mousepad \
  lightdm lightdm-gtk-greeter network-manager firefox-esr \
  python3 python3-gi gir1.2-gtk-3.0 \
  fonts-noto-core fonts-noto-color-emoji adwaita-icon-theme \
  xdg-utils dbus-x11 unattended-upgrades
echo 'de_DE.UTF-8 UTF-8' > /etc/locale.gen
locale-gen
update-locale LANG=de_DE.UTF-8
ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime
cat > /etc/default/keyboard <<'EOF'
XKBMODEL="pc105"
XKBLAYOUT="de"
XKBVARIANT=""
XKBOPTIONS=""
BACKSPACE="guess"
EOF
install -d -m 0755 /usr/share/keyrings
curl -fsSL https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg \
  -o /usr/share/keyrings/brave-browser-archive-keyring.gpg
cat > /etc/apt/sources.list.d/brave-browser-release.list <<'EOF'
deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main
EOF
apt-get update
apt-get install -y --no-install-recommends brave-browser
update-alternatives --install /usr/bin/x-www-browser x-www-browser /usr/bin/brave-browser 200
install -Dm755 /root/tomato-build/firstboot.py /usr/local/bin/tomato-firstboot
install -Dm755 /root/tomato-build/tomato-desktop-init.sh /usr/local/bin/tomato-desktop-init
install -Dm644 /root/tomato-build/tomato-desktop-init.desktop /etc/xdg/autostart/tomato-desktop-init.desktop
install -Dm644 /root/tomato-build/mimeapps.list /etc/xdg/mimeapps.list
install -Dm755 /root/tomato-build/finish-setup.py /usr/local/sbin/tomato-finish-setup
install -Dm644 /root/tomato-build/firstboot.desktop /etc/xdg/autostart/tomato-firstboot.desktop
install -Dm644 /root/tomato-build/wallpaper.svg /usr/share/backgrounds/tomato.svg
install -Dm644 /root/tomato-build/lightdm.conf /etc/lightdm/lightdm.conf.d/50-tomato.conf
install -Dm644 /root/tomato-build/greeter.conf /etc/lightdm/lightdm-gtk-greeter.conf
install -Dm644 /root/tomato-build/gtk.css /etc/skel/.config/gtk-3.0/gtk.css
install -Dm644 /root/tomato-build/xfce4-panel.xml /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml
cat > /etc/lightdm/lightdm.conf.d/51-tomato-firstboot.conf <<'EOF'
[Seat:*]
autologin-user=tomato-setup
autologin-user-timeout=0
EOF
useradd --create-home --shell /bin/bash tomato-setup
passwd --delete tomato-setup
cat > /etc/sudoers.d/tomato-firstboot <<'EOF'
tomato-setup ALL=(root) NOPASSWD: /usr/local/sbin/tomato-finish-setup
EOF
chmod 0440 /etc/sudoers.d/tomato-firstboot
visudo -cf /etc/sudoers.d/tomato-firstboot
cat > /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF
cat > /etc/default/grub <<'EOF'
GRUB_DEFAULT=0
GRUB_TIMEOUT=2
GRUB_DISTRIBUTOR="Tomato OS"
GRUB_CMDLINE_LINUX_DEFAULT="quiet console=tty0 console=ttyS0,115200n8"
GRUB_CMDLINE_LINUX=""
GRUB_TERMINAL="console serial"
GRUB_SERIAL_COMMAND="serial --speed=115200"
EOF
systemctl enable NetworkManager lightdm
apt-get clean