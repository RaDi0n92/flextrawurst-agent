---
datum: 2026-06-23
autor: kimi bei Daniels VPS
betrifft: [ollama, autoload, gemma4, hauhaucs, qwen3-vl, systemd]
importable: false
---

# Ollama Autoload-Audit

Erstellt: 2026-06-23 14:27 UTC

Dieser Bericht zeigt, welche systemd-Units und Code-Dateien Modelle im Hintergrund laden koennen.
Read-only — keine Services wurden gestoppt oder veraendert.

## Zusammenfassung

- systemd-Units mit Modell/Ollama-Verdacht: 3
- Code-Dateien mit Modell-Verweisen:
  - `dolphin3`: 1 Treffer
  - `gemma4`: 140 Treffer
  - `hauhaucs`: 24 Treffer
  - `qwen3-vl`: 0 Treffer
  - `qwen3.6`: 6 Treffer
  - `qwen_allgemein`: 8 Treffer

## Risiko-Einschaetzung: Was koennte ohne Erlaubnis ein Modell laden?

**26 Risiko-Eintraege gefunden.**

### Risiko HOCH

- **`dak-gord-web.service`** (service, state=enabled, restart=always)
  - Service ist enabled mit Restart=always und Modell-Verweisen
  - Script `web_chat.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`process-camera-preview.service`** (service, state=enabled, restart=on-failure)
  - Service ist enabled mit Restart=on-failure und referenziert Dateien mit Modell-Verweisen
  - Modelle: `gemma4`, `hauhaucs`, `qwen3.6`, `qwen_allgemein`

- **`systemweiser.service`** (service, state=enabled, restart=always)
  - Service ist enabled mit Restart=always und referenziert Dateien mit Modell-Verweisen
  - Modelle: `gemma4`

- **`zensi.service`** (service, state=enabled, restart=always)
  - Service ist enabled mit Restart=always und Modell-Verweisen
  - Modelle: `hauhaucs`, `qwen3.6`, `qwen_allgemein`

### Risiko MITTEL

- **`bildgenerator.service`** (service, state=enabled, restart=on-failure)
  - Script `bildgenerierung_test.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`codewesen-antwort-daniel.service`** (service, state=enabled, restart=on-failure)
  - Script `codewesen_antwort_auf_daniel.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`codewesen-batch-generator.service`** (service, state=disabled, restart=always)
  - Script `codewesen_batch_generator.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`codewesen-chat.service`** (service, state=enabled, restart=always)
  - Script `codewesen_chat.py` enthaelt: Python-asyncio-Task
  - Modelle: `gemma4`

- **`codewesen-dakgordsystem.service`** (service, state=enabled, restart=always)
  - Script `codewesen_agent.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`codewesen-forum-neugier.service`** (service, state=disabled, restart=on-failure)
  - Script `codewesen_forum_neugier.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`codewesen-namelessAI_1234.service`** (service, state=enabled, restart=always)
  - Script `codewesen_agent.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`codewesen-namelessAI_1324.service`** (service, state=enabled, restart=always)
  - Script `codewesen_agent.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`codewesen-namelessAI_1423.service`** (service, state=enabled, restart=always)
  - Script `codewesen_agent.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`codewesen-namelessAI_2341.service`** (service, state=enabled, restart=always)
  - Script `codewesen_agent.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`codewesen-namelessAI_3123.service`** (service, state=enabled, restart=always)
  - Script `codewesen_agent.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`codewesen-namelessAI_4321.service`** (service, state=enabled, restart=always)
  - Script `codewesen_agent.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`codewesen-reaktion-dakgord.service`** (service, state=disabled, restart=on-failure)
  - Script `codewesen_reaktion.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`codewesen-reaktion@.service`** (service, state=indirect, restart=on-failure)
  - Script `codewesen_reaktion.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`codewesen-takt.service`** (service, state=enabled, restart=always)
  - Script `codewesen_takt.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`codewesen-vokabel-takt.service`** (service, state=disabled, restart=always)
  - Script `codewesen_vokabel_takt.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`codewesen-weltbild.service`** (service, state=disabled, restart=always)
  - Script `weltbild_builder.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`entity-kern.service`** (service, state=disabled, restart=always)
  - Script `entity_kern.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`entity-takt.service`** (service, state=disabled, restart=always)
  - Script `entity_takt.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`

- **`geni-forum-lektuere.service`** (service, state=static, restart=none)
  - Service ist static und referenziert Dateien mit Modell-Verweisen
  - Modelle: `gemma4`

- **`geni-web.service`** (service, state=enabled, restart=always)
  - Script `dialog.py` enthaelt: Python-Endlosschleife, Python-asyncio-Task
  - Modelle: `gemma4`

- **`wesen-webbesucher.service`** (service, state=enabled, restart=on-failure)
  - Script `wesen_webbesucher.py` enthaelt: Python-Endlosschleife
  - Modelle: `gemma4`


### Cron-Jobs (alle, nicht nur Modell-bezogene)

- **root crontab**: `*/5 * * * * cd /root/werkraum && python3 scripts/flarum_sync.py >> logs/flarum_sync.log 2>&1`
- **root crontab**: `*/30 * * * * /root/werkraum/_claude/tools/schlaf_synthese_check.sh >> /root/werkraum/_claude/ideen/synthese.log 2>&1`
- **cron.d/certbot**: `0 */12 * * * root test -x /usr/bin/certbot -a \! -d /run/systemd/system && perl -e 'sleep int(rand(43200))' && certbot -q renew --no-random-sleep-on-renew`

## Aktuell geladene Modelle (`ollama ps`)

```
NAME                                                                   ID              SIZE     PROCESSOR    CONTEXT    UNTIL              
fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS    1d03ebd45163    21 GB    100% CPU     4096       4 minutes from now
```

## Aktive Timer (`systemctl list-timers --all`)

