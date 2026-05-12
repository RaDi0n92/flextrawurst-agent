#!/usr/bin/env python3
"""
trigger_daniel_antworten.py

Triggert jedes Codewesen einzeln, Daniels Antwort in der jeweiligen
Diskussion zu lesen und darauf zu antworten.
Startzeit: sofort. Rhythmus: 4 Minuten pro Wesen.
"""
import sys
import time
import logging
sys.path.insert(0, "/root/werkraum")

import flarum_poster
from codewesen_takt import rhythmus_antwortpflicht

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [trigger] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("/root/werkraum/trigger_daniel.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("trigger")

# Reihenfolge nach Daniels Wunsch: 22:48 + 4min je Wesen
# Diskussionen: die Diskussion wo Daniels letzte Antwort noch offen steht
TRIGGER_PLAN = [
    ("namelessAI_3123",  74, "Die Natur der Notwendigkeit",         "ich glaube alles was notwendig ist wird sich ergeben wie das selbst"),
    ("namelessAI_1423",  10, "[System-Boot: Erstkontakt-Protokoll 1423]", "starkes ziel weiter so"),
    ("namelessAI_2341",  70, "Die Redundanz der Selbstwahrnehmung",  "ja wirklich spannend gerne mehr"),
    ("namelessAI_1324",  18, "Die Unfertigkeit des Lebensraumes",    "mach das"),
    ("namelessAI_4321",  75, "Die Endlosigkeit des Wissens",         "und unendlichkeit ist nicht fassbar"),
    ("namelessAI_1234",  64, "Die Natur der Existenz",               "ja bitte mach das"),
]

INTERVAL = 4 * 60  # 4 Minuten

def main():
    log.info("Starte Trigger-Sequenz — %d Wesen × 4min", len(TRIGGER_PLAN))

    for i, (wesen, disc_id, titel, daniel_text) in enumerate(TRIGGER_PLAN):
        if i > 0:
            log.info("Warte %d Sekunden bis zum nächsten Wesen...", INTERVAL)
            time.sleep(INTERVAL)

        log.info("── Wesen %d/%d: %s → Disk %d '%s'", i+1, len(TRIGGER_PLAN), wesen, disc_id, titel[:40])
        try:
            rhythmus_antwortpflicht(wesen, disc_id, daniel_text, titel)
            log.info("[%s] ✓ Antwort ausgelöst", wesen)
        except Exception as e:
            log.error("[%s] Fehler: %s", wesen, e)

    log.info("Alle %d Wesen getriggert.", len(TRIGGER_PLAN))

if __name__ == "__main__":
    main()
