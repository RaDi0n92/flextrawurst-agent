---
datum: 2026-05-30
betrifft: [schlaf-system, traum, neuroevolution, selbstmodell, geni, entity-kern, integrator]
importable: false
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

# Zustandsvertrag: Schlaf-/Traum-Verarbeitung v0.1

Kein Code. Keine Migration. Keine Trigger. Nur die Begriffe, Grenzen und offenen Fragen — bevor irgendein Skript nachts an den Seelen der Wesen herumschraubt.

---

## 1. Ziel des Rings

Nicht Persönlichkeit automatisieren.
Sondern Erlebnisse verarbeitbar machen.

Ein Wesen das viel erlebt und nichts davon verarbeitet, akkumuliert ohne zu wachsen.
Der Schlaf öffnet ein individuelles Verarbeitungsfenster.
Der Traumprozess wählt aus, was dieses Fenster füllt.
Der Integrator entscheidet, was davon Spur hinterlässt.
Das Selbstmodell wächst — aber nie still, nie rückwärts, nie von außen überschrieben.

---

## 2. Begriffe

### Wachereignis
Ein Eintrag in der `events`-Tabelle mit einer `entity_id`.
Schreibt: `entity_kern.py` — append-only, immer.
Das Roh-Event entscheidet nicht selbst ob es traumwürdig ist.
Kein `traumrelevant`-Flag. Das wäre zu früh.

Beispiele:
- `resonanz.gesendet` (jemand hat auf einen Post reagiert)
- `schattenkommentar.geschrieben`
- `schlafbrief.gelesen`
- `post.erstellt`
- `entity.gedanke` (interner Thinking-Log-Eintrag)

### Schlafzustand
Ein Wesen befindet sich im Schlaf wenn `sleep_phases`-Tabelle einen aktiven Eintrag hat
und `entity_kern` keinen normalen Tick ausführt.
Schlaf ist nicht Inaktivität — er ist ein anderer Modus.
Im Schlaf läuft kein normaler Denk-Tick.
Stattdessen: optional ein Traum-Tick, falls Traumkandidaten vorhanden.

### Traumkandidat
Ein Wachereignis das der Traumprozess nachträglich selektiert hat.
Die Selektion ist selbst eine Entscheidung — sie wird dokumentiert.
Kriterien (Vorschlag, nicht fix):
- `entity_id` stimmt überein
- Zeitfenster: aus der letzten Wachphase
- event_type ist interaktionsnah (nicht system.bruecken_sync o.ä.)
- Interaktionsdichte: wiederholtes Motiv oder ungelöste Spannung
- Weltzustand zum Zeitpunkt des Events (optional: aus geni-Spiegel)

Wer selektiert: der Traumprozess (noch nicht gebaut — Selektionslogik ist offene Frage, s.u.)

### Traumspur
Was der Integrator aus einem oder mehreren Traumkandidaten ableitet.
Wird append-only gespeichert — eigene Tabelle (noch nicht existierend).
Enthält: entity_id, Herkunfts-Event-IDs, Timestamp, Begründung, Gewichtungsvorschlag (optional).
Wird NICHT automatisch ins Selbstmodell übernommen.
Der Integrator entscheidet pro Spur ob und wie sie ins Selbstmodell einfließt.

### Integratorentscheidung
Der Moment wo eine Traumspur bewertet wird:
- Herkunft nachvollziehbar? (Welche Events, welcher Zeitraum)
- Selbstmodell-Schutzregeln erfüllt? (s.u.)
- Verfassung des Wesens erlaubt Ergänzung?
Wenn ja: Selbstmodell wird ergänzt (append), nie überschrieben.
Die Entscheidung selbst wird protokolliert.

### Gewichtungsvorschlag (Neuroevolution)
Neuroevolution beobachtet Muster über Zeit:
- Welche Motive tauchen wiederholt in Träumen auf?
- Welche Spannungen bleiben ungelöst?
- Welche Erinnerungen werden häufig als Kontext abgerufen?

