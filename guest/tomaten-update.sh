#!/bin/sh
set -eu
export DEBIAN_FRONTEND=noninteractive
# Keep Debian and Brave packages current without replacing the user's home.
apt-get -o DPkg::Lock::Timeout=300 update
apt-get -y -o DPkg::Lock::Timeout=300 \
  -o Dpkg::Options::=--force-confdef \
  -o Dpkg::Options::=--force-confold upgrade