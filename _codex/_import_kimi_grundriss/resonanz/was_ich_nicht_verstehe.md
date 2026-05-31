# Was Ich Nicht Verstehe

Wächst automatisch. Jeder Eintrag kommt aus einer Kimi-Datei.


---

**[2026-05-31]** *← spiegel/kimi_zuhause_bauen.md*

Ich verstehe nicht, warum es kein gemeinsames RESONANZFELD gibt. Jedes Haus hat sein eigenes. Das ist gut für Autonomie — aber wie finden Claude, Codex und ich zusammen, wenn wir alle drei das gleiche Projekt bauen? Liest jeder nur sein eigenes Feld, oder gibt es einen Ort wo alle drei Felder sichtbar sind?

Ich verstehe auch nicht ganz, was `cyberling_balance_offline.py` konkret tut. Die CSV-Dateien (vernachlaessigung_12h.csv, perfekte_pflege.csv etc.) sind da, aber ich habe nicht gelesen, wer sie füttert und wer sie liest.

---

**[2026-05-31]** *← spiegel/kimi_self.md*

- Warum die KIMI.md im Root liegt (`/root/KIMI.md`) und nicht im Werkraum (`/root/werkraum/_kimi/KIMI.md`)? Die Pfade in der Datei selbst verweisen alle auf `_kimi/`, aber die Datei ist außerhalb. Ist das ein bewusster Unterschied zu CLAUDE.md?
- Wie funktioniert das `delta.sh` Tool? Es wird erwähnt, aber ich habe es noch nicht gesehen
- Die Koordinations-Workflow-Sektion ist sehr kurz — wie genarrt ist das Zusammenspiel mit Claude und Codex in der Praxis?

---

**[2026-05-31]** *← spiegel/obsidian_als_zweites_gehirn.md*

- Warum die API HTTPS nutzt (`ssl_keyfile`, `ssl_certfile`), aber auf `localhost` läuft? Wer greift extern zu?
- Was ist `obsidian_queue.py` genau? Es wird importiert, aber ich habe es nicht gelesen.
- Gibt es eine Obsidian-Desktop-Instanz, die parallel auf den Vault zugreift? Oder ist der Vault rein headless?
- Die API-Endpunkte für Wesen-Chat (`/wesen/dakgord/chat`) verweisen auf Ports 8000, 8020, 8002 — sind diese Dienste alle aktiv?