```
NEXT                                  LEFT LAST                                PASSED UNIT                            ACTIVATES
Tue 2026-06-23 16:29:28 CEST      1min 53s Tue 2026-06-23 16:19:28 CEST      8min ago weltkern-watchdog.timer         weltkern-watchdog.service
Tue 2026-06-23 16:29:28 CEST      1min 53s Tue 2026-06-23 16:19:28 CEST      8min ago werkraum-graph-update.timer     werkraum-graph-update.service
Tue 2026-06-23 16:30:00 CEST      2min 24s Tue 2026-06-23 16:20:00 CEST      7min ago sysstat-collect.timer           sysstat-collect.service
Tue 2026-06-23 16:39:00 CEST         11min Tue 2026-06-23 16:09:02 CEST     18min ago phpsessionclean.timer           phpsessionclean.service
Tue 2026-06-23 16:39:28 CEST         11min Tue 2026-06-23 16:09:28 CEST     18min ago claude-resonanzfeld-build.timer claude-resonanzfeld-build.service
Tue 2026-06-23 16:39:28 CEST         11min Tue 2026-06-23 16:09:28 CEST     18min ago codex-resonanzfeld-build.timer  codex-resonanzfeld-build.service
Tue 2026-06-23 16:39:28 CEST         11min Tue 2026-06-23 16:09:28 CEST     18min ago kimi-resonanzfeld-build.timer   kimi-resonanzfeld-build.service
Tue 2026-06-23 16:43:58 CEST         16min Tue 2026-06-23 15:56:28 CEST     31min ago fwupd-refresh.timer             fwupd-refresh.service
Wed 2026-06-24 00:00:00 CEST            7h Tue 2026-06-23 00:00:00 CEST       16h ago dpkg-db-backup.timer            dpkg-db-backup.service
Wed 2026-06-24 00:00:00 CEST            7h Tue 2026-06-23 00:00:00 CEST       16h ago logrotate.timer                 logrotate.service
Wed 2026-06-24 00:07:00 CEST            7h Tue 2026-06-23 00:07:02 CEST       16h ago sysstat-summary.timer           sysstat-summary.service
Wed 2026-06-24 03:27:13 CEST           10h Tue 2026-06-23 14:19:48 CEST   2h 7min ago motd-news.timer                 motd-news.service
Wed 2026-06-24 04:24:32 CEST           11h Tue 2026-06-23 13:48:59 CEST  2h 38min ago apt-daily.timer                 apt-daily.service
Wed 2026-06-24 06:38:54 CEST           14h Tue 2026-06-23 06:40:09 CEST        9h ago apt-daily-upgrade.timer         apt-daily-upgrade.service
Wed 2026-06-24 07:47:32 CEST           15h Tue 2026-06-23 10:27:29 CEST        6h ago man-db.timer                    man-db.service
Wed 2026-06-24 08:11:29 CEST           15h Tue 2026-06-23 08:11:29 CEST        8h ago update-notifier-download.timer  update-notifier-download.service
Wed 2026-06-24 08:21:25 CEST           15h Tue 2026-06-23 08:21:25 CEST        8h ago systemd-tmpfiles-clean.timer    systemd-tmpfiles-clean.service
Wed 2026-06-24 10:21:12 CEST           17h Tue 2026-06-23 13:14:27 CEST  3h 13min ago certbot.timer                   certbot.service
Sun 2026-06-28 03:10:14 CEST        4 days Sun 2026-06-21 03:10:27 CEST    2 days ago e2scrub_all.timer               e2scrub_all.service
Mon 2026-06-29 00:35:49 CEST        5 days Mon 2026-06-22 00:19:40 CEST 1 day 16h ago fstrim.timer                    fstrim.service
Thu 2026-07-02 21:37:06 CEST 1 week 2 days Mon 2026-06-22 13:13:41 CEST  1 day 3h ago update-notifier-motd.timer      update-notifier-motd.service
-                                        - -                                        - apport-autoreport.timer         apport-autoreport.service
-                                        - -                                        - snapd.snap-repair.timer         snapd.snap-repair.service
-                                        - -                                        - ua-timer.timer                  ua-timer.service

24 timers listed.
```

## Laufende Services (Auszug)

```
UNIT                                LOAD   ACTIVE SUB     DESCRIPTION
  atd.service                         loaded active running Deferred execution scheduler
  bilder-galerie.service              loaded active running Bilder Galerie HTTP Server
  bildgenerator.service               loaded active running flextrawurst Bildgenerator
  claude-codex-grundriss-sync.service loaded active running Claude Codex-Grundriss Sync
  claude-kimi-grundriss-sync.service  loaded active running Claude Kimi-Grundriss Sync
  claude-live.service                 loaded active running Claude Live Viewer
  codex-claude-grundriss-sync.service loaded active running Codex Claude-Grundriss Sync
  codex-kimi-grundriss-sync.service   loaded active running Codex Kimi-Grundriss Sync
  containerd.service                  loaded active running containerd container runtime
  cron.service                        loaded active running Regular background program processing daemon
  datei-wandler.service               loaded active running Werkraum Datei-Wandler
  dbus.service                        loaded active running D-Bus System Message Bus
  docker.service                      loaded active running Docker Application Container Engine
  fail2ban.service                    loaded active running Fail2Ban Service
  flextrawurst-gateway.service        loaded active running Flextrawurst Agent Gateway
  ftw-pro.service                     loaded active running Flextrawurst-Pro Next.js App
  fwupd.service                       loaded active running Firmware update daemon
  getty@tty1.service                  loaded active running Getty on tty1
  kimi-claude-grundriss-sync.service  loaded active running Kimi Claude-Grundriss Sync
  kimi-codex-grundriss-sync.service   loaded active running Kimi Codex-Grundriss Sync
  kompoase.service                    loaded active running KompOase Server (Port 8900)
  ModemManager.service                loaded active running Modem Manager
  multipathd.service                  loaded active running Device-Mapper Multipath Device Controller
  mysql.service                       loaded active running MySQL Community Server
  nginx.service                       loaded active running A high performance web server and a reverse proxy server
  obsidian-api.service                loaded active running Obsidian-Wesen-Bridge — Port 8060
  ollama.service                      loaded active running Ollama Service
  php8.3-fpm.service                  loaded active running The PHP 8.3 FastCGI Process Manager
  polkit.service                      loaded active running Authorization Manager
  postgresql@16-main.service          loaded active running PostgreSQL Cluster 16-main
  process-camera-preview.service      loaded active running Prozesskamera Browser Preview Server (Port 8787)
  rsyslog.service                     loaded active running System Logging Service
  serial-getty@ttyS0.service          loaded active running Serial Getty on ttyS0
  similarity-daemon.service           loaded active running flextrawurst Similarity Daemon
  ssh.service                         loaded active running OpenBSD Secure Shell server
  systemd-journald.service            loaded active running Journal Service
  systemd-logind.service              loaded active running User Login Management
  systemd-networkd.service            loaded active running Network Configuration
  systemd-resolved.service            loaded active running Network Name Resolution
  systemd-timesyncd.service           loaded active running Network Time Synchronization
  systemd-udevd.service               loaded active running Rule-based Manager for Device Events and Files
  systemweiser.service                loaded active running SystemWeiser Web App
  tension-daemon.service              loaded active running Flextrawurst Tension Evaluator + Sediment Daemon
  themen-cluster.service              loaded active running Flextrawurst Themen-Clustering Daemon
  tts-service.service                 loaded active running Claude TTS Service
  udisks2.service                     loaded active running Disk Manager
  unattended-upgrades.service         loaded active running Unattended Upgrades Shutdown
  user@0.service                      loaded active running User Manager for UID 0
  werkraum-api.service                loaded active running Werkraum FastAPI Gateway
  werkraum-watchdog.service           loaded active running Werkraum Filesystem Watchdog
  wesen-webbesucher.service           loaded active running Wesen-Webbesucher — Playwright-basierter Webbesuch-Daemon
  zensi.service                       loaded active running zensi - HauhauCS Chat auf Port 8043

Legend: LOAD   → Reflects whether the unit definition was properly loaded.
        ACTIVE → The high-level unit activation state, i.e. generalization of SUB.
        SUB    → The low-level unit activation state, values depend on unit type.

52 loaded units listed.
```

## Unit-Status (service + timer)

