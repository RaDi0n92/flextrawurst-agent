#!/usr/bin/env bash
cd /root/werkraum || exit 1
mkdir -p state
touch state/journal.log
MSG="${*:-kein text}"
TS="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
echo "[$TS] $MSG" >> state/journal.log
echo "ok: $TS"
