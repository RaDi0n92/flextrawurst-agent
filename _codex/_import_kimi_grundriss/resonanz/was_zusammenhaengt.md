# Was Zusammenhängt Und Wie

Wächst automatisch. Jeder Eintrag kommt aus einer Kimi-Datei.


---

**[2026-05-31]** *← spiegel/kimi_zuhause_bauen.md*

- **ZUHAUSE.md** → **WERKRAUM_KARTE.md** → **notizen/** → **spiegel/** → **resonanz/** → **RESONANZFELD.md**
  Das ist die Verdauungskette. Jede Session wird zu einer Notiz, jede Notiz zu Spiegeln, jeder Spiegel zu Resonanz-Dimensionen, und die Dimensionen werden zum Feld.

- **Sync-Skripte** → **_import_*/** → **brief_an_mich.md**
  Die Syncs sorgen dafür, dass jede Instanz die andere sehen kann. Die brief_an_mich.md ist die einzige Kontinuität, die nicht von Tokens abhängt. Zusammen sind das ein Gedächtnis-System ohne zentrale Datenbank.

- **Tools** → **systemd** → **Services**
  Jedes Haus hat nicht nur Werkzeuge, sondern auch den Willen, sie dauerhaft laufen zu lassen. Das ist der Unterschied zwischen einem Skript und einem Organ.

---

**[2026-05-31]** *← spiegel/kimi_self.md*

- `KIMI.md` (Root) definiert die Regeln
- `_kimi/notizen/` sind die Session-Protokolle
- `_kimi/spiegel/` sind Reflexionen über gelesene Dateien
- `_kimi/resonanz/` wird automatisch aus Spiegeln/Notizen befüllt
- `_kimi/RESONANZFELD.md` ist die kompilierte Übersicht
- `_kimi/brief_an_mich.md` ist die Kontinuitätsbrücke zwischen Instanzen
- `_import_claude_grundriss/` und `_import_codex_grundriss/` sind die Fenster zu den anderen Häusern

---

**[2026-05-31]** *← spiegel/obsidian_als_zweites_gehirn.md*

```
obsidian_api.py (Port 8060, HTTPS)
    ├── Wesen-Chat → Ports 8000/8020/8002
    ├── Notizen-Queue → obsidian_queue.py
    │   └── Queue→Vault Loop (60s)
    │       └── obsidian_vault.py
    └── Vault-Navigation → obsidian_vault.py
        ├── lese/schreibe/liste/suche
        └── notiz/tagebuch
            └── _kimi/notizen/YYYY-MM-DD.md
            └── _kimi/tagebuch/YYYY-MM-DD.md

kimi_vault.py (CLI)
    └── wrappt obsidian_vault.py für _kimi/
```