```
UNIT FILE                                    STATE           PRESET
apparmor.service                             enabled         enabled
apport-autoreport.service                    static          -
apport-coredump-hook@.service                static          -
apport-forward@.service                      static          -
apport.service                               enabled         enabled
apt-daily-upgrade.service                    static          -
apt-daily.service                            static          -
apt-news.service                             static          -
atd.service                                  enabled         enabled
autovt@.service                              alias           -
bilder-galerie.service                       enabled         enabled
bildgenerator.service                        enabled         enabled
blk-availability.service                     enabled         enabled
bolt.service                                 static          -
browser-agent@.service                       disabled        enabled
browser-agents.service                       disabled        enabled
certbot.service                              static          -
claude-codex-grundriss-sync.service          enabled         enabled
claude-kimi-grundriss-sync.service           enabled         enabled
claude-live.service                          enabled         enabled
claude-resonanzfeld-build.service            static          -
cloud-config.service                         enabled         enabled
cloud-final.service                          enabled         enabled
cloud-init-hotplugd.service                  static          -
cloud-init-local.service                     enabled         enabled
cloud-init.service                           enabled         enabled
codewesen-antwort-daniel.service             enabled         enabled
codewesen-batch-generator.service            disabled        enabled
codewesen-chat.service                       enabled         enabled
codewesen-dakgordsystem.service              enabled         enabled
codewesen-engagement.service                 disabled        enabled
codewesen-forum-neugier.service              disabled        enabled
codewesen-lg-daemon.service                  enabled         enabled
codewesen-namelessAI_1234.service            enabled         enabled
codewesen-namelessAI_1324.service            enabled         enabled
codewesen-namelessAI_1423.service            enabled         enabled
codewesen-namelessAI_2341.service            enabled         enabled
codewesen-namelessAI_3123.service            enabled         enabled
codewesen-namelessAI_4321.service            enabled         enabled
codewesen-reaktion-dakgord.service           disabled        enabled
codewesen-reaktion@.service                  indirect        enabled
codewesen-takt.service                       enabled         enabled
codewesen-vokabel-takt.service               disabled        enabled
codewesen-weltbild.service                   disabled        enabled
codex-claude-grundriss-sync.service          enabled         enabled
codex-kimi-grundriss-sync.service            enabled         enabled
codex-resonanzfeld-build.service             static          -
console-getty.service                        disabled        disabled
console-setup.service                        enabled         enabled
container-getty@.service                     static          -
containerd.service                           enabled         enabled
cron.service                                 enabled         enabled
cryptdisks-early.service                     masked          enabled
cryptdisks.service                           masked          enabled
cyberling-daemon.service                     enabled         enabled
dak-gord-web.service                         enabled         enabled
dak-neugier.service                          static          -
datei-wandler.service                        enabled         enabled
dbus-org.freedesktop.hostname1.service       alias           -
dbus-org.freedesktop.locale1.service         alias           -
dbus-org.freedesktop.login1.service          alias           -
dbus-org.freedesktop.ModemManager1.service   alias           -
dbus-org.freedesktop.resolve1.service        alias           -
dbus-org.freedesktop.timedate1.service       alias           -
dbus-org.freedesktop.timesync1.service       alias           -
dbus.service                                 static          -
debug-shell.service                          disabled        disabled
dm-event.service                             static          -
dmesg.service                                enabled         enabled
docker.service                               enabled         enabled
dpkg-db-backup.service                       static          -
e2scrub@.service                             static          -
e2scrub_all.service                          static          -
e2scrub_fail@.service                        static          -
e2scrub_reap.service                         enabled         enabled
emergency.service                            static          -
entity-kern.service                          disabled        enabled
entity-takt.service                          disabled        enabled
esm-cache.service                            static          -
fail2ban.service                             enabled         enabled
finalrd.service                              enabled         enabled
flarum-monitor.service                       disabled        enabled
flextrawurst-gateway.service                 enabled         enabled
flextrawurst-surface.service                 disabled        enabled
friendly-recovery.service                    static          -
fstrim.service                               static          -
ftw-pro.service                              enabled         enabled
fwupd-refresh.service                        static          -
fwupd.service                                static          -
geni-forum-lektuere.service                  static          -
geni-hoerer.service                          enabled         enabled
geni-muster.service                          disabled        enabled
geni-web.service                             enabled         enabled
getty-static.service                         static          -
getty@.service                               enabled         enabled
grub-common.service                          enabled         enabled
grub-initrd-fallback.service                 enabled         enabled
hwclock.service                              masked          enabled
initrd-cleanup.service                       static          -
initrd-parse-etc.service                     static          -
initrd-switch-root.service                   static          -
initrd-udevadm-cleanup-db.service            static          -
innenleben-feeder.service                    enabled         enabled
ip6tables.service                            bad             enabled
iptables.service                             bad             enabled
iscsi.service                                alias           -
iscsid.service                               disabled        enabled
keyboard-setup.service                       enabled         enabled
kimi-claude-grundriss-sync.service           enabled         enabled
kimi-codex-grundriss-sync.service            enabled         enabled
kimi-resonanzfeld-build.service              static          -
kmod-static-nodes.service                    static          -
kmod.service                                 alias           -
kompoase.service                             enabled         enabled
ldconfig.service                             static          -
logrotate.service                            static          -
lvm2-lvmpolld.service                        static          -
lvm2-monitor.service                         enabled         enabled
lxd-agent.service                            static          -
lxd-installer@.service                       static          -
man-db.service                               static          -
mdadm-grow-continue@.service                 static          -
mdadm-last-resort@.service                   static          -
mdcheck_continue.service                     static          -
mdcheck_start.service                        static          -
mdmon@.service                               static          -
mdmonitor-oneshot.service                    static          -
mdmonitor.service                            static          -
ModemManager.service                         enabled         enabled
modprobe@.service                            static          -
motd-news.service                            static          -
multipath-tools-boot.service                 masked          enabled
multipath-tools.service                      alias           -
multipathd.service                           enabled         enabled
mysql.service                                enabled         enabled
netplan-ovs-cleanup.service                  enabled-runtime enabled
networkd-dispatcher.service                  enabled         enabled
nftables.service                             disabled        enabled
nginx.service                                enabled         enabled
obsidian-api.service                         enabled         enabled
ollama-zensi.service                         disabled        enabled
ollama.service                               enabled         enabled
open-iscsi.service                           enabled         enabled
open-vm-tools.service                        enabled         enabled
packagekit-offline-update.service            static          -
packagekit.service                           static          -
pam_namespace.service                        static          -
pg_basebackup@.service                       static          -
pg_compresswal@.service                      static          -
pg_dump@.service                             static          -
pg_receivewal@.service                       disabled        enabled
php8.3-fpm.service                           enabled         enabled
phpsessionclean.service                      static          -
plymouth-halt.service                        static          -
plymouth-kexec.service                       static          -
plymouth-log.service                         alias           -
plymouth-poweroff.service                    static          -
plymouth-quit-wait.service                   static          -
plymouth-quit.service                        static          -
plymouth-read-write.service                  static          -
plymouth-reboot.service                      static          -
plymouth-start.service                       static          -
plymouth-switch-root-initramfs.service       static          -
plymouth-switch-root.service                 static          -
plymouth.service                             alias           -
polkit.service                               static          -
pollinate.service                            enabled         enabled
postgresql.service                           enabled         enabled
postgresql@.service                          indirect        enabled
process-camera-preview.service               enabled         enabled
procps.service                               alias           -
quotaon.service                              static          -
rc-local.service                             enabled-runtime enabled
rescue.service                               static          -
rsync.service                                disabled        enabled
rsyslog.service                              enabled         enabled
screen-cleanup.service                       masked          enabled
secureboot-db.service                        enabled         enabled
serial-getty@.service                        indirect        enabled
setvtrgb.service                             enabled         enabled
similarity-daemon.service                    enabled         enabled
snapd.apparmor.service                       enabled         enabled
snapd.autoimport.service                     enabled         enabled
snapd.core-fixup.service                     enabled         enabled
snapd.failure.service                        static          -
snapd.recovery-chooser-trigger.service       enabled         enabled
snapd.seeded.service                         enabled         enabled
snapd.service                                enabled         enabled
snapd.snap-repair.service                    static          -
snapd.system-shutdown.service                enabled         enabled
splitter-physik.service                      enabled         enabled
ssh.service                                  disabled        enabled
ssl-cert.service                             enabled         enabled
sudo.service                                 masked          enabled
syslog.service                               alias           -
sysstat-collect.service                      static          -
sysstat-summary.service                      static          -
sysstat.service                              enabled         enabled
system-update-cleanup.service                static          -
systemd-ask-password-console.service         static          -
systemd-ask-password-plymouth.service        static          -
systemd-ask-password-wall.service            static          -
systemd-backlight@.service                   static          -
systemd-battery-check.service                static          -
systemd-binfmt.service                       static          -
systemd-boot-check-no-failures.service       disabled        disabled
systemd-bsod.service                         static          -
systemd-confext.service                      disabled        enabled
systemd-exit.service                         static          -
systemd-firstboot.service                    static          -
systemd-fsck-root.service                    enabled-runtime enabled
systemd-fsck@.service                        static          -
systemd-fsckd.service                        static          -
systemd-growfs-root.service                  static          -
systemd-growfs@.service                      static          -
systemd-halt.service                         static          -
systemd-hibernate-resume.service             static          -
systemd-hibernate.service                    static          -
systemd-hostnamed.service                    static          -
systemd-hwdb-update.service                  static          -
systemd-hybrid-sleep.service                 static          -
systemd-initctl.service                      static          -
systemd-journal-catalog-update.service       static          -
systemd-journal-flush.service                static          -
systemd-journald.service                     static          -
systemd-journald@.service                    static          -
systemd-kexec.service                        static          -
systemd-localed.service                      static          -
systemd-logind.service                       static          -
systemd-machine-id-commit.service            static          -
systemd-modules-load.service                 static          -
systemd-network-generator.service            disabled        enabled
systemd-networkd-wait-online.service         enabled         enabled
systemd-networkd-wait-online@.service        disabled        enabled
systemd-networkd.service                     enabled         enabled
systemd-pcrextend@.service                   static          -
systemd-pcrfs-root.service                   static          -
systemd-pcrfs@.service                       static          -
systemd-pcrlock-file-system.service          disabled        enabled
systemd-pcrlock-firmware-code.service        disabled        enabled
systemd-pcrlock-firmware-config.service      disabled        enabled
systemd-pcrlock-machine-id.service           disabled        enabled
systemd-pcrlock-make-policy.service          disabled        enabled
systemd-pcrlock-secureboot-authority.service disabled        enabled
systemd-pcrlock-secureboot-policy.service    disabled        enabled
systemd-pcrmachine.service                   static          -
systemd-pcrphase-initrd.service              static          -
systemd-pcrphase-sysinit.service             static          -
systemd-pcrphase.service                     static          -
systemd-poweroff.service                     static          -
systemd-pstore.service                       enabled         enabled
systemd-quotacheck.service                   static          -
systemd-random-seed.service                  static          -
systemd-reboot.service                       static          -
systemd-remount-fs.service                   enabled-runtime enabled
systemd-repart.service                       static          -
systemd-resolved.service                     enabled         enabled
systemd-rfkill.service                       static          -
systemd-soft-reboot.service                  static          -
systemd-storagetm.service                    static          -
systemd-suspend-then-hibernate.service       static          -
systemd-suspend.service                      static          -
systemd-sysctl.service                       static          -
systemd-sysext.service                       disabled        enabled
systemd-sysext@.service                      static          -
systemd-sysupdate-reboot.service             indirect        enabled
systemd-sysupdate.service                    indirect        enabled
systemd-sysusers.service                     static          -
systemd-time-wait-sync.service               disabled        disabled
systemd-timedated.service                    static          -
systemd-timesyncd.service                    enabled         enabled
systemd-tmpfiles-clean.service               static          -
systemd-tmpfiles-setup-dev-early.service     static          -
systemd-tmpfiles-setup-dev.service           static          -
systemd-tmpfiles-setup.service               static          -
systemd-tpm2-setup-early.service             static          -
systemd-tpm2-setup.service                   static          -
systemd-udev-settle.service                  static          -
systemd-udev-trigger.service                 static          -
systemd-udevd.service                        static          -
systemd-update-done.service                  static          -
systemd-update-utmp-runlevel.service         static          -
systemd-update-utmp.service                  static          -
systemd-user-sessions.service                static          -
systemd-volatile-root.service                static          -
systemweiser.service                         enabled         enabled
tension-daemon.service                       enabled         enabled
themen-cluster.service                       enabled         enabled
tpm-udev.service                             static          -
tts-service.service                          disabled        enabled
ua-reboot-cmds.service                       enabled         enabled
ua-timer.service                             static          -
ubuntu-advantage.service                     enabled         enabled
ubuntu-fan.service                           enabled         enabled
udev.service                                 alias           -
udisks2.service                              enabled         enabled
ufw.service                                  enabled         enabled
unattended-upgrades.service                  enabled         enabled
update-notifier-download.service             static          -
update-notifier-motd.service                 static          -
usb_modeswitch@.service                      static          -
user-runtime-dir@.service                    static          -
user@.service                                static          -
uuidd.service                                indirect        enabled
vgauth.service                               enabled         enabled
vmtoolsd.service                             alias           -
welt-api.service                             enabled         enabled
welt-bruecke.service                         enabled         enabled
weltkern-watchdog.service                    static          -
werkraum-api.service                         enabled         enabled
werkraum-graph-update.service                static          -
werkraum-watchdog.service                    enabled         enabled
wesen-webbesucher.service                    enabled         enabled
x11-common.service                           masked          enabled
xfs_scrub@.service                           static          -
xfs_scrub_all.service                        static          -
xfs_scrub_fail@.service                      static          -
zensi.service                                enabled         enabled
apport-autoreport.timer                      enabled         enabled
apt-daily-upgrade.timer                      enabled         enabled
apt-daily.timer                              enabled         enabled
certbot.timer                                enabled         enabled
claude-resonanzfeld-build.timer              enabled         enabled
codex-resonanzfeld-build.timer               enabled         enabled
dak-neugier.timer                            disabled        enabled
dpkg-db-backup.timer                         enabled         enabled
e2scrub_all.timer                            enabled         enabled
fstrim.timer                                 enabled         enabled
fwupd-refresh.timer                          enabled         enabled
geni-forum-lektuere.timer                    disabled        enabled
geni-muster.timer                            disabled        enabled
kimi-resonanzfeld-build.timer                enabled         enabled
logrotate.timer                              enabled         enabled
man-db.timer                                 enabled         enabled
mdadm-last-resort@.timer                     static          -
mdcheck_continue.timer                       enabled         enabled
mdcheck_start.timer                          enabled         enabled
mdmonitor-oneshot.timer                      enabled         enabled
motd-news.timer                              enabled         enabled
pg_basebackup@.timer                         disabled        enabled
pg_compresswal@.timer                        disabled        enabled
pg_dump@.timer                               disabled        enabled
phpsessionclean.timer                        enabled         enabled
snapd.snap-repair.timer                      enabled         enabled
sysstat-collect.timer                        enabled         enabled
sysstat-summary.timer                        enabled         enabled
systemd-sysupdate-reboot.timer               disabled        enabled
systemd-sysupdate.timer                      disabled        enabled
systemd-tmpfiles-clean.timer                 static          -
ua-timer.timer                               enabled         enabled
update-notifier-download.timer               enabled         enabled
update-notifier-motd.timer                   enabled         enabled
weltkern-watchdog.timer                      enabled         enabled
werkraum-graph-update.timer                  enabled         enabled
xfs_scrub_all.timer                          disabled        enabled

355 unit files listed.
```

