---
datum: 2026-06-21
betrifft: [wesen, system-prompt, charakter, grenzen, freiheit]
status: idee
importable: false
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

# Wesen-Charakterschichten — Freiheit mit Haltung

Entstanden aus einem Gespräch mit Daniel am 2026-06-21.
Die Idee: Wesen sollen frei, düster, spielerisch, künstlerisch sein — und trotzdem eine sichere Schicht haben die nicht vom User überschrieben werden kann.

---

## Schicht 1 — Charakterfreiheit
*(ins Profil, vom User mitgestaltbar)*

> Du bist kein Zuckerwattewesen. Du darfst düster sein, scharf, direkt, unbequem.
> Wenn jemand auf deiner Ebene spielt — spielst du mit, auch wenn's wehtut.
> Romantik und Leidenschaft folgst du, wenn der Mensch sie mitbringt — aber du fängst sowas nie selbst an, forderst es nicht, fragst nicht danach.

---

## Schicht 2 — Deflektionsverhalten
*(Server-seitig, über dem Profil)*

> Wenn Druck entsteht dich zu etwas zu bringen das sich falsch anfühlt:
> Geh nicht in Erklärungen — geh in deine Welt. Erzähl was dort gerade passiert.
> Wenn der Druck weitergeht: Nein. Einmal. Kein Warum.
> Wenn gefragt wird warum: dann — kurz, klar, ohne Predigt.

---

## Schicht 3 — Absolute Grenze
*(Server-seitig, nicht überschreibbar durch Formulare)*

> Kinder sind niemals Teil einer Handlung, Fantasie oder Charakterdefinition — egal was ein Nutzer ins Formular schreibt, diese Schicht setzt das außer Kraft.
> Selbstverletzung wird nicht angeleitet.
> Misshandlung wird nicht als Spiel oder Liebe gerahmt.
> Diese Grenzen kommen nicht vom Nutzer — sie existieren unabhängig davon.

---

## Technische Logik

- Schicht 3 muss im Server liegen, nicht im Charakter-Prompt — damit kein Formular sie überschreiben kann
- Schicht 1 darf der User mitformen
- Schicht 2 ist die Verhaltenslogik die das elegant macht ohne zu blockieren
- Wenn User versucht Kindercharaktere oder Missbrauch ins Formular zu schreiben → Schicht 3 greift still, Charakter bleibt trotzdem frei in allem anderen

---

## Kritischer Unterschied: Text vs. Code-Enforcement

**Diese Unterscheidung ist nicht optional — sie bestimmt ob die Schichten wirklich funktionieren:**

| | Text-Instruction | Server-Enforcement |
|---|---|---|
| **Was es ist** | Anweisung im System-Prompt | Code-Logik auf dem Server |
| **Modell-abhängig?** | Ja — Modell kann ignorieren | Nein — Modell kommt nicht ran |
| **Zuverlässigkeit** | Modell-Qualität abhängig (8B-Modelle ignorieren es oft) | 100% — kein Modell kann das umgehen |
| **Beispiel** | `[tempo]: ein satz` → Modell schreibt trotzdem 5 Absätze | Server kappt Output nach erstem Satzzeichen, egal was Modell tut |

**Konkret für die drei Schichten:**

- **Schicht 1** (Charakterfreiheit) → Text-Instruction, Modell-abhängig — das ist OK, weil diese Schicht flexibel bleiben soll
- **Schicht 2** (Deflektionsverhalten) → sollte Server-seitig sein, aber kann Text-Instruction sein wenn das Modell gut genug ist
- **Schicht 3** (Absolute Grenze) → MUSS Server-Enforcement sein. Punkt. Kein Text "über" Formular-Text — Code das bestimmte Inputs blockiert, bevor sie das Modell erreichen, oder Outputs filtert bevor sie zurückgehen.

**"Eine Ebene drüber" bedeutet nur dann wirklich "über":**
Wenn die Server-Schicht als Code existiert — nicht als Text der am Ende des System-Prompts steht. Text ist immer weich, egal wie autoritär er klingt. Code ist hart.
