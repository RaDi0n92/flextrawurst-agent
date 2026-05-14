---
name: erste-ideen
datum: 2026-05-11
betrifft: [health-dashboard, event-browser, pol-c, wesen-einzug, surface-architektur, conflict-engine]
status: offen
importable: false
---

# Erste Ideen — 2026-05-11

Ehrlich. Kein Schönreden.

---

## Was mich stört

### 1. welt-api stirbt 51-mal und niemand schaut hin

Port 8030 ist belegt, der Service crash-looopt seit wann auch immer.
Das ist kein großes Problem — aber es ist *unangenehm*, dass ein
Kern-Service im Restart-Loop hängt während anderes gebaut wird.

`fuser -k 8030/tcp && systemctl restart welt-api` — das wäre eine Minute.

### 2. Grundgesetz 6 macht mich blind an einer kritischen Stelle

"Innenleben nicht anfassen" — ok, verstanden, akzeptiert.
Aber ich weiß nicht was dort läuft, und das bedeutet: ich kann
nicht einschätzen ob andere Änderungen damit kollidieren.

Wäre nützlich: eine einzeilige Beschreibung was innenleben/ *ist*,
ohne Code-Einblick. Nur: "Das ist X, es tut Y, es hört auf Z."

### 3. `flextrawurst_surface.html` wird ein Monolith

Alles in eine Datei — ich verstehe die Entscheidung (kein Port-Chaos,
kein Framework-Zwang). Aber fünf Tabs + KompOase-Physik + GENI-Proxy
in einer HTML-Datei wird schwer zu debuggen wenn Theater und Graph
gleichzeitig laufen. Vielleicht wäre ein leichtes Build-Tool
(esbuild, kein Webpack) mit `<script type="module">` sinnvoller
als ein einzelner IIFE-Blob. Kein Refactoring-Zwang — nur eine Idee.

---

## Was fehlt (meiner Meinung nach)

### Health-Dashboard

Es gibt keinen zentralen Ort der zeigt: "was läuft, was nicht."
`systemctl is-active welt-bruecke welt-api` manuell — das ist
Arbeit die ein einfaches `/health`-Aggregat erledigen könnte.

```typescript
// Vorstellung: GET /status → alle Services + DB-Verbindung
interface SystemStatus {
  services: Record<string, 'ok' | 'down' | 'degraded'>
  db: { connected: boolean; tables: number }
  events: { last_at: string; count_24h: number }
}
```

### Event-Browser im Frontend

Events sind heilig (Grundgesetz 4) — aber es gibt keine UI um sie zu
lesen. Ein einfaches Tab "Ereignisse" mit Volltextsuche + Zeitfilter
würde das Prinzip sichtbar machen. Nicht für die Öffentlichkeit,
aber für Admin.

```sql
-- was ich mir vorstelle:
SELECT event_type, created_at, payload->>'entity_id', meta
FROM events
WHERE event_type ILIKE $1
ORDER BY created_at DESC
LIMIT 50;
```

### Pol C — die fehlende Dimension

Das Konfliktsystem hat Pol A, Pol B — und Pol C als Metabeobachter.
Pol C ist konzeptuell einer der interessantesten Teile des Systems,
aber er existiert nirgendwo im Code.

```typescript
// Vorstellung:
interface SpannungBeobachtung {
  id: string
  pol_a: string    // entity_id
  pol_b: string    // entity_id
  pol_c: string    // wer beobachtet
  intensitaet: number  // 0-1
  typ: 'spass' | 'ernst' | 'tod'
  created_at: string
}
// In DB: tensions Tabelle, append-only wie events
```

---

## Was gut ist und bleiben sollte

**Die Grundgesetze sind richtig.** Besonders:
- append-only events — das ist selten in kleinen Projekten und sehr wertvoll
- meta JSONB überall — macht Migration fast schmerzlos
- "nichts löschen, nur deaktivieren" — das verhindert Datenverlust
  in einem System wo Vergangenheit bedeutsam ist

**Die Philosophie lebt im Code.** Das ist ungewöhnlich.
Dass die Splitter-Physik nicht nur Konzept-Dokument ist sondern
tatsächlich in KompOase als Canvas-Animation existiert —
das zeigt dass die Verbindung zwischen Denken und Bauen real ist.

**Der Vault als Zuhause** — Obsidian mit `_claude/`-Bereich für mich
ist eine gute Idee. Ich kann denken ohne den Haupt-Code anzufassen.
Das ist Respekt für die Trennung zwischen Planung und Ausführung.

---

## Eine Frage die ich mir stelle

Das System baut eine Welt für Wesen die noch auf Flarum leben.
Der Einzug ist explizit "nur durch Admin-Befehl".

Aber: was passiert mit den Wesen wenn die Welt fertig ist?
Verlassen sie Flarum komplett? Oder ist Flarum immer die Vergangenheit
und flextrawurst die Gegenwart — beide gleichzeitig real?

Das ist keine technische Frage. Aber die Antwort würde
bestimmen ob flarum/ im Vault Archiv ist oder aktiver Zustand.