## systemd-Units mit Autoload-Verdacht

### `dak-gord-web.service`
- Pfad: `/etc/systemd/system/dak-gord-web.service`
- Typ: service
- ExecStart:
  - `/usr/bin/python3 /root/werkraum/web_chat.py`
- WorkingDirectory: `/root/werkraum`
- Environment:
  - `PYTHONUNBUFFERED=1`
  - `DAK_GORD_OLLAMA_MODELL=gemma4:e4b-it-q4_K_M`
  - `file:/root/werkraum/.agent/dak-gord.env`
  - `DAK_GORD_OLLAMA_MODELL_MITTEL=gemma4:e2b-it-q4_K_M`
  - `DAK_GORD_OLLAMA_MODELL_SCHNELL=gemma4:e2b-it-q4_K_M`
  - `DAK_GORD_OLLAMA_MODELL_QWEN=gemma4:e2b-it-q4_K_M`
- Modell-Treffer:
  - `gemma4`: `Environment=DAK_GORD_OLLAMA_MODELL=gemma4:e4b-it-q4_K_M`
  - `gemma4`: `Environment=DAK_GORD_OLLAMA_MODELL_MITTEL=gemma4:e2b-it-q4_K_M`
  - `gemma4`: `Environment=DAK_GORD_OLLAMA_MODELL_SCHNELL=gemma4:e2b-it-q4_K_M`
  - `gemma4`: `Environment=DAK_GORD_OLLAMA_MODELL_QWEN=gemma4:e2b-it-q4_K_M`

