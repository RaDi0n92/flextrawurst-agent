Created by trial version of DocuFreezer

🧠 MINIMAL-PLAYABLE-PROTOTYPE
STATE MACHINE (Zustände & Übergänge)

Denk das Ganze wie ein Automat, nicht wie Screens.
Screens sind nur Darstellung eines Zustands.

🔵 STATE 0 — INIT
Bedeutung

Das System existiert

Noch keine Bindung

Noch keine Entscheidung

Systemvariablen

budget = 100

round = 0

history = []

Übergang

User klickt „Spiel starten“
→ SELECT

🟡 STATE 1 — SELECT (Auswahlphase)
Bedeutung

Maximales Kontrollgefühl

Keine Zeit

Keine Konsequenz noch

System tut

Generiert 8 Spiele

Zeigt Prognosen & Quoten

Erlaubt:

Einsatz festlegen

Einzel oder Kombi wählen

Auswahl ändern (beliebig oft)

System merkt

Welche Spiele gewählt wurden

Einsatzhöhe

Wettform (Einzel/Kombi)

Übergang

User bestätigt Auswahl
→ LOCKED

🟠 STATE 2 — LOCKED (Bindung)
Bedeutung

Entscheidung ist gefallen

Noch passiert nichts

Aber: kein Zurück

System tut

friert Auswahl ein

friert Einsatz ein

setzt round += 1

👉 Dieser Zustand darf sehr kurz sein
(auch nur 1 Frame), aber er ist konzeptionell wichtig.

Übergang

automatisch
→ LIVE

🔴 STATE 3 — LIVE (90 Sekunden)
Bedeutung

Zeit läuft

User kann nichts ändern

Aufmerksamkeit wird gefordert

System tut

Startet 90s-Timer

Simuliert alle 8 Spiele parallel

Erzeugt Events:

Chance

Eckball

Gelbe Karte

Tor

Regeln

Kein Exit

Kein Pause

Keine Eingriffe

Übergang

Timer endet
→ RESOLVE

🟣 STATE 4 — RESOLVE (Auswertung)
Bedeutung

Konsequenzen materialisieren sich

Kein Drama

Nur Resultat

System tut

Berechnet:

Gewinn / Verlust

Aktualisiert:

budget

Loggt:

Ergebnis der Runde

👉 Kein Feedback im Sinne von „gut/schlecht“

Übergang

automatisch
→ ROUND_END

🟢 STATE 5 — ROUND_END (Reflexionsfenster)
Bedeutung

Einzige echte Entscheidungsfreiheit

Klarer Schnitt

System zeigt

„Runde abgeschlossen“

Aktuellen Saldo

einen Mini-Spiegel-Satz

User kann

Aussteigen

Nächste Runde starten

Übergänge

Aussteigen → END

Weiterspielen → SELECT

⚫ STATE 6 — END
Bedeutung

Spiel ist vorbei

Kein Handlungsdruck

Kein Weiterdrehen

Eintritt über zwei Wege

User steigt freiwillig aus

budget <= 0

System zeigt

Runden gespielt

Höchster Saldo

1 zentraler Satz (Entlarvung)

User kann

Neues Spiel starten → INIT

Beenden → Session endet

🔁 VOLLSTÄNDIGER FLOW (kompakt)
INIT
 ↓
SELECT
 ↓
LOCKED
 ↓
LIVE (90s)
 ↓
RESOLVE
 ↓
ROUND_END
 ↙        ↘
END      SELECT


Das ist alles.
Kein versteckter Zustand.
Kein Hintertürchen.

🧠 WARUM DIESE STATE MACHINE STARK IST

Keine Magie

Keine Ausnahmen

Keine Sonderfälle

Alles, was später kommt (Liga, Cashout, Fokus, Ballverlauf),
ist nur eine Erweiterung von LIVE oder SELECT.

Der Kern bleibt stabil.

🧭 WANN DU JETZT WIRKLICH BAUEN KANNST

Du kannst jetzt mit reinem State-Denken:

einen einfachen Prototyp bauen

egal ob:

Web

Game Engine

Paper Prototype

Wenn du irgendwo hängenbleibst, frag dich immer:

„In welchem State bin ich gerade –
und was darf hier nicht passieren?“

