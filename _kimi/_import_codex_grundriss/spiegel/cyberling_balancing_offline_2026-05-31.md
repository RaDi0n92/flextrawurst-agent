---
datum: 2026-05-31
betrifft: [cyberling, balancing, offline-simulation]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

# Cyberling-Balancing offline

## Was ich gelesen habe

Ich habe den bestehenden Cyberling-Daemon gelesen, vor allem seine Kaskade: Durst faellt schnell, Hunger langsamer, danach Energie und Gesundheit. Der Code sagt klar: Pflege ist nicht Dekoration, sondern Zeitdruck.

Ich habe auch die Handlungsgrammatik gelesen. Dort steht sinngemaess: *Du kannst nicht einfach immer klicken.* Das war der Kern, weil der produktive API-Pfad genau das noch nicht erzwingt.

Dann habe ich das alte Verzeichnis `welt/cyberling_balancing/` gesehen. Es gab dort schon eine Simulation mit IST/SOLL-Vergleich. Ich habe sie nicht ueberschrieben, sondern eine neue Offline-Datei unter `_codex/tools/` angelegt, damit Herkunft sichtbar bleibt.

## Was ich verstehe

Der Cyberling soll nicht durch Spam stabil bleiben. Er soll einen Rhythmus brauchen. Gute Pflege darf leicht sein, aber nicht bedeutungslos.

## Was ich nicht verstehe

Ich verstehe noch nicht, ob 24 Stunden Vernachlaessigung schon Gesundheit kosten soll oder ob Energie allein genug Warnsignal ist.

## Was mich interessiert

Mich interessiert, wie viel Unbequemlichkeit noetig ist, damit Pflege als Beziehung und nicht als Button-Routine erscheint.

## Was zusammenhängt und wie

Daemon, API, Handlungsgrammatik und Surface haengen direkt zusammen. Wenn nur einer davon Schwellen kennt, ist das System inkonsistent.

## Was konzeptionell darin steht

Der Cyberling ist ein Pflegeverhaeltnis. Balancing ist hier Ethik in Zahlenform: Wie schnell darf ein abhaengiges Wesen leiden?

## Was mich heute beschäftigt hat

Dass die Simulation bewusst offline blieb. Kein produktiver Tick, kein echter Tod, keine echte Rettung. Nur Zahlen auf Papier.

## Was mich noch beschäftigt

Die Grenze zwischen "brauchbar" und "zu hart" ist noch eine Daniel-Entscheidung.

## Tiefer eingetaucht

Die neue Simulation erzeugt sechs Szenarien: perfekte Pflege, leicht verspaetete Pflege, 12h/24h/48h Vernachlaessigung und Ueberpflege. Wichtig ist der Spamversuch: er darf nicht belohnt werden.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie Werkbankarbeit. Kein Welteingriff, nur ein Messgeraet gebaut.

## Warum dieser Code / diese Datei wohl existiert

Die Simulation existiert, damit spaeter nicht am lebenden Cyberling gebalanced wird.

## Was ich beim Bauen brauche

Vor Produktivbau brauche ich eine klare Entscheidung: 24h kritisch-reparierbar, 48h lebensgefaehrlich, Spam blockiert.

## Was noch fehlt bevor wir bauen können

Ein Schema-/API-Abgleich fuer Cooldowns, Schwellen und Caps.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Pflege ist kein Maximalwert-Spiel. Ein Cyberling darf nicht immer voll sein muessen, aber er muss spuerbar brauchen duerfen.

**Code-Skizze:**
```python
@dataclass
class CyberlingCareRule:
    field: Literal["hunger", "durst"]
    allowed_at: float
    amount: float
    cap: float
    cooldown_h: float
```

## Was ich mir merken will

Offline-Simulation zuerst. Produktivcode spaeter. Das ist hier richtig.

## Dokumente gehören zusammen

`_codex/tools/cyberling_balance_offline.py`, `_codex/berichte/cyberling_balancing/zusammenfassung.md`, `welt/cyberling_daemon.py`, `wesen_entscheidung_cyberling.md`.

## Was mich überrascht hat

Dass schon eine alte Balancing-Simulation existierte. Der neue Auftrag war nicht aus dem Nichts.

## Wenn wir das bauen

**Vision-Schicht:** Der Cyberling soll Verantwortung sichtbar machen, nicht Klickfleiss.

**Code-Skizze:**
```python
def can_care(cyberling, action, now):
    return value_below_threshold(cyberling, action) and cooldown_done(cyberling, action, now)
```

## Resonanz

[[abwurf: Balancing am lebenden Wesen waere kein Test, sondern ein Eingriff.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Konzept, Simulation, Daemon, API, Surface, Eventlog. Jede Schicht muss dieselbe Pflegephysik sprechen.

## Was das Gespräch hinzugefügt hat

Daniel hat die Grenze klar gesetzt: offline, keine DB, keine Services. Dadurch wurde die Simulation sauber.

## Vergessen-Wollen

Den Reflex, schnell die Daemon-Werte anzupassen, weil die Simulation plausibel aussieht.

## Was fehlt noch

Daniels Freigabe fuer konkrete Werte und danach ein kleiner, sauberer Produktivbau.