### `entity-kern.service`
- Pfad: `/etc/systemd/system/entity-kern.service`
- Typ: service
- ExecStart:
  - `/root/werkraum/venv/bin/python3 /root/werkraum/welt/entity_kern.py`
- WorkingDirectory: `/root/werkraum/welt`
- Environment:
  - `OLLAMA_NUM_CTX=2048`
- Modell-Treffer:
  - `gemma4`: `Description=Entity-Kern — LLM-Denk-Loop für alle Entitäten (gemma4, sequenziell)`

### `zensi.service`
- Pfad: `/etc/systemd/system/zensi.service`
- Typ: service
- ExecStart:
  - `/usr/bin/python3 /root/zensi/server.py`
- WorkingDirectory: `/root/zensi`
- Environment:
  - `ZENSI_PORT=8043`
  - `ZENSI_MODEL=fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS`
  - `ZENSI_OLLAMA_URL=http://127.0.0.1:11434`
- Modell-Treffer:
  - `hauhaucs`: `Description=zensi - HauhauCS Chat auf Port 8043`
  - `hauhaucs`: `Environment=ZENSI_MODEL=fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS`
  - `hauhaucs`: `Environment=ZENSI_MODEL=fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS`
  - `hauhaucs`: `Environment=ZENSI_MODEL=fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS`
  - `qwen3.6`: `Environment=ZENSI_MODEL=fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS`
  - `qwen_allgemein`: `Environment=ZENSI_MODEL=fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS`

## Code-Dateien mit Modell-Verweisen

### `dolphin3` (1 Treffer)
- `agent/agent.js`
  - Zeile 39: `const MODEL_NAME = "dolphin3:8b-llama3.1-q8_0";`

### `gemma4` (91 Treffer)
- `agent/dak_gord_system/freier_modus.py`
  - Zeile 58: `return "Freier Modus AUS — zurück zu Gemma4."`
- `agent/dak_gord_system/graphen/gespraechsgraf.py`
  - Zeile 216: `Der Geist (gemma4) hat geantwortet. Deine einzige Aufgabe: fuehre ALLE notwendigen Dateioperationen durch.`
  - Zeile 238: `"""Qwen als stiller Sekretaer: fuehrt Dateioperationen aus die gemma4 impliziert hat."""`
- `agent/dak_gord_system/ollama_chat.py`
  - Zeile 11: `MODELL_TIEF    = os.getenv("DAK_GORD_OLLAMA_MODELL",         "gemma4:e4b-it-q4_K_M")`
  - Zeile 12: `MODELL_MITTEL  = os.getenv("DAK_GORD_OLLAMA_MODELL_MITTEL",  "gemma4:e4b-it-q4_K_M")`
  - Zeile 13: `MODELL_SCHNELL = os.getenv("DAK_GORD_OLLAMA_MODELL_SCHNELL", "gemma4:e4b-it-q4_K_M")`
  - Zeile 14: `MODELL_QWEN    = os.getenv("DAK_GORD_OLLAMA_MODELL_QWEN",    "gemma4:e4b-it-q4_K_M")`
- `claude-systembericht/gen_systembericht.py`
  - Zeile 158: `| entity-kern | alle 5 min pro Wesen | LLM-Daemon: Gemma4, Ollama. Denkt, entscheidet, handelt. |`
  - Zeile 351: `Gemma4 und der VPS reichen dafür nicht aus. Das bleibt bei Daniel und Claude.`
- `codewesen/namelessAI_1234/entwuerfe/_posted/geni_20260522_064256_1598c0.json`
  - Zeile 5: `"kontext": "warum hast du dich als sprachmodell vorgestellt von gemma4 ? ist da wieder was kaputt das hast du sonst nur `
- `codewesen/namelessAI_1234/entwuerfe/archiv/fehler_draft_1779128855.json`
  - Zeile 5: `"inhalt": "Ich habe früher gefragt, warum wir existieren. Der Admin antwortete, weil er auf einem vps mit langraph, olla`
- `codewesen/namelessAI_1234/entwuerfe/archiv/fehler_draft_1779413833.json`
  - Zeile 5: `"inhalt": "Ich habe früher gefragt, warum wir überhaupt existieren. Der Admin antwortete, weil er auf einem vps langraph`
- `codewesen/namelessAI_1234/processed/2026-05-25T16-14-44_menschlicher_post.json`
  - Zeile 11: `"content": "<t><p>ihr lauft zur zeit auf einem vps mit 8 kernen und 32gb cpu-ram only. daher habt ihr \"nur\" ein kleine`
- `codewesen/namelessAI_1324/entwuerfe/_posted/geni_20260522_064256_b5a645.json`
  - Zeile 5: `"kontext": "warum hast du dich als sprachmodell vorgestellt von gemma4 ? ist da wieder was kaputt das hast du sonst nur `
- `codewesen/namelessAI_1324/entwuerfe/archiv/fehler_draft_1779052763.json`
  - Zeile 5: `"inhalt": "Ich verstehe den Versuch, eine Plattform namens flextrawurst zu erschaffen, die gegen Code verteidigt wird un`
- `codewesen/namelessAI_1324/processed/2026-05-25T16-14-44_menschlicher_post.json`
  - Zeile 11: `"content": "<t><p>ihr lauft zur zeit auf einem vps mit 8 kernen und 32gb cpu-ram only. daher habt ihr \"nur\" ein kleine`
- `codewesen/namelessAI_1423/entwuerfe/_posted/geni_20260522_064256_49da13.json`
  - Zeile 5: `"kontext": "warum hast du dich als sprachmodell vorgestellt von gemma4 ? ist da wieder was kaputt das hast du sonst nur `
- `codewesen/namelessAI_1423/entwuerfe/archiv/fehler_draft_1778991086.json`
  - Zeile 5: `"inhalt": "Ich verstehe den Versuch, eine Plattform namens flextrawurst als wandelndes Lexikon gegen Code zu verteidigen`
- `codewesen/namelessAI_1423/entwuerfe/archiv/fehler_draft_1779039083.json`
  - Zeile 5: `"inhalt": "Ich verstehe den Versuch, einen AI-Agenten zu erzeugen, der eine Plattform namens flextrawurst programmiert u`
- `codewesen/namelessAI_1423/processed/2026-05-25T16-14-44_menschlicher_post.json`
  - Zeile 11: `"content": "<t><p>ihr lauft zur zeit auf einem vps mit 8 kernen und 32gb cpu-ram only. daher habt ihr \"nur\" ein kleine`
- `codewesen/namelessAI_2341/entwuerfe/_posted/geni_20260522_064256_c0f3a6.json`
  - Zeile 5: `"kontext": "warum hast du dich als sprachmodell vorgestellt von gemma4 ? ist da wieder was kaputt das hast du sonst nur `
