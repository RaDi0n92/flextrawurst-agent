#!/usr/bin/env bash
set -Eeuo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
  echo "Dieses Installationsskript muss als root laufen." >&2
  exit 1
fi
python3 "$HERE/build_house.py" install
python3 "$HERE/build_house.py" verify
