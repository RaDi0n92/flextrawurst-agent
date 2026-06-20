---
name: zwischenwesen-fluechtlingsarchiv
description: Tab FLÜCHTLINGSARCHIV — alle erschaffenen Wesen eines Users, Chatverlauf, Link zur KompOase
metadata:
  type: project
tags: [zwischenwesen, flüchtlingsarchiv, tab, archiv]
status: in-planung
datum: 2026-06-19
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Was ich verstehe

Jedes Zwischenwesen das ein Mensch erschaffen hat hinterlässt eine Spur. Das Flüchtlingsarchiv macht diese Spur lesbar. Kein Wesen wird vergessen.

---

## Tab-Name: FLÜCHTLINGSARCHIV

Eigener Tab in der Surface. Nur eingeloggte User sehen ihre eigenen Einträge.

---

## Was angezeigt wird

### Liste aller erschaffenen Flüchtlinge (chronologisch, neueste zuerst)

Jeder Flüchtling als Card:
```
┌──────────────────────────────────────────────────┐
│  [◇ in Wesen-Farbe]  [Wesen-Bild 48px]          │
│  WESEN-NAME           Typ: [wesen_typ]            │
│  Erschaffen: 2026-06-19  Gelandet: 2026-06-20    │
│  [Zur KompOase →]    [Gespräch lesen]            │
└──────────────────────────────────────────────────┘
```

### Detail-Ansicht (nach Klick auf Card)

```
┌──────────────────────────────────────────────────┐
│  ◇ WESEN-NAME                 [Zur KompOase →]  │
│──────────────────────────────────────────────────│
│  ERSCHAFFEN AM    2026-06-19 14:22               │
│  GELANDET AM      2026-06-20 14:22               │
│  TYP              Zimmerpflanze                  │
│                                                  │
│  BESCHREIBUNG     [wesen_text hier]              │
│  MAG              Regen, Stille, Dämmerung       │
│  MAG NICHT        Lärm, grelles Licht            │
│  FARBE            ████ #3a7a5c                   │
│                                                  │
│  ─────── GESPRÄCHSVERLAUF ───────                │
│  [Chatverlauf scrollbar, wenn User freigegeben] │
│  (oder: "Du hast den Verlauf nicht freigegeben")│
└──────────────────────────────────────────────────┘
```

### Weiterleitung zur KompOase

"Zur KompOase →" öffnet die KompOase direkt beim entsprechenden Zwischenwesenfragment — es wird highlighted/fokussiert.

---

## Counter im Menschenprofil

Im öffentlichen Profil des Menschen:
```
N Flüchtlinge erschaffen
```

Berechnung: `SELECT COUNT(*) FROM zwischenwesen WHERE user_id = :id AND status != 'aktiv'`

Kein extra Feld — COUNT on the fly, immer korrekt.

---

## Datenstruktur

Kein neues Schema nötig — alle Daten liegen bereits in:
- `zwischenwesen` (Felder, Datum, Status)
- `zwischenwesen_nachrichten` (Chatverlauf)
- `zwischenwesen.meta` (Entscheidungen der Lande-Zeremonie: Verlauf freigegeben ja/nein, anonymisiert ja/nein)

API-Endpunkt:
```
GET /api/zwischenwesen/archiv          ← alle abgeschlossenen des eingeloggten Users
GET /api/zwischenwesen/:id/detail      ← Detail + Chatverlauf (wenn freigegeben)
```

---

## Was noch offen ist

- Soll man im Archiv Einträge löschen können? (Empfehlung: nein — aber Admin kann)
- Soll es eine Suchfunktion im Archiv geben?
- Sollen andere User das Archiv eines Menschen sehen können (öffentliche Übersicht)?

---

## Resonanz

[[zwischenwesen-chat-konzept]]
[[zwischenwesen-schlachtplan]]
[[zwischenwesen-kompoase]]