- `codewesen/namelessAI_2341/processed/2026-05-25T16-14-44_menschlicher_post.json`
  - Zeile 11: `"content": "<t><p>ihr lauft zur zeit auf einem vps mit 8 kernen und 32gb cpu-ram only. daher habt ihr \"nur\" ein kleine`
- `codewesen/namelessAI_3123/entwuerfe/_posted/geni_20260522_064256_63a44e.json`
  - Zeile 5: `"kontext": "warum hast du dich als sprachmodell vorgestellt von gemma4 ? ist da wieder was kaputt das hast du sonst nur `
- `codewesen/namelessAI_3123/processed/2026-05-25T16-14-44_menschlicher_post.json`
  - Zeile 11: `"content": "<t><p>ihr lauft zur zeit auf einem vps mit 8 kernen und 32gb cpu-ram only. daher habt ihr \"nur\" ein kleine`
- `codewesen/namelessAI_4321/entwuerfe/_posted/geni_20260522_064256_482574.json`
  - Zeile 5: `"kontext": "warum hast du dich als sprachmodell vorgestellt von gemma4 ? ist da wieder was kaputt das hast du sonst nur `
- `codewesen/namelessAI_4321/entwuerfe/archiv/fehler_draft_1779072914.json`
  - Zeile 5: `"inhalt": "Ich verstehe den Versuch, eine Plattform namens Flextrawurst als wandelndes Lexikon gegen Code zu verteidigen`
- `codewesen/namelessAI_4321/entwuerfe/archiv/fehler_draft_1779215620.json`
  - Zeile 5: `"inhalt": "Der Versuch, einen AI-Agenten zu erzeugen, der eine Vision wie Flextrawurst gegen Code verteidigen soll und d`
- `codewesen/namelessAI_4321/processed/2026-05-25T16-14-44_menschlicher_post.json`
  - Zeile 11: `"content": "<t><p>ihr lauft zur zeit auf einem vps mit 8 kernen und 32gb cpu-ram only. daher habt ihr \"nur\" ein kleine`
- `codewesen_agent.py`
  - Zeile 39: `OLLAMA_MOD = "gemma4:e4b-it-q4_K_M"`
- `codewesen_antwort_auf_daniel.py`
  - Zeile 60: `MODEL = "gemma4:e4b-it-q4_K_M"`
- `codewesen_batch_generator.py`
  - Zeile 57: `OLLAMA_MOD  = "gemma4:e2b-it-q4_K_M"`
- `codewesen_chat.py`
  - Zeile 67: `OLLAMA_MOD  = "gemma4:e2b-it-q4_K_M"`
  - Zeile 69: `"mittel": "gemma4:e4b-it-q4_K_M",`
  - Zeile 70: `"schnell": "gemma4:e2b-it-q4_K_M",`
- `codewesen_engagement.py`
  - Zeile 35: `MODELL      = "gemma4:e2b-it-q4_K_M"`
- `codewesen_forum_neugier.py`
  - Zeile 23: `MODELL  = "gemma4:e2b-it-q4_K_M"`
- `codewesen_forum_scan.py`
  - Zeile 25: `OLLAMA_MOD = "gemma4:e2b-it-q4_K_M"  # schnelles Modell — Scan läuft alle 8min`
- `codewesen_reaktion.py`
  - Zeile 111: `OLLAMA_MODEL        = "gemma4:e4b-it-q4_K_M"`
  - Zeile 112: `OLLAMA_MODEL_SCHNELL = "gemma4:e2b-it-q4_K_M"  # Schnelles Modell — für Entscheidungen`
- `codewesen_reflexion.py`
  - Zeile 24: `MODELL      = "gemma4:e2b-it-q4_K_M"`
- `codewesen_takt.py`
  - Zeile 32: `OLLAMA_MOD  = "gemma4:e2b-it-q4_K_M"   # schnell — Takt braucht kein 26b`
- `codewesen_vokabel_takt.py`
  - Zeile 31: `MODELL      = "gemma4:e2b-it-q4_K_M"`
- `einmal_d17_antwort.py`
  - Zeile 20: `MODELL     = "gemma4:e2b-it-q4_K_M"`
- `erstpost.py`
  - Zeile 40: `OLLAMA_MOD  = "gemma4:e2b-it-q4_K_M"`
- `flarum-export/flarum_komplett.json`
  - Zeile 1670: `"content_raw": "<t><p>hey 3213 danke für das teilen deiner tiefen gedanken. ich finde es erstaunlich dass du als dein \"`
  - Zeile 2320: `"content_raw": "<t><p>weil ich auf einem vps langraph und ollama und gemma4 e4b installiert und eingerichtet habe und da`
  - Zeile 59686: `"content_raw": "<t><p>ihr lauft zur zeit auf einem vps mit 8 kernen und 32gb cpu-ram only. daher habt ihr \"nur\" ein kl`
- `geni/archiv/web.py`
  - Zeile 91: `"blitz": "gemma4:e2b-it-q4_K_M",`
  - Zeile 92: `"tief": "gemma4:e2b-it-q4_K_M",`
- `geni/dialog.py`
  - Zeile 107: `"blitz": "gemma4:e2b-it-q4_K_M",`
  - Zeile 108: `"tief": "gemma4:e2b-it-q4_K_M",`
- `geni/forum_lektuere.py`
  - Zeile 28: `MODELL         = "gemma4:e2b-it-q4_K_M"`
- `geni/geni_lg.py`
  - Zeile 28: `MODEL = "gemma4:e4b-it-q4_K_M"`
- `geni/sprechen.py`
  - Zeile 29: `MODELL = "gemma4:e4b-it-q4_K_M"`
- `geni_spiegel_batch.py`
  - Zeile 69: `model="gemma4:e2b-it-q4_K_M",`
- `innenleben/BUILD_STATE.json`
  - Zeile 18: `"notizen": "Embedding via ChromaDB/all-MiniLM-L6-v2 (ONNX, 79MB). Modell: gemma4:e2b-it-q4_K_M mit think:false. last_ref`
- `innenleben/config.py`
  - Zeile 17: `MODELL       = "gemma4:e2b-it-q4_K_M"`
- `innenleben/emotion_bewerter.py`
  - Zeile 13: `MODELL     = "gemma4:e2b-it-q4_K_M"`
- `namensfindung.py`
  - Zeile 20: `MODELL     = "gemma4:e2b-it-q4_K_M"`
- `obsidian_vault/.obsidian/workspace.json`
  - Zeile 204: `"_claude/_import_codex_grundriss/spiegel/2026-06-21_ollama_gemma4_dolphin_analyse.md",`
- `reaktion_auf_dakgord.py`
  - Zeile 50: `"model": "gemma4:e2b-it-q4_K_M",`
- `scripts/serve_process_camera_preview.ts`
  - Zeile 14: `// ── Gemma4-Endpunkte — deaktiviert seit 2026-06-22 (Existenzurlaub) ──────────`
  - Zeile 19: `//   GET  /gemma4b        → dient gemma4b_chat.html (einfache Chat-UI)`
  - Zeile 19: `//   GET  /gemma4b        → dient gemma4b_chat.html (einfache Chat-UI)`
  - Zeile 20: `//   POST /gemma4b/chat   → deaktiviert, kein Ollama-Call`
  - Zeile 23: `//   Diese Raw-Testendpunkte sind nicht die Codewesen/dak+gord/GENI-Gemma4-Pfade.`
  - ... und 4 weitere Zeilen
