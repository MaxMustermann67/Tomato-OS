#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/dist"
WORK="$ROOT/.build"
MNT="$WORK/rootfs"
RAW="$WORK/tomato.raw"
LOOP=""
if [ "$EUID" -ne 0 ]; then
  echo "Run this script with sudo on a Debian/Ubuntu x86-64 host." >&2
  exit 1
fi
for cmd in debootstrap parted losetup mkfs.ext4 grub-install qemu-img python3; do
  command -v "$cmd" >/dev/null || { echo "Missing command: $cmd" >&2; exit 1; }
done
cleanup() {
  if mountpoint -q "$MNT"; then umount -R "$MNT" || true; fi
  if [ -n "$LOOP" ]; then losetup -d "$LOOP" || true; fi
}
trap cleanup EXIT
mkdir -p "$OUT" "$MNT"
rm -f "$RAW" "$OUT/Tomato-OS.ova" "$OUT/Tomato-OS-disk1.vmdk"
truncate -s 16G "$RAW"
parted -s "$RAW" mklabel msdos mkpart primary ext4 1MiB 100% set 1 boot on
LOOP="$(losetup --find --show --partscan "$RAW")"
udevadm settle
PART="$LOOP"p1
mkfs.ext4 -F -L TOMATO_ROOT "$PART"
mount "$PART" "$MNT"
debootstrap --arch=amd64 --variant=minbase trixie "$MNT" http://deb.debian.org/debian
cp -L /etc/resolv.conf "$MNT/etc/resolv.conf"
cat > "$MNT/etc/fstab" <<EOF
UUID=$(blkid -s UUID -o value "$PART") / ext4 defaults,noatime 0 1
EOF
cp -a "$ROOT/guest" "$MNT/root/tomato-build"
mount --rbind /dev "$MNT/dev"
mount --make-rslave "$MNT/dev"
mount -t proc proc "$MNT/proc"
mount -t sysfs sysfs "$MNT/sys"
mount --bind /run "$MNT/run"
chroot "$MNT" /bin/bash /root/tomato-build/configure.sh
grub-install --target=i386-pc --boot-directory="$MNT/boot" --recheck "$LOOP"
chroot "$MNT" update-grub
rm -rf "$MNT/root/tomato-build" "$MNT/var/cache/apt/archives/"*.deb
truncate -s 0 "$MNT/etc/machine-id"
rm -f "$MNT/var/lib/dbus/machine-id"
sync
cleanup
trap - EXIT
qemu-img convert -f raw -O vmdk -o subformat=streamOptimized "$RAW" "$OUT/Tomato-OS-disk1.vmdk"
python3 "$ROOT/scripts/make-ovf.py" "$OUT/Tomato-OS-disk1.vmdk" "$OUT/Tomato-OS.ovf"
tar --format=ustar -cf "$OUT/Tomato-OS.ova" -C "$OUT" Tomato-OS.ovf Tomato-OS-disk1.vmdk
(cd "$OUT" && sha256sum Tomato-OS.ova > Tomato-OS.ova.sha256)
rm -f "$RAW"
echo "Built $OUT/Tomato-OS.ova"