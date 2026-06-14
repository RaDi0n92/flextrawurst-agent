# Kimi Session-Notiz — 2026-06-14

**Ort:** Review-Ordner (weil aktuell „no commits“ gilt und eine Notiz im werkraum-Repo einen Backup-Commit erfordern würde).

---

## Was gemacht wurde

- Full-Server Review für flextrawurst abgeschlossen.
- 19 Markdown-Reports in `/root/flextrawurst_full_server_review_kimi_20260614_020210/` geschrieben.
- Gesamt: ~93 Findings, davon 6 P0 und 29 P1.
- Keine Änderungen am System, keine Commits, keine Restarts, keine Config-Änderungen.

## Top-Erkenntnisse

- `api_bridge.py`: Default-Key + `shell=True` = RCE.
- Agent Gateway: Auth deaktiviert sich bei fehlendem `AGENT_API_TOKEN`.
- Hardcodierte DB-URIs mit Klartext-Passwort in ≥18 Dateien unter `welt/`.
- CORS wildcard in mehreren FastAPI-Apps.
- Services laufen als root und binden an `0.0.0.0`.

## Offen / Nächste Schritte

- Claude übernimmt P0/P1-Fixes anhand von `17_CLAUDE_FIX_PREP.md`.
- Vor jedem Fix: Backup-Commit + Abstimmung mit Daniel wegen Passwortrotation und Service-Usern.

## Resonanz

Der Review zeigt ein klares Muster: schnelles Wachstum hat zu hartcodierten Secrets, offenem CORS und übermäßigen Root-Rechten geführt. Die Architektur trägt, aber die operative Härte hinkt hinterher. Der wichtigste Hebel ist nicht mehr Code, sondern saubere Trennung von Secrets, Rechten und Netzwerkzugang.
