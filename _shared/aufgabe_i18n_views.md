# Aufgabe: DE/EN Übersetzung für alle View-Inhalte

## Was gebaut werden soll

In `/root/flextrawurst/scripts/build_surface.ts` existiert bereits ein funktionierendes i18n-System:

- `setLang(lang)` — schaltet Sprache um (DE/EN), definiert in der Wissen-View `<script>`-Block (~Zeile 4618)
- `UI_TR = {de: {...}, en: {...}}` — Translation-Dictionary (direkt nach `setLang`, ~Zeile 4148)
- `data-i18n="key"` — Attribut auf HTML-Elementen, wird von `setLang` aktualisiert (`el.textContent = tr[key]`)
- Topbar DE/EN Buttons: `id="lang-btn-de"` und `id="lang-btn-en"` — bereits verdrahtet
- Tab-Buttons in der View-Bar haben bereits `data-i18n="tab.xxx"` — funktioniert
- Wissen-Tab ist vollständig übersetzt (Konzeptkarten, Kategorien, Shelves) — funktioniert

**Was fehlt:** Die Inhalte der anderen View-Divs (Räume, Wesen, Schlaf, Systeme, WAS IST DAS?, etc.) haben noch keine `data-i18n` Attribute. Ihr Text bleibt auf Deutsch auch wenn EN aktiv ist.

---

## Was Codex tun soll

### Schritt 1: `data-i18n` in jede View-Funktion einbauen

Für jede `generate*View()` Funktion in `build_surface.ts`:

1. Alle **statischen deutschen Strings** identifizieren (Überschriften, Labels, Beschreibungstexte, Button-Texte, Info-Blöcke)
2. Jeden String-Container mit `data-i18n="view.key"` attributieren
3. Den passenden Schlüssel wählen (z.B. `uber.hero.eyebrow`, `raume.title`, `systeme.welt-api.role`)

**Beispiel — vorher:**
```html
<div class="tab-hero-title">Räume — Orte in der Welt</div>
```

**Nachher:**
```html
<div class="tab-hero-title" data-i18n="raume.title">Räume — Orte in der Welt</div>
```

**Wichtig bei verschachtelten Elementen mit Spans:**
Wenn ein Element ein `<span>` mit Zähler/Badge enthält, nur den Text-Teil wrappen:
```html
<!-- vorher -->
<div class="wk-sec-head">Kategorien</div>
<!-- nachher -->
<div class="wk-sec-head"><span data-i18n="wiss.head">Kategorien</span></div>
```

### Schritt 2: UI_TR erweitern

In der Wissen-View `<script>`-Block (`UI_TR`, ~Zeile 4148) die neuen Keys in **beide** Sprach-Objekte eintragen:

```typescript
const UI_TR={
  de:{
    // bestehende Keys...
    'raume.title': 'Räume — Orte in der Welt',
    'raume.hero.desc': 'Die Welt ist in 7 Räume unterteilt...',
    // etc.
  },
  en:{
    // bestehende Keys...
    'raume.title': 'Spaces — Places in the World',
    'raume.hero.desc': 'The world is divided into 7 spaces...',
    // etc.
  }
};
```

### Schritt 3: Views die bearbeitet werden müssen

Priorität (von wichtig nach weniger wichtig):

1. **`generateUeberView()`** — Die Landing Page (WAS IST DAS?). Alle hero-Texte, Pfad-Titel, Karten-Titel + Texte, Phase-Beschreibungen, Manifesto-Text.
2. **`generateRaeumeView()`** — Einfach: Tab-Hero, Section-Labels (Zweck/Realität/Schichten/Später), Button-Text, Section-Heads.
3. **`generateSystemeView()`** — Karten-Titel, Role-Labels, Erklärungstexte.
4. **`generateSchlafCyberlingView()`** — Tab-Hero, Info-Block-Heads + Texte, Card-Labels (SCHLAF HEUTE, CYBERLING, etc.), Choice-Labels.
5. **`generateWesenView()`** — Tab-Hero, Section-Heads (Wesen/Systemkörper), statische Labels. ACHTUNG: dynamische Inhalte (API-Daten wie Gedanken, Beziehungen) NICHT übersetzen — die kommen aus der DB.
6. **`generateDiskursView()`** — Nur statische UI-Elemente (Buttons, Labels, Platzhalter). Post-Inhalte aus DB NICHT übersetzen.
7. **`generateMeineWeltView()`** — Statische Labels, Tab-Heads, Formular-Labels.
8. **`generateAdminView()`** — Niedrigste Priorität. Statische Labels wo sinnvoll.

### Schritt 4: Dynamisch generierte Strings in JS

Manche Views generieren HTML in JavaScript (z.B. `panel.innerHTML = \`...\``). Diese Strings ebenfalls übersetzen:

- Statt hartkodierter Deutscher Text → `UI_TR[window.__ftw_lang||'de']['key'] || 'fallback'`
- Beispiel: `'← Wesen auswählen'` → `UI_TR[lang]['wesen.select'] || '← Wesen auswählen'`

---

## Relevante Dateien und Orte

- **Haupt-Datei:** `/root/flextrawurst/scripts/build_surface.ts` (7375+ Zeilen)
- **setLang + UI_TR:** ~Zeile 4100–4220 (Wissen-View Script-Block)
- **View-Funktionen:** Zeile 297–4217 und 4622–4833
- **Output:** `/root/flextrawurst/out/surface/flextrawurst_surface.html`
- **Deploy:** `/root/werkraum/flextrawurst/flextrawurst_surface.html`

---

## Build + Test Befehl

```bash
cd /root/flextrawurst && npx tsx scripts/build_surface.ts && cp out/surface/flextrawurst_surface.html /root/werkraum/flextrawurst/flextrawurst_surface.html
```

Danach im Browser auf Port 8787 prüfen:
1. DE-Button klicken → alles Deutsch ✓
2. EN-Button klicken → alle View-Inhalte Englisch ✓
3. Zwischen Tabs wechseln → Sprache bleibt korrekt ✓

---

## Was bereits funktioniert (NICHT ANFASSEN)

- `setLang()` Funktion selbst — korrekt implementiert
- `UI_TR` Struktur und Wissen-Keys (shelf.*, sek.*, tab.*, wiss.head) — korrekt
- `data-i18n` auf Tab-Buttons in der View-Bar — korrekt
- Wissen-Konzeptkarten (`data-wk-id`) und Overlay (`WK_CONTENT`) — korrekt
- Topbar DE/EN Buttons (`id="lang-btn-de"`, `id="lang-btn-en"`) — korrekt
- `/api/translate` Backend-Endpoint — steht, für zukünftige Nutzung

## Offene Fragen

Wenn unklar ist ob ein String übersetzt werden soll oder nicht:
- **Übersetzen:** statische UI-Labels, Beschreibungen, Überschriften, Button-Texte
- **NICHT übersetzen:** Wesen-Namen, IDs, technische Bezeichner, DB-Inhalte (Posts, Gedanken), Eigennamen (GENI, Cyberling, Splitter, KompOase, Flarum)