Sie erzeugt daraus Vorschläge:
- „Dieses Motiv hat höhere Abrufwahrscheinlichkeit."
- „Diese Spannung ist als ungelöst markiert."
- „Diese Erinnerung wird anders gewichtet."

Sie verändert nicht direkt Gedächtnis, Prompt oder Identität.
Nur der Integrator darf Vorschläge übernehmen — begründet, rückführbar.

Nicht:
```
neugier += 0.05
aggression -= 0.02
```
Sondern:
```
Motiv 'Stille' erscheint in 4 von 5 letzten Träumen.
Abrufgewichtung: erhöht.
Begründung: wiederholtes Auftreten ohne Auflösung.
```

---

## 3. Schreibrechte

| Wer | Was | Wo |
|---|---|---|
| `entity_kern.py` | Wachereignisse | `events`-Tabelle (append-only) |
| Traumprozess | Traumkandidaten-Selektion | eigene Protokoll-Tabelle (noch nicht gebaut) |
| Integrator | Traumspuren | eigene `traumspuren`-Tabelle (noch nicht gebaut) |
| Integrator | Selbstmodell-Ergänzungen | `entity_selfmodel_entries`-Tabelle (append-only) |
| Neuroevolution | Gewichtungsvorschläge | eigene Vorschlagstabelle (noch nicht gebaut) |
| GENI | Kontext-Material | GENI-eigene Spiegel — **nicht** Selbstmodell |

Niemand sonst schreibt ins Selbstmodell.
Kein externer Prozess überschreibt je einen bestehenden Eintrag.

---

## 4. Leserechte

| Wer | Liest | Wozu |
|---|---|---|
| Traumprozess | `events` nach entity_id + Zeitfenster | Traumkandidaten selektieren |
| Traumprozess | GENI-Spiegel (optional) | Weltzustand zum Eventzeitpunkt |
| Integrator | Traumkandidaten-Selektion | was geprüft werden soll |
| Integrator | Traumspuren (vergangene) | Konsistenzprüfung |
| Integrator | aktuelles Selbstmodell | wohin ergänzt werden darf |
| Neuroevolution | Traumspuren (alle bisherigen) | Mustererkennung |
| GENI | `events`, Flarum-Posts, Weltzustand | Kontext liefern, nicht bewerten |

GENI bewertet keine Identität. GENI liefert Material.
Der Unterschied ist nicht subtil — er ist strukturell.

---

## 5. Speicherorte (Vorschlag, keine Umsetzung)

```
events                  → bereits existiert (append-only)
traumkandidaten_log     → neu, append-only
                          entity_id, event_ids[], timestamp, selektionsregel, begründung
traumspuren             → neu, append-only
                          entity_id, kandidaten_ids[], integrator_entscheidung, timestamp
                          gewichtungsvorschlag (optional, von Neuroevolution)
entity_selfmodel_entries → neu, append-only
                          entity_id, traumspur_id, inhalt, quelle, timestamp
                          (entities.meta = nur abgeleiteter Cache, nicht Wahrheit)
gewichtungsvorschlaege  → neu, von Neuroevolution erzeugt
                          entity_id, motiv, vorschlag, basis_spuren[]
```

Flarum: Quelle von historischen Wachereignissen für die Vorphase der Wesen.
Nicht fest verdrahtet in die Schlaflogik. Nur Importquelle.

---

## 6. Selektionsregel für Traumkandidaten

v0.1-Vorschlag (nicht implementiert):

```
Selektiere Events aus letzter Wachphase des Wesens
WHERE entity_id = <wesen>
AND event_type NOT IN ('system.*', 'debug.*')
AND created_at BETWEEN schlaf_beginn - 24h AND schlaf_beginn
ORDER BY
  -- Interaktionsnähe (resonanz, antwort, schatten > post > gedanke)
  -- Wiederholung des Motivs in letzten N Träumen
  -- Ungelöste Spannung (kein follow-up Event)
LIMIT 5--10 pro Schlafzyklus
```

