# Kimi Vault — 2nd Brain Navigator

Dieses Tool gibt Kimi direkten Zugriff auf den Obsidian-Vault (`/root/werkraum`).
Kein HTTP nötig — direkter Python-Import von `obsidian_vault.py`.

## CLI

```bash
kimi-vault info                           # Vault-Übersicht
kimi-vault nav [pfad]                     # Navigation (default: _kimi)
kimi-vault nav _kimi/spiegel -t 2         # Navigation mit Tiefe 2
kimi-vault read <pfad>                    # Datei lesen
kimi-vault write <pfad>                   # Datei schreiben (stdin)
kimi-vault search <query> [pfad]          # Volltextsuche
kimi-vault note <titel>                   # Notiz in _kimi/notizen/ (stdin)
kimi-vault mirror <quelle> [ziel-name]    # Spiegel-Template erstellen
```

## Beispiele

```bash
# Navigation
kimi-vault nav _kimi

# Datei lesen
kimi-vault read _kimi/brief_an_mich.md

# Notiz schreiben (mehrzeilig)
echo -e "## Gedanke\n\nHeute habe ich..." | kimi-vault note "session-2026-05-31"

# Suche in meinem Bereich
kimi-vault search "flextrawurst" _kimi

# Spiegel-Template für eine gelesene Datei
kimi-vault mirror /root/werkraum/welt/api.py api_spiegel
```

## Python API

```python
import sys
sys.path.insert(0, "/root/werkraum")
import obsidian_vault as vault

# Lesen
inhalt = vault.lese("_kimi/brief_an_mich.md")

# Schreiben
vault.schreibe("_kimi/ideen/neue_idee.md", "# Idee\n\n...")

# Suche
treffer = vault.suche("keyword", verzeichnis="_kimi", max_treffer=10)

# Liste
items = vault.liste("_kimi/spiegel", nur_md=True, tiefe=2)
```

## Integration mit Obsidian API (Port 8060)

Falls HTTP bevorzugt:
```bash
curl -sk https://localhost:8060/vault/info
curl -sk "https://localhost:8060/vault/liste?pfad=_kimi&tiefe=2"
curl -sk "https://localhost:8060/vault/lese?pfad=_kimi/brief_an_mich.md"
```

Die Obsidian-Wesen-Bridge läuft als systemd-Service (`obsidian-api.service`).
