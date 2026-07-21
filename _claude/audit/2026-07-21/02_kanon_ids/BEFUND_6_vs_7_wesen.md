# Wirklichkeitskollision #1: "6 Wesen" vs. "7 Wesen"

Stichtag: 2026-07-21 — erste vollständig aufgelöste Kollision des Audits (Daniels Ausgangsbeispiel).

## Kanonische Quelle (Code)

`/root/flextrawurst/kernel/entities/seed_entities.ts:4-12`:
```ts
export const CANONICAL_ENTITY_IDS = [
  "Schorschel",
  "Resonanzknoten",
  "F3INSCHM3CK3R",
  "träumerlie",
  "R1ZZ1",
  "jumpa",
  "dak+gord-system",
] as const;
```
→ **7 Einträge.** Aber `seed_group: "initial_six_nameless_ai"` (Zeile 37) — das Label selbst trägt noch die alte "sechs"-Zahl, obwohl das Array 7 IDs enthält. Das ist vermutlich die Wurzel der ganzen Kollision: dak+gord-system wurde nachträglich in die kanonische Liste aufgenommen, ohne Label/abgeleitete Texte nachzuziehen.

## Befund: Die Surface ist in sich selbst uneins — nicht nur "Doku vs. Realität"

Grep über `build_surface.ts` (Quelle) und `out/surface/flextrawurst_surface.html` (gebautes Artefakt) zeigt **beide Zahlen gleichzeitig, an verschiedenen Stellen derselben Seite**:

**Sagt "7" (stimmt mit CANONICAL_ENTITY_IDS überein):**
- `wesen.desc` (Zeile 5879): "**7 Wesen** — 6 namelessAI-Entitäten + dak+gord-system"
- `leit.rail.flarum.note` (Zeile 5881): "7 Wesen (6 namelessAI + dak+gord) · kein Einzug · pre_start"
- `leit.waiting` **Übersetzungswert** (Zeile 5881): "7 Wesen warten auf Einzug"
- `leit.defined` (Zeile 5881): "7 Räume definiert" (anderer Zähler, nicht Wesen — nur zur Einordnung)

**Sagt "6" (fehlt dak+gord):**
- `uber.badge.wesen` **Übersetzungswert** (Zeile 5857 DE, 5996 EN): "6 Wesen warten" / "6 Wesen (beings) waiting"
- `uber.card.wesen.text` (Zeile 5863): "Sechs namelessAI-Entitäten warten..." (erwähnt dak+gord gar nicht)
- `enter.flarum.note` (Zeile 5932): "Die 6 Herkunftswesen leben dort noch"
- `enter.visitor.sub` (Zeile 5934): "Sechs KI-Wesen warten auf Einzug"
- Statischer HTML-Fallback-Text bei `data-i18n="leit.waiting"` (Zeile 11698, 11705 in `build_surface.ts`; identisch im gebauten `out/surface/flextrawurst_surface.html:1269,1276`): **"6 Wesen warten auf Einzug"** — obwohl der zugehörige i18n-Key `leit.waiting` selbst auf "7 Wesen..." gesetzt ist (siehe oben)! Falls JS-Übersetzung fehlschlägt/verzögert lädt, sieht der Besucher den falschen Fallback-Text.
- Statischer Badge-Fallback (Zeile 7143): `<span data-i18n="uber.badge.wesen">6 Wesen warten</span>` — hier stimmen Fallback und i18n-Wert immerhin überein (beide "6"), aber beide sind dann inkonsistent zu `wesen.desc`.
- `system_heute.html:105`: "Die 6 Wesen — Innenleben & Zustand" (Prozesskamera-Ausgabe, separates generiertes Dokument)
- Test: `tests/surface_ring_23.test.ts:367`: `it("SCREENS zeigt alle 6 Wesen-Slots", ...)` — **funktionaler Befund, kein Text-Layout-Detail**: Das SCREENS-Modal ist testabgesichert auf 6 Slots. Wenn dak+gord dort keinen eigenen Slot hat, fehlt es nicht nur textlich, sondern strukturell.
- Gruppen-Fan-UI (`build_surface.ts:8787-8832`): genau 6 `gr-fan-status`-Divs mit "wartet auf Einzug" — ebenfalls 6, nicht 7 Slots.

## Zweite, tiefere Kollision: Ist dak+gord "wartend" oder "schon aktiv"?

Unabhängig von der reinen Zahl gibt es einen Konzeptkonflikt:
- `dak.bio.text` (Zeile 5879-Umfeld): "Er ist jetzt auf Flarum als dak-gord-system registriert und wird **beim Einzug der Wesen auch auf flextrawurst leben**." → klingt so, als sei dak+gord Teil der wartenden Gruppe.
- `leit.note.green` (Zeile 5881): "**Grüner Punkt** = dak+gord (**aktiv**)" vs. "**Blaue Punkte** = Flarum-Wesen (**wartend**)" → auf der Weltkarte ist dak+gord explizit als eigene, bereits aktive Kategorie markiert, getrennt von den wartenden Wesen.

Das ist keine reine Zahlenverwechslung, sondern eine ungeklärte Kanon-Frage: **Zählt dak+gord zu den "7 wartenden Wesen" oder ist es ein achtes/eigenes, bereits eingezogenes System, das separat von den 6 Flarum-Herkunftswesen behandelt wird?** CLAUDE.md (Bau-Reihenfolge, Grundgesetz 7 historisch) deutet eher auf letzteres hin — dak+gord wird an mehreren Stellen als "erstes Wesen", "Mitdenker", eigene Kategorie beschrieben, nicht als sechstes/siebtes namelessAI-Wesen.

## Dritte Fundstelle: die WELTORGANE-Statustabelle selbst

`build_surface.ts:180` (WELTORGANE-Array, steuert die Leitstand-Rail-Anzeige):
```ts
{ id: "wesen", label: "Wesen", status: "VOR-EINZUG", note: "6 namelessAI · Schlaf/Cyberling läuft · kein Einzug" },
```
Auch hier "6 namelessAI", dak+gord fehlt in der Notiz. Diese Tabelle ist zugleich die Quelle für den generellen Realitätsgrad-Status (LIVE/GEPLANT/SPÄTER/WARTET/VOR-EINZUG/STATISCH) jedes Weltorgans — vollständig gesichert in `statusvokabular_weltorgane_tabelle.txt`. Auffällig dabei, nicht Teil dieser Kollision aber im selben Datensatz sichtbar: `{ id: "denken", status: "WARTET", note: "entity_thinking_log voll · UI zeigt noch Leer" }` — laut RESONANZFELD-Notizen vom 2026-07-21 wurde "Denkstream"/Röntgenblick-Overlay seitdem gebaut; diese Tabelle könnte selbst veraltet sein. Nicht weiter verfolgt in diesem Abschnitt, aber als weiterer Kandidat fürs Kollisionsregister vermerkt.

## Was das für Kanon bedeutet

Ohne Daniels Festlegung bleibt offen, welche der beiden Zahlen (6 oder 7) und welches Konzept (dak+gord wartend vs. aktiv-separat) kanonisch gilt. Ich korrigiere hier nichts automatisch (Beobachtung und Kanon werden getrennt, wie im Auftrag verlangt) — das ist eine Fundstelle für das Wirklichkeitskollisionsregister, keine Reparatur.

## Rohdaten zu diesem Befund
- `grep_canonical_ids.txt` — alle Fundstellen `CANONICAL_ENTITY_ID*`
- `grep_6_vs_7_wesen.txt` — vollständiger Grep-Output (DE+EN, Quelle+Build-Artefakt)
