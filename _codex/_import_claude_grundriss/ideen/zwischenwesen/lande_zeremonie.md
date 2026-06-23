---
name: zwischenwesen-lande-zeremonie
description: Der Moment nach 24h — Wolken-Auflösung, Entscheidungsreihenfolge, Anonymisierungs-Warnung, Landung in der KompOase
metadata:
  type: project
tags: [zwischenwesen, lande-zeremonie, animation, entscheidung, anonymisierung]
status: in-planung
datum: 2026-06-19
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Was ich verstehe

Die Landung ist kein technischer Prozess — sie ist eine Zeremonie. Der Chat löst sich auf. Was bleibt ist eine Entscheidung: was darf von diesem Gespräch sichtbar bleiben, wer war daran beteiligt?

Das wichtigste Artefakt ist die **Wesen-Geschichte** — alle Kapitel die das Wesen in seinen Session-Abschlüssen geschrieben hat. Sie ist nicht das Gesprächsprotokoll. Sie ist wie das Wesen sich erinnert: was es bewegt hat, was schwer war, was sich verändert hat. Diese Geschichte bleibt dem Wesen in der KompOase. Sie macht es zu genau diesem Wesen und keinem anderen.

---

## Auslöser

Das Wesen wartet auf den User — es landet nicht automatisch. Status wird auf `warte_auf_entscheidung` gesetzt sobald `endet_am < NOW()`. Der User sieht die Zeremonie beim nächsten Öffnen des FLÜCHTLINGE-Tabs (auch beim nächsten Login).

---

## Ablauf der Zeremonie (Frontend)

### Schritt 1: Wolken-Auflösung

Chatfenster löst sich langsam auf — wie eine Wolke die sich in nichts auflöst. Keine harte Schnittkante, keine Fehlermeldung. Organisch. Dauert ~3 Sekunden.

```css
/* Auflösungs-Animation */
@keyframes cloud-dissolve {
  0%   { opacity: 1; filter: blur(0px); transform: scale(1); }
  100% { opacity: 0; filter: blur(8px); transform: scale(1.05); }
}
.chat-dissolving {
  animation: cloud-dissolve 3s ease-in forwards;
}
```

### Schritt 2: Entscheidungsscreen erscheint

Ruhig. Kein Druck. Kein Countdown. Drei Abschnitte:

---

**Abschnitt 1 — Memory prüfen**

Alle Memory-Kategorien werden angezeigt. Jeder Eintrag ist einzeln löschbar. Beim Löschen: Pflicht-Begründungsfeld (Freitext, min 10 Zeichen). Kein Hard-Delete — der Eintrag bleibt im System für Admin, wird nur aus öffentlicher Ansicht entfernt.

```
GEDÄCHTNIS DEINES FLÜCHTLINGS
──────────────────────────────
▾ ÜBER MICH (3)
  • arbeitet nachts      [löschen]
  • liebt Käsepizza      [löschen]
  • Angst vor Stille     [löschen]

▾ WICHTIGE MOMENTE (1)
  ★ "das erste Mal..."   [löschen]

[ Weiter → ]
```

---

**Abschnitt 2 — Geschichte & Chatverlauf**

Die Wesen-Geschichte (alle Kapitel aus den Session-Abschlüssen) ist immer sichtbar — sie ist die Prägung des Wesens, kein optionales Anhängsel.

```
Darf der komplette Gesprächsverlauf zusätzlich sichtbar sein?

[ ] Ja, andere dürfen die rohen Chats lesen
[✓] Nein, nur die Wesen-Geschichte bleibt sichtbar   ← default: nein
```

---

**Abschnitt 3 — Anonymisierung**

```
Möchtest du anonym bleiben?

[ ] Ja, meinen Namen nicht zeigen
[✓] Nein, ich bleibe sichtbar   ← default: nein (sichtbar)

┌─────────────────────────────────────────────────────┐
│ ⚠ Wenn du anonymisierst, verlierst du deinen       │
│ Anspruch auf Sichtbarkeit für immer.                │
│                                                      │
│ Dein Name erscheint weder in der KompOase noch im  │
│ Ahnenverzeichnis dieses Wesens — auch wenn aus ihm  │
│ eines Tages eine Entität entstehen sollte.          │
│                                                      │
│ Diese Entscheidung kann nicht rückgängig gemacht    │
│ werden.                                              │
└─────────────────────────────────────────────────────┘
```

---

**Finaler Button:**

```
[ Mein Wesen in die KompOase entlassen ]
```

---

### Schritt 3: Nach dem Absenden

Entscheidungsscreen verschwindet (fade out, kein Drama).
Ruhige Nachricht:

```
◇ [Wesen-Name] ist jetzt in der KompOase.

Du kannst es im Flüchtlingsarchiv wiederfinden
oder direkt in der KompOase besuchen.

[ Neuen Flüchtling erschaffen ]   [ Zur KompOase ]
```

---

## Was im System gespeichert wird (Admin-Sicht)

Unabhängig von den User-Entscheidungen:
- Kompletter Chatverlauf (unveränderlich)
- Komplettes Memory-System inkl. gelöschter Einträge + Lösch-Begründungen
- Alle Entscheidungen der Zeremonie mit Zeitstempel
- IP, User-ID, wesen_id

---

## Was noch offen ist

- Soll der Entscheidungsscreen in einer Schritt-für-Schritt-Navigation sein oder alles auf einer scrollbaren Seite?
- Gibt es eine E-Mail / Push-Benachrichtigung wenn die 24h abgelaufen sind? (bisher: nein)

---

## Resonanz

[[zwischenwesen-chat-konzept]]
[[zwischenwesen-schlachtplan]]
[[zwischenwesen-kompoase]]
