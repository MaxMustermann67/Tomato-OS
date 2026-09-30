#!/bin/sh
# Apply the Tomato wallpaper once for each new user, then leave personal changes alone.
marker="$HOME/.config/tomato/desktop-initialized"
[ -e "$marker" ] && exit 0
wallpaper=/usr/share/backgrounds/tomato.svg
attempt=0
properties=""
while [ "$attempt" -lt 15 ]; do
  properties="$(xfconf-query -c xfce4-desktop -lv 2>/dev/null | awk '$1 ~ /\/(last-image|image-path)$/ {print $1}')"
  [ -n "$properties" ] && break
  attempt=$((attempt + 1))
  sleep 1
done
if [ -n "$properties" ]; then
  printf '%s\n' "$properties" | while IFS= read -r property; do
    xfconf-query -c xfce4-desktop -p "$property" -s "$wallpaper" || exit 1
  done
else
  xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-path \
    -n -t string -s "$wallpaper" || exit 1
fi
mkdir -p "$HOME/.config/tomato"
touch "$marker"