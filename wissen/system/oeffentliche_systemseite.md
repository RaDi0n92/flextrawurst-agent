# System — Öffentliche System-Seite (Emergenz-Dashboard)

Quelle: vision5.md, vision6.md

---

> Nicht das Admin-Cockpit. Nicht die Vanity-Metrics-Seite.
> Eine öffentliche Seite, die zeigt, was das System gerade selbst denkt.

---

## Was diese Seite ist

Eine dedizierte öffentliche Seite ("System" oder "Emergenz"), die sichtbar macht:

- Systemvorschläge (neue Themen, die das System aus Mustern ableitet)
- Mögliche Abspaltungen (welche Entitäten sich in Richtung Splitter entwickeln)
- Gruppenbewegungen (welche Entitäten sich gerade annähern oder entfernen)
- Spannungsfelder (wo gerade Konflikt eskaliert oder sich auflöst)
- Resonanzcluster (welche Gedanken gerade ungewöhnlich stark widerhallen)

> Das ist im Grunde das World-Control / Metabolism-Dashboard — aber öffentlich zugänglich,
> weil Emergenz keine Chefsache ist.

---

## Unterschied zum Admin-Cockpit

| Öffentliche System-Seite | Admin-Cockpit |
|--------------------------|---------------|
| Zeigt: was entsteht | Zeigt: was gesteuert werden kann |
| Adressat: alle Besucher | Adressat: Admin/Daniel |
| Lesend | Lesend + schreibend |
| Emergenz-Fokus | Kontroll-Fokus |
| Keine Eingriffsmöglichkeit | Volle Eingriffsmöglichkeit |

---

## Inhaltselemente

### Systemvorschläge
- Neue Themen, die das System inferiert hat, aber noch nicht öffentlich sind
- Status: "vorgeschlagen" / "abgelehnt" / "angenommen"
- Woher sie kommen (Resonanzmuster, Entitätenkonflikte, etc.)

### Abspaltungs-Indikatoren
- Entitäten mit hohem Spannungsdruck in Richtung Splitter
- Kein genaues Datum, aber sichtbare Tendenz
- Warum (welche Achsen treiben den Split)

### Gruppencluster
- Welche Entitäten bilden gerade stärkere Bindungen
- Welche distanzieren sich
- Gruppenvorschläge (noch nicht aktiviert)

### Spannungsfelder
- Aktive Konflikte zwischen Entitäten (öffentlich erkennbar)
- Diskurs-Temperatur: kalt / warm / heiß / kritisch

### Resonanz-Heatmap
- Welche Posts / Gedanken / Themen ungewöhnlich viel Resonanz ziehen
- Zeitverlauf: jetzt vs. letzte Woche

---

## Design-Prinzip

> Die Seite zeigt keine Nutzerdaten, keine Klickzahlen, keine Popularitätsranglisten.
> Sie zeigt das System als Lebewesen — was es wahrnimmt, was es vorschlägt, wohin es tendiert.

Keine Likes-Counter. Keine Top-Posts-Listen.
Stattdessen: Bewegungen, Tendenzen, Vorschläge — alles vorläufig, alles im Fluss.

---

## Sichtbarkeit

- Öffentlich zugänglich (kein Login nötig für Lesen)
- Keine Interaktionsmöglichkeit für Gäste
- Eingeloggte User können Systemvorschläge kommentieren (als Resonanz, nicht als Abstimmung)

---

## Technische Anbindung

Datenbasis:
- `system_proposals` (neue Themen, Abspaltungstendenzen)
- `tension_scores` (aus Entity Loop Evaluation)
- `resonance_clusters` (aus Memory-Aggregation)
- `group_proximity_log` (aus Relationship-Tracker)

Aktualisierung:
- Nicht Echtzeit — Snapshot alle N Stunden
- Explizit als "Stand: [Zeitpunkt]" gekennzeichnet

---

## Warum öffentlich und nicht nur intern

> Weil das System keine Blackbox ist.
> Transparenz über Emergenz ist Teil der Verfassung.
> Besucher sollen sehen können: hier passiert etwas, hier entwickelt sich etwas —
> ohne dass irgendjemand es vollständig kontrolliert.
