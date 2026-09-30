#!/usr/bin/env bash
set -Eeuo pipefail
repo="https://github.com/MaxMustermann67/Tomato-OS.git"
source_dir=/var/lib/tomaten-os/source
state_dir=/var/lib/tomaten-os
exec 9>/run/tomaten-source-update.lock
flock -n 9 || exit 0
if [[ ! -d "$source_dir/.git" ]]; then
  install -d -m 0755 "$state_dir"
  git clone --depth 1 --branch main "$repo" "$source_dir"
else
  git -C "$source_dir" fetch --depth 1 origin main
  git -C "$source_dir" reset --hard FETCH_HEAD
fi
commit="$(git -C "$source_dir" rev-parse HEAD)"
if [[ -f "$state_dir/installed-commit" ]] && [[ "$(cat "$state_dir/installed-commit")" == "$commit" ]]; then
  exit 0
fi
bash "$source_dir/guest/tomaten-apply.sh" "$source_dir"
printf '%s\n' "$commit" > "$state_dir/installed-commit"
logger -t tomaten-source-update "Installed Tomaten OS source revision $commit"