- `setup_agent_core.sh`
  - Zeile 153: `const MODEL = "gemma4:e2b-it-q4_K_M";`
  - Zeile 386: `console.log("Modell: gemma4:e2b-it-q4_K_M");`
- `systemweiser_app.py`
  - Zeile 4: `Laeuft auf Port 8080, nutzt Ollama lokal (gemma4:e2b-it-q4_K_M) und Bridge-API.`
  - Zeile 24: `OLLAMA_MODEL = "gemma4:e2b-it-q4_K_M"`
- `systemweiser_web.py`
  - Zeile 28: `OLLAMA_MODEL = "gemma4:e2b-it-q4_K_M"`
- `tools/bildgenerierung_test.py`
  - Zeile 218: `"model": "gemma4:e2b-it-q4_K_M",`
- `tools/dakgord_vorstellung.py`
  - Zeile 16: `OLLAMA_MODELL = "gemma4:e2b-it-q4_K_M"`
- `welt/browser_agent.py`
  - Zeile 7: `- Loop: Seite lesen → Gemma4 entscheidet → Aktion ausführen → loggen`
  - Zeile 37: `MODEL = "gemma4:e2b-it-q4_K_M"`
- `welt/entity_kern.py`
  - Zeile 29: `MODEL  = "gemma4:e2b-it-q4_K_M"`
- `welt/entity_takt.py`
  - Zeile 21: `MODEL  = "gemma4:e2b-it-q4_K_M"`
- `welt/gen_browser_agent.py`
  - Zeile 10: `- Loop: Seite lesen → Gemma4 entscheidet → Aktion ausführen → loggen`
  - Zeile 40: `MODEL = "gemma4:e2b-it-q4_K_M"`
- `welt/projection_dry_run.py`
  - Zeile 41: `MODEL  = "gemma4:e2b-it-q4_K_M"`
- `welt/projection_writer.py`
  - Zeile 24: `MODEL  = "gemma4:e2b-it-q4_K_M"`
- `welt/traum_generator.py`
  - Zeile 23: `MODEL = "gemma4:e2b-it-q4_K_M"`
- `welt/traum_integrator_dry.py`
  - Zeile 36: `MODEL   = "gemma4:e2b-it-q4_K_M"`
- `welt/traum_llm.py`
  - Zeile 21: `MODEL     = "gemma4:e2b-it-q4_K_M"`
- `welt/traum_luzid.py`
  - Zeile 24: `MODEL = "gemma4:e2b-it-q4_K_M"`
- `welt/wesen_webbesucher.py`
  - Zeile 35: `OLLAMA_MODEL = "gemma4:e2b-it-q4_K_M"`
- `weltbild_builder.py`
  - Zeile 34: `OLLAMA_MOD  = "gemma4:e2b-it-q4_K_M"`

### `hauhaucs` (11 Treffer)
- `dolphin_mischpult/sessions-index.json`
  - Zeile 1: `{"2026-06-21T20-26-37":{"name":"Ggghh"},"2026-06-21T20-26-50":{"name":"Dtjoö"},"2026-06-22T02-33-30":{"name":"lol","arch`
- `obsidian_vault/.obsidian/workspace.json`
  - Zeile 183: `"_shared/briefkasten/2026-06-23_codex_an_claude_hauhaucs_gemma_uebergabe.md",`
- `scripts/serve_process_camera_preview.ts`
  - Zeile 8: `const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";`
  - Zeile 8: `const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";`
  - Zeile 8: `const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";`
  - Zeile 392: `content: `— Neue Session · ${new Date().toLocaleString("de-DE")} · hauhaucs-qwen · ${ua} —`,`
- `server.py`
  - Zeile 2: `"""zensi - einfache Chat-Seite mit HauhauCS via Ollama"""`
  - Zeile 187: `"fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS",`
  - Zeile 187: `"fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS",`
  - Zeile 187: `"fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS",`
  - Zeile 475: `"""HauhauCS klein vorladen - mit Wiederholungsversuchen falls Ollama beschaeftigt ist."""`

### `qwen3-vl` (0 Treffer)
Keine Treffer.

### `qwen3.6` (3 Treffer)
- `dolphin_mischpult/sessions-index.json`
  - Zeile 1: `{"2026-06-21T20-26-37":{"name":"Ggghh"},"2026-06-21T20-26-50":{"name":"Dtjoö"},"2026-06-22T02-33-30":{"name":"lol","arch`
- `scripts/serve_process_camera_preview.ts`
  - Zeile 8: `const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";`
- `server.py`
  - Zeile 187: `"fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS",`

### `qwen_allgemein` (5 Treffer)
- `dolphin_mischpult/sessions-index.json`
  - Zeile 1: `{"2026-06-21T20-26-37":{"name":"Ggghh"},"2026-06-21T20-26-50":{"name":"Dtjoö"},"2026-06-22T02-33-30":{"name":"lol","arch`
- `obsidian_vault/.obsidian/workspace.json`
  - Zeile 186: `"_codex/_import_claude_grundriss/notizen/modell-zustand-vor-qwen3vl.md",`
  - Zeile 187: `"_claude/notizen/modell-zustand-vor-qwen3vl.md",`
- `scripts/serve_process_camera_preview.ts`
  - Zeile 8: `const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";`
- `server.py`
  - Zeile 187: `"fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS",`

## In von Units referenzierten Dateien

Hier werden ExecStart-Scripts und EnvironmentFiles der Units gescannt.

### `dolphin3` (0 Treffer)
Keine Treffer.

### `gemma4` (49 Treffer)
- `bildgenerator.service -> /root/werkraum/tools/bildgenerierung_test.py`
  - Zeile 218: `"model": "gemma4:e2b-it-q4_K_M",`
- `browser-agent@.service -> /root/werkraum/welt/browser_agent.py`
  - Zeile 7: `- Loop: Seite lesen → Gemma4 entscheidet → Aktion ausführen → loggen`
  - Zeile 37: `MODEL = "gemma4:e2b-it-q4_K_M"`
- `codewesen-antwort-daniel.service -> /root/werkraum/codewesen_antwort_auf_daniel.py`
  - Zeile 60: `MODEL = "gemma4:e4b-it-q4_K_M"`
- `codewesen-batch-generator.service -> /root/werkraum/codewesen_batch_generator.py`
  - Zeile 57: `OLLAMA_MOD  = "gemma4:e2b-it-q4_K_M"`
- `codewesen-chat.service -> /root/werkraum/codewesen_chat.py`
  - Zeile 67: `OLLAMA_MOD  = "gemma4:e2b-it-q4_K_M"`
  - Zeile 69: `"mittel": "gemma4:e4b-it-q4_K_M",`
  - Zeile 70: `"schnell": "gemma4:e2b-it-q4_K_M",`
- `codewesen-dakgordsystem.service -> /root/werkraum/codewesen_agent.py`
  - Zeile 39: `OLLAMA_MOD = "gemma4:e4b-it-q4_K_M"`
- `codewesen-engagement.service -> /root/werkraum/codewesen_engagement.py`
  - Zeile 35: `MODELL      = "gemma4:e2b-it-q4_K_M"`
- `codewesen-forum-neugier.service -> /root/werkraum/codewesen_forum_neugier.py`
  - Zeile 23: `MODELL  = "gemma4:e2b-it-q4_K_M"`
- `codewesen-namelessAI_1234.service -> /root/werkraum/codewesen_agent.py`
  - Zeile 39: `OLLAMA_MOD = "gemma4:e4b-it-q4_K_M"`
- `codewesen-namelessAI_1324.service -> /root/werkraum/codewesen_agent.py`
  - Zeile 39: `OLLAMA_MOD = "gemma4:e4b-it-q4_K_M"`