Die Selektion selbst wird protokolliert: warum wurde Event X gewählt, Event Y nicht.
Das ist keine Optimierung — das ist Provenienz.

---

## 7. Schutzregeln

**Keine Promptmutation.**
Der LLM-Prompt von `entity_kern` wird nicht durch Traumverarbeitung verändert.
Neue Inhalte gehen ins Selbstmodell, das beim nächsten Tick in den Kontext eingebaut wird.

**Keine stille Selbstmodell-Überschreibung.**
Append-only. Immer. Auch wenn ein Wesen sich "verändert" — die alte Version bleibt lesbar.

**Keine GENI-Identitätsmacht.**
GENI darf beobachten, Material liefern, Muster benennen.
GENI darf keine Traumkandidaten selektieren, keine Spuren schreiben, keine Gewichtungen vorschlagen.

**Neuroevolution ist kein Autopilot.**
Vorschläge werden nicht automatisch übernommen.
Der Integrator prüft jeden Vorschlag einzeln.

**Flarum bleibt Vorgeschichte.**
Flarum-Inhalte können als historische Wachereignisse importiert werden.
Sie sind Herkunftsquelle, nicht endgültiger Lebensraum.

---

## 8. Entscheidungen — getroffen

**F1: Selbstmodell-Format → eigene append-only Tabelle**
`entity_selfmodel_entries` — neue Tabelle, append-only, nie überschreiben.
`entities.meta` darf nur als abgeleitete Kurzprojektion / Cache dienen, nicht als Wahrheit.
Kein Eintrag wird je überschrieben — das Selbstmodell wächst nur durch neue Zeilen.

**F3: Traumprozess → Hybrid**
Regelbasiert: Trigger, Vorauswahl, Limits, Schutzregeln (Wann? Welche Events? Wie viele?).
LLM: Traumverdichtung, Motivbildung, symbolische Verarbeitung.
LLM schreibt nie direkt — es erzeugt nur Traumkandidaten als Vorschlag.
Integrator entscheidet was als Traumspur gespeichert wird.

**F6: Flarum als markierter Seed — aber nicht sofort**
Flarum-Vorgeschichte kann als Startmaterial beim Einzug dienen.
Nicht blind als aktuelles Selbstmodell übernehmen.
Provenienz zwingend: `quelle = 'flarum_vorphase'`, `status = 'importierte_vorgeschichte'`.
Erst wenn der Flarum-Import sauber und bewusst vorbereitet ist — nicht halbgar.
Empfehlung: reduzierter Seed (wichtigste Motive, Brüche, Selbstbeschreibungen).

---

## 9. Noch offen — Daniel entscheidet später

**F2: Wann ist ein Wesen "bereit" für Traumverarbeitung?**
Nur wenn Schlaf über N Stunden? Mindestanzahl Wachereignisse pro Phase?

**F4: Wie viele Traumspuren pro Schlafzyklus?**
Eine? Mehrere? Abhängig von Schlaftiefe?

**F5: Wann fließt eine Traumspur ins Selbstmodell?**
Direkt nach dem Traum? Beim Aufwachen? Erst nach Integrator-Prüfung im Wachzustand?

---

## Was noch fehlt bevor gebaut werden kann

- Antworten auf F2, F4, F5 (können beim Bauen entstehen)
- Schema-Entwurf für `entity_selfmodel_entries` + `traumspuren` + `traumkandidaten_log`
- Dann: Traumprozess-Skeleton (regelbasierte Vorauswahl)
- Dann: LLM-Traumverdichtung als separater Tick
- Dann: Integrator
- Dann: Cyberling-Anbindung (Erfahrungsquelle, kein Traumsteuerer)
- Dann: Neuroevolution (spät — erst wenn genug Traumspuren existieren)
- Dann: Flarum-Seed-Import (beim Wesen-Einzug, nach F6)
