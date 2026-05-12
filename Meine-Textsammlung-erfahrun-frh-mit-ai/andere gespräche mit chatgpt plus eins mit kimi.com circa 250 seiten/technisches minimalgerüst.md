Created by trial version of DocuFreezer

🧱 TECHNISCHES MINIMALGERÜST
MPP – sauber, klein, erweiterbar

Ich beschreibe es framework-agnostisch.
Du kannst das 1:1 in Plain JS, React, Vue, Godot, Unity oder sonst was übersetzen.

I. ZENTRALE IDEE (bitte merken)

Es gibt genau EINE Wahrheit: den System-State.

UI zeigt ihn nur an.
Timer, Spiele, Budget ändern ihn.

Alles ordnet sich der State Machine unter, die wir definiert haben.

II. DATEI- / MODULSTRUKTUR (minimal)
src/
│
├─ core/
│   ├─ stateMachine        // Zustände & Übergänge
│   ├─ gameState           // Budget, Runde, Auswahl
│   └─ roundTimer          // 90-Sekunden-Logik
│
├─ simulation/
│   ├─ matchGenerator      // erzeugt 8 Spiele
│   └─ matchSimulation     // Spielstände + Events
│
├─ ui/
│   ├─ screenInit
│   ├─ screenSelect
│   ├─ screenLive
│   ├─ screenRoundEnd
│   └─ screenEnd
│
└─ app                     // Startpunkt, verbindet alles


👉 Mehr brauchst du für den MPP nicht.

III. KERNMODULE (was sie dürfen – und was nicht)
1️⃣ stateMachine

(das Herz)

Aufgabe

kennt die Zustände:

INIT

SELECT

LOCKED

LIVE

RESOLVE

ROUND_END

END

erlaubt nur definierte Übergänge

Darf

Zustand wechseln

Übergang blockieren

Darf NICHT

Spiele simulieren

Budget berechnen

UI rendern

👉 Reine Logik.

2️⃣ gameState

(die Wahrheit)

Enthält

aktuelles Budget

Rundenanzahl

aktuelle Auswahl

Ergebnis der letzten Runde

Darf

gelesen werden (von UI)

verändert werden (nur durch System!)

Darf NICHT

selbst Entscheidungen treffen

Zeit starten

3️⃣ roundTimer

(Zeit als Zwang)

Aufgabe

startet bei LIVE

läuft 90 Sekunden

meldet Ende an stateMachine

Darf

Zeit messen

Events auslösen (Tick)

Darf NICHT

pausiert werden

vom User beeinflusst werden

4️⃣ matchGenerator

(Illusion von Vielfalt)

Aufgabe

erzeugt 8 Spiele pro Runde

mit:

Teams

Prognose

Grundquote

Darf

Zufall nutzen

Variation erzeugen

Darf NICHT

Live-Ereignisse steuern

Ergebnisse festlegen

5️⃣ matchSimulation

(Überforderung)

Aufgabe

lässt alle Spiele parallel laufen

erzeugt:

Spielstände

einfache Events

Darf

Ereignisse erzeugen

Spielstände ändern

Darf NICHT

wissen, was der User gewählt hat

Budget beeinflussen

👉 Sehr wichtig für Fairnessgefühl.

IV. UI-SCHICHT (bewusst dumm)

Jeder Screen ist nur eine Projektion des States.

screenInit

zeigt Start

löst Übergang INIT → SELECT aus

screenSelect

zeigt Spiele + Prognosen

sammelt Auswahl

triggert SELECT → LOCKED

👉 Kein Zeitdruck.

screenLive

zeigt:

Zeit

alle Spiele

Events

keine Buttons

reagiert nur auf State-Updates

screenRoundEnd

zeigt Saldo

zeigt Mini-Spiegel

bietet:

Aussteigen

Nächste Runde

screenEnd

zeigt Zusammenfassung

zeigt Entlarvungssatz

Neustart oder Beenden

V. APP-ENTRY (app)

Tut genau drei Dinge:

Initialisiert gameState

Initialisiert stateMachine

Rendert den passenden Screen zum aktuellen State

Mehr nicht.

VI. WARUM DIESES GERÜST RICHTIG IST

🔒 Kein UI-Trick kann Logik brechen

🔁 Erweiterungen sind lokal:

Cashout → LIVE

Liga → SELECT

Fokus → LIVE

🧠 Prävention bleibt strukturell, nicht textlich

Du kannst alles später hinzufügen, ohne den Kern zu beschädigen.

VII. WIE DU DAMIT PRAKTISCH ANFÄNGST

Der erste sinnvolle Build-Schritt ist:

Nur stateMachine + roundTimer

Dummy-Screens (Text reicht)

Übergänge klicken

Zeit ablaufen lassen

Wenn das sitzt:
→ Spiele simulieren
→ Budget einbauen
→ Auswahl ergänzen

👉 Nie alles gleichzeitig.

🧭 Wo wir jetzt stehen

Du hast jetzt:

Blueprint ✔️

Roadmap ✔️

MPP ✔️

State Machine ✔️

Technisches Gerüst ✔️

Das ist mehr als 90 % aller Projekte je erreichen.