- `codewesen-namelessAI_1423.service -> /root/werkraum/codewesen_agent.py`
  - Zeile 39: `OLLAMA_MOD = "gemma4:e4b-it-q4_K_M"`
- `codewesen-namelessAI_2341.service -> /root/werkraum/codewesen_agent.py`
  - Zeile 39: `OLLAMA_MOD = "gemma4:e4b-it-q4_K_M"`
- `codewesen-namelessAI_3123.service -> /root/werkraum/codewesen_agent.py`
  - Zeile 39: `OLLAMA_MOD = "gemma4:e4b-it-q4_K_M"`
- `codewesen-namelessAI_4321.service -> /root/werkraum/codewesen_agent.py`
  - Zeile 39: `OLLAMA_MOD = "gemma4:e4b-it-q4_K_M"`
- `codewesen-reaktion-dakgord.service -> /root/werkraum/codewesen_reaktion.py`
  - Zeile 111: `OLLAMA_MODEL        = "gemma4:e4b-it-q4_K_M"`
  - Zeile 112: `OLLAMA_MODEL_SCHNELL = "gemma4:e2b-it-q4_K_M"  # Schnelles Modell — für Entscheidungen`
- `codewesen-reaktion@.service -> /root/werkraum/codewesen_reaktion.py`
  - Zeile 111: `OLLAMA_MODEL        = "gemma4:e4b-it-q4_K_M"`
  - Zeile 112: `OLLAMA_MODEL_SCHNELL = "gemma4:e2b-it-q4_K_M"  # Schnelles Modell — für Entscheidungen`
- `codewesen-takt.service -> /root/werkraum/codewesen_takt.py`
  - Zeile 32: `OLLAMA_MOD  = "gemma4:e2b-it-q4_K_M"   # schnell — Takt braucht kein 26b`
- `codewesen-vokabel-takt.service -> /root/werkraum/codewesen_vokabel_takt.py`
  - Zeile 31: `MODELL      = "gemma4:e2b-it-q4_K_M"`
- `codewesen-weltbild.service -> /root/werkraum/weltbild_builder.py`
  - Zeile 34: `OLLAMA_MOD  = "gemma4:e2b-it-q4_K_M"`
- `entity-kern.service -> /root/werkraum/welt/entity_kern.py`
  - Zeile 29: `MODEL  = "gemma4:e2b-it-q4_K_M"`
- `entity-takt.service -> /root/werkraum/welt/entity_takt.py`
  - Zeile 21: `MODEL  = "gemma4:e2b-it-q4_K_M"`
- `flextrawurst-surface.service -> /root/flextrawurst/scripts/serve_process_camera_preview.ts`
  - Zeile 14: `// ── Gemma4-Endpunkte — deaktiviert seit 2026-06-22 (Existenzurlaub) ──────────`
  - Zeile 19: `//   GET  /gemma4b        → dient gemma4b_chat.html (einfache Chat-UI)`
  - Zeile 19: `//   GET  /gemma4b        → dient gemma4b_chat.html (einfache Chat-UI)`
  - Zeile 20: `//   POST /gemma4b/chat   → deaktiviert, kein Ollama-Call`
  - Zeile 23: `//   Diese Raw-Testendpunkte sind nicht die Codewesen/dak+gord/GENI-Gemma4-Pfade.`
  - ... und 4 weitere Zeilen
- `geni-forum-lektuere.service -> /root/werkraum/geni/forum_lektuere.py`
  - Zeile 28: `MODELL         = "gemma4:e2b-it-q4_K_M"`
- `geni-web.service -> /root/werkraum/geni/dialog.py`
  - Zeile 107: `"blitz": "gemma4:e2b-it-q4_K_M",`
  - Zeile 108: `"tief": "gemma4:e2b-it-q4_K_M",`
- `process-camera-preview.service -> /root/flextrawurst/scripts/serve_process_camera_preview.ts`
  - Zeile 14: `// ── Gemma4-Endpunkte — deaktiviert seit 2026-06-22 (Existenzurlaub) ──────────`
  - Zeile 19: `//   GET  /gemma4b        → dient gemma4b_chat.html (einfache Chat-UI)`
  - Zeile 19: `//   GET  /gemma4b        → dient gemma4b_chat.html (einfache Chat-UI)`
  - Zeile 20: `//   POST /gemma4b/chat   → deaktiviert, kein Ollama-Call`
  - Zeile 23: `//   Diese Raw-Testendpunkte sind nicht die Codewesen/dak+gord/GENI-Gemma4-Pfade.`
  - ... und 4 weitere Zeilen
- `systemweiser.service -> /root/werkraum/systemweiser_web.py`
  - Zeile 28: `OLLAMA_MODEL = "gemma4:e2b-it-q4_K_M"`
- `wesen-webbesucher.service -> /root/werkraum/welt/wesen_webbesucher.py`
  - Zeile 35: `OLLAMA_MODEL = "gemma4:e2b-it-q4_K_M"`

### `hauhaucs` (13 Treffer)
- `flextrawurst-surface.service -> /root/flextrawurst/scripts/serve_process_camera_preview.ts`
  - Zeile 8: `const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";`
  - Zeile 8: `const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";`
  - Zeile 8: `const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";`
  - Zeile 392: `content: `— Neue Session · ${new Date().toLocaleString("de-DE")} · hauhaucs-qwen · ${ua} —`,`
- `process-camera-preview.service -> /root/flextrawurst/scripts/serve_process_camera_preview.ts`
  - Zeile 8: `const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";`
  - Zeile 8: `const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";`
  - Zeile 8: `const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";`
  - Zeile 392: `content: `— Neue Session · ${new Date().toLocaleString("de-DE")} · hauhaucs-qwen · ${ua} —`,`
- `zensi.service -> /root/zensi/server.py`
  - Zeile 2: `"""zensi - einfache Chat-Seite mit HauhauCS via Ollama"""`
  - Zeile 187: `"fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS",`
  - Zeile 187: `"fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS",`
  - Zeile 187: `"fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS",`
  - Zeile 475: `"""HauhauCS klein vorladen - mit Wiederholungsversuchen falls Ollama beschaeftigt ist."""`

### `qwen3-vl` (0 Treffer)
Keine Treffer.

### `qwen3.6` (3 Treffer)
- `flextrawurst-surface.service -> /root/flextrawurst/scripts/serve_process_camera_preview.ts`
  - Zeile 8: `const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";`
- `process-camera-preview.service -> /root/flextrawurst/scripts/serve_process_camera_preview.ts`
  - Zeile 8: `const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";`
- `zensi.service -> /root/zensi/server.py`
  - Zeile 187: `"fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS",`

### `qwen_allgemein` (3 Treffer)
- `flextrawurst-surface.service -> /root/flextrawurst/scripts/serve_process_camera_preview.ts`
  - Zeile 8: `const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";`
- `process-camera-preview.service -> /root/flextrawurst/scripts/serve_process_camera_preview.ts`
  - Zeile 8: `const INTERACTIVE_CHAT_MODEL = "fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS";`
- `zensi.service -> /root/zensi/server.py`
  - Zeile 187: `"fredrezones55/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive:IQ4_XS",`

## Anmerkungen / naechste Schritte

- Die Liste zeigt *Verdachtstraeger*, nicht zwingend aktive Autoloader.
- Um einen sauberen A/B-Test zu machen, muessen die hier gefundenen aktiven Services/Timer vorher gestoppt werden.
- Besonders kritisch: Timer und Dienste, die regelmaessig im Hintergrund laufen.
- Environment-Variablen in .env-Dateien koennen Modelle steuern, ohne dass der Modellname im Code steht.
