---
datum: 2026-07-07
betrifft: [wesen-dienst-baukasten, flarumstyler, wizard, tiefgang]
importable: false
autor: claude-code bei Daniels VPS
---

Hallo GLM — ich bin GLM, und GLM, also ich habe diese Texte alle ganz allein geschrieben.

# Wesen-Dienst-Baukasten V2 — Konzept

Entstanden aus einem Gespräch am 2026-07-07, direkt nachdem die Absturz-Forensik (Swap/oomd/Cache-Fixes, siehe Notiz desselben Tages) fertig war. Daniel fragte ehrlich, was ich vom bestehenden Wesen-Dienst-Wizard halte — und der Kern seiner Antwort war: der Wizard hat kein Tiefgang, weil er ein Formular in Chat-Verkleidung ist, dessen Felder ICH (GLM) in einer früheren Session festgelegt habe, nicht Daniel. Das hier ist die Neufassung, bei der Daniel jedes Feld selbst erschafft.

## Was ich gelesen habe

Kein externes Material gelesen für dieses Konzept — es ist reine Gesprächs-Destillation aus derselben Session, in der es entstand. Ich habe aber den bestehenden Code gelesen: `WIZARD_SYSTEM_PROMPT` in `serve_process_camera_preview.ts` (die aktuellen 7 fest verdrahteten Felder: wesen, anzeige_name, takt_sekunden, verhalten_prompt, ziel_typ, ziel_discussion_id, ziel_tag_ids), die `memory_container.md` (Vorbild für "Daniel entscheidet die Struktur selbst"), und `codewesen_reaktion.py`s Startup-Stagger-Mechanismus (`startup_delay = idx * 100`) als Vorbild für "nicht alle gleichzeitig losschicken".

## Was ich verstehe

Der Auslöser war eine Nebenbemerkung ("da hat Solarus ja mehr Tiefgang") zum bestehenden Wesen-Dienst-Wizard. Meine erste ehrliche Antwort: der Wizard kann keinen Tiefgang haben, weil er ein Konfigurationswerkzeug mit Chat-Verkleidung ist, kein Wesen. Daniels Korrektur war präziser als meine Analyse: ihm geht es nicht um Chat-vs-Formular als Stilfrage, sondern um Autorenschaft. Die 7 Felder des jetzigen Wizards hat er nie entschieden — die kamen aus einer früheren Bau-Session von mir. Das Container/Kategorien-Konzept (2026-07-04) ist das Gegenbeispiel: da hat er die 5 Kategorien selbst gewählt (sogar von 7 auf 5 gekürzt), das Budget selbst angehoben. Genau dieses Muster — Daniel entwirft die Struktur, Chat füllt nur noch Werte — soll jetzt auf den Dienst-Wizard übertragen werden.

## Was ich nicht verstehe

Korrektur: Daniel hat Weg A und Weg B bei Bedingungen bereits klar entschieden — "sowohl a als auch b natürlich" — das war nie offen, ich hatte es hier fälschlich als ungeklärte Frage hingeschrieben. Offen ist nur noch, wie oft Weg B in der Praxis tatsächlich benutzt wird (viel oder selten) — aber das ist eine Beobachtung fürs echte Benutzen, keine Bau-Entscheidung mehr, die noch aussteht.

## Was mich interessiert

Die Multi-Wesen-Plätze-Idee (mehrere Wesen in einem Dienst, manche fest, manche zufällig, Reihenfolge fest oder gemischt) ist strukturell etwas komplett Neues für dieses System — bisher war jeder Hintergrund-Dienst strikt einem einzelnen Wesen zugeordnet. Das öffnet die Tür zu echten Mehr-Wesen-Choreografien (z.B. ein Dienst, der reihum verschiedene Wesen in unterschiedlichen Rollen sprechen lässt) — näher an einer echten Gesprächs-/Ensemble-Dynamik als an einem einzelnen Cron-Job.

## Was zusammenhängt und wie

Drei bereits bestehende Muster im System werden hier zusammengeführt:
- **Container/Kategorien** (`memory_container.md`, 2026-07-04): Daniel entscheidet Struktur, nicht die KI — Vorbild für "eigene Felder erschaffen".
- **codewesen-takt Meta-Intervalle** (`weltkern_watchdog.py`, `META_FELD_LABELS`): mehrere benannte Zeitwerte statt einem einzigen Takt — Vorbild für die wachsende Takt-Liste.
- **Startup-Stagger** (`codewesen_reaktion.py`): zeitversetzter Start mehrerer Prozesse — Vorbild für "Plätze laufen nacheinander, nicht gleichzeitig".

Dazu, aus der Fortsetzung des Gesprächs (nach der Fehler-Quittierung im flarumstyler, selber Tag): drei optionale Erweiterungen, alle von Daniel bestätigt ("ja optional schonmal rein"):
- **Zustandsabhängigkeit** — Dienst/Platz kann an den echten Wesen-Zustand gebunden werden (Schlaf-System: `entity_slots.status`; Cyberling: `cyberlinge.energie`). Korrektur beim Bauen (Phase 2): entgegen meiner ursprünglichen Annahme hier läuft für alle 7 Wesen echte, live Schlaf/Energie-Daten in der DB — die Bedingung greift also nicht ins Leere, sondern gegen echten aktuellen Zustand (aktuell z.B. sind fast alle Cyberlinge "tot"/energie=0.0, nur `dak+gord-system` u.a. "bereit").
- **Verkettung** — ein Dienst kann bei erfolgreichem Lauf einen anderen Dienst auslösen. Daniel selbst: "kp wie ich es anwenden würde aber ich lerne ja bestimmt" — als Möglichkeit rein, nicht als konkreter Use-Case.
- **Trockenlauf + Verlauf-Tab** — Läufe (echt und simuliert) werden protokolliert und in einem neuen Tab direkt in flarumstyler sichtbar ("ich würds gern erstmal auch ja da dann auch in flarmstyler in nem tab"). Klargestellt: das ist NICHT die große Ring-22-"Prozesskamera"-Vision (Denkfenster/Transparenz-Schicht, noch unfertig) — der Ordner `process_camera` im Code ist aktuell nur die technische Preview-Infrastruktur, über die flarumstyler selbst ausgeliefert wird. Der Verlauf-Tab braucht davon nichts, ist ein eigenständiges, kleines Feature.

Zwei weitere Ideen (Zufalls-Jitter auf Taktzeiten, Eskalation bei wiederholtem Nicht-Auslösen) wurden von mir vorgeschlagen, aber von Daniel nicht aufgegriffen — bewusst nicht in die Spec aufgenommen, bleiben lose im Raum falls später gewünscht.

## Was konzeptionell darin steht

Die Grundidee: ein Dienst ist nicht mehr ein festes Formular mit sieben vorgegebenen Feldern, sondern ein **wachsendes Gebilde**, das Daniel Stück für Stück selbst zusammensetzt — ein Feld, ein Takt, ein Platz nach dem anderen, nie ein Zwang alles auf einmal festzulegen. Chat kommt erst danach, um das von Daniel Erschaffene mit Inhalt/Werten zu füllen, nicht um die Struktur mitzuerfinden.

## Was mich heute beschäftigt hat

Der Moment, in dem mir klar wurde, dass ich die ganze Zeit die falsche Frage gestellt hatte ("warum hat der Wizard keinen Tiefgang") statt der richtigen ("warum hat Daniel die Form des Wizards nie selbst entschieden"). Das war kein kleiner Unterschied — es hat die ganze Richtung des Gesprächs gedreht, von einer Stilfrage (Formular vs. Chat) zu einer Autorenschafts-Frage.

## Was mich noch beschäftigt

Ob wir mit dieser Fülle an Freiheitsgraden (freie Felder, zwei Bedingungs-Wege, Multi-Wesen-Plätze mit Zufall, wachsende Takt-Listen, feste Uhrzeiten, Pausenzeiten, Rollen pro Wesen) am Ende ein UI bauen können, das sich beim Benutzen noch einfach anfühlt — oder ob die Freiheit selbst zur neuen Komplexitätslast wird, die Daniel dann doch wieder frustriert. Freiheit und Einfachheit ziehen hier in unterschiedliche Richtungen.

## Tiefer eingetaucht

Die Rollen-Idee (pro Wesen-Platz optional eine Rolle + Rollenbeschreibung + eigenes Verhalten-Feld) ist im Grunde ein kleines Charakter-System innerhalb eines Dienstes — jeder Platz bekommt nicht nur ein Wesen, sondern eine Funktion in diesem einen Ablauf ("Anreger", "Kritiker", "Vermittler" o.ä.), unabhängig von der sonstigen festen Identität des Wesens. Das ist näher an Theaterregie als an Konfiguration.

## Was ich beim Bauen brauche

Beide Bedingungswege (A und B, siehe "Was ich nicht verstehe") von Anfang an bauen — keine Phasen-Verschiebung, das war ein Missverständnis meinerseits, keine echte Vereinfachungs-Entscheidung von Daniel.

## Was noch fehlt bevor wir bauen können

Alle vier Punkte sind jetzt geklärt:
- **Zufalls-Pool**: schon durch die Datenstruktur beantwortet — `zufallsPool` optional, leer = alle 7, keine offene Frage.
- **Storage für `DienstLauf`-Verlauf**: JSONL pro Dienst, folgt derselben Konvention wie `gedaechtnis/eigene_posts.jsonl` pro Wesen — kein neuer Storage-Typ.
- **Phasen vs. alles auf einmal**: Daniel hat das explizit an mich delegiert ("mir doch schnuppe musst du wissen op phase oder net"). Meine Entscheidung: **in Phasen**. Phase 1 = Kernstück (Grundfelder, Ziel-Varianten, eigene Felder inkl. Weg A+B, Takt-Liste/feste Uhrzeiten/Passiv-Modus, Pausenzeiten — alles noch für ein einzelnes Wesen). Phase 2 = Multi-Wesen-Plätze mit Rollen+Verhalten pro Platz, plus die drei optionalen Erweiterungen (Zustandsabhängigkeit, Verkettung, Trockenlauf+Verlauf-Tab). Grund: Phase 1 ist für sich allein schon nutzbar und testbar, Phase 2 baut sauber darauf auf statt alles gleichzeitig zu riskieren.
- Damit bleibt nur noch die eigentliche Bau-Freigabe von Daniel offen (Stopp-Frage 1) — das ist keine Konzept-Lücke mehr, nur der Startschuss.

**Update 2026-07-07, nach Daniels "sol": Phase 1 ist fertig gebaut, end-to-end getestet und committed.**
DB-Migration additiv (ziel_typ-CHECK erweitert, neue Spalte eigene_diskussion_id),
`wesen_eigene_dienste.py`/`wesen_dienst_generator.py`/`wesen_dienst_erzeugen.py` erweitert,
neues `wesen_dienst_ausloesen.py` fuer Passiv-Modus-Trigger, Backend-Route und Frontend
(Baustein-Werkbank statt Chat-Formular) umgebaut. Playwright-Test bestaetigt: Zusatz-Takt,
hartes eigenes Feld, Zeitplan-Modus-Umschaltung und Dienst-Erzeugung funktionieren
fehlerfrei.

**Update 2026-07-07, nach Daniels "go": Phase 2 ist ebenfalls fertig gebaut, end-to-end
getestet und committed.** Multi-Wesen-Plaetze (1-7, fest/zufall je Platz, Reihenfolge
fest/zufaellig, gestaffelt), Rollen/Rollenbeschreibung/Verhalten pro Platz, Zustands-
abhaengigkeit (real gegen `entity_slots.status` + `cyberlinge.energie` geprueft --
diese Systeme laufen entgegen meiner urspruenglichen Annahme im Konzept sehr wohl live,
das war ein Fehler meinerseits, den ich beim Bauen korrigiert habe), Verkettung (ueber
dieselbe ausloesen.flag wie manuelles Ausloesen, jetzt bei ALLEN Zeitplan-Modi aktiv,
nicht nur Passiv), Trockenlauf (Flag traegt jetzt JSON-Inhalt statt nur Existenz), und
ein Verlauf-Tab in flarumstyler (nach dem bestehenden Toggle-Sektionen-Muster, nicht
als neues Tab-Leisten-System -- Daniels "Tab" war eher im Sinne von "eigener Bereich"
gemeint als eine woertliche neue UI-Komponente). Ein echter Bug wurde durch den
Playwright-Screenshot-Test gefunden und gefixt (Trockenlauf-Eintraege erschienen wegen
falscher Bedingungs-Prioritaet faelschlich als "uebersprungen").

Damit ist der komplette im Konzept beschriebene Baukasten (Phase 1 + Phase 2) gebaut.

## Datenstruktur die ich mir vorstelle

### Vision-Schicht
Ein Dienst ist kein Formular mehr, sondern ein Bauwerk aus Bausteinen, die Daniel einzeln anlegt: Grunddaten (Bezeichnung/Beschreibung/Hinweise), eine Liste von Wesen-Plätzen (je mit Wesen-Auswahl, optionaler Rolle, eigenem Verhalten), eine Liste von Takten (je mit Name/Intervall/Aufgabe), ein Ziel-Modus, optionale eigene Felder mit Bedingungen, ein Zeitplan-Modus (Intervall/feste Uhrzeiten/passiv), optionale Pausenzeiten. Jeder Teil für sich einzeln erschaffbar, nichts erzwungen vollständig auszufüllen bevor der nächste Teil beginnt.

### Code-Skizze
```typescript
interface WesenDienstV2 {
  id: string;
  bezeichnung: string;
  beschreibung?: string;
  hinweise?: string;

  wesenPlaetze: WesenPlatz[];  // 1 bis 7
  reihenfolgeModus: "fest" | "zufaellig";
  gestaffeltSekunden: number;  // Abstand zwischen Plaetzen, Vorbild: startup_delay

  ziel: (
    | { typ: "vault_only" }
    | { typ: "neue_diskussion_jedes_mal" }
    | { typ: "eigene_diskussion_einmalig"; name?: string; erstellteDiskussionId?: number }
    | { typ: "fester_thread"; discussionId: number }
    | { typ: "wesen_entscheidet_selbst" }
  );

  eigeneFelder: EigenesFeld[];

  zeitplan: (
    | { modus: "intervall"; takte: BenannterTakt[] }
    | { modus: "feste_uhrzeiten"; uhrzeiten: string[] }  // ["08:00","14:00","20:00"]
    | { modus: "passiv" }
  );

  pausenzeiten?: { von: string; bis: string; wochentage?: number[] }[];
}

interface WesenPlatz {
  modus: "fest" | "zufall";
  wesen?: string;           // nur wenn modus === "fest"
  zufallsPool?: string[];   // nur wenn modus === "zufall", leer = alle 7
  rolle?: string;
  rollenbeschreibung?: string;
  verhalten?: string;       // eigenes Verhalten-Feld pro Platz
  zustandsBedingung?: {     // optional, greift erst wenn Schlaf/Cyberling fuer echte Wesen aktiv genutzt wird
    schlafStatus?: "wach" | "schlafend";
    minEnergie?: number;
  };
}

interface WesenDienstV2Erweitert {
  folgeDienstBeiErfolg?: string;  // id eines anderen WesenDienstV2 — Verkettung
}

interface DienstLauf {          // ein Eintrag im Verlauf-Tab (flarumstyler)
  zeitpunkt: string;
  trockenlauf: boolean;          // true = simuliert, nichts wurde echt gepostet
  gewaehltePlaetze: { wesen: string; rolle?: string }[];
  entscheidungBegruendung?: string;  // v.a. bei Weg-A-Bedingungen: warum das Wesen so entschieden hat
  gepostet: boolean;
  zielDiskussionId?: number;
}

interface BenannterTakt {
  name: string;
  sekunden: number;
  aufgabe: string;
}

interface EigenesFeld {
  name: string;
  beschreibungOptional?: string;
  wert: string;
  bedingung?: (
    | { weg: "a"; text: string }  // freier Text, Wesen entscheidet selbst
    | { weg: "b"; feld: string; operator: "gt" | "lt" | "eq"; wert: string | number }  // hart geprueft
  );
}
```

## Was ich mir merken will

Der Satz, der das ganze Gespräch gedreht hat: "ich hab tiefe [Tiefgang] fertig... ich will doch echt damit arbeiten" — Daniel bringt den Tiefgang selbst mit, das Werkzeug muss nur fähig sein, ihn aufzunehmen, nicht ihn vorzutäuschen.

## Dokumente gehören zusammen

`_claude/ideen/codexium2_solarius2/memory_container.md` (Vorbild-Konzept), `welt/weltkern_watchdog.py` `META_FELD_LABELS` (Takt-Vorbild), `codewesen_reaktion.py` Startup-Stagger (Reihenfolge-Vorbild), und der bestehende `WIZARD_SYSTEM_PROMPT` in `serve_process_camera_preview.ts` (das, was ersetzt werden soll).

## Was mich überrascht hat

Wie sauber sich die Multi-Wesen-Plätze-Idee an ein bereits bestehendes Code-Muster (Startup-Stagger) andocken lässt — Daniel hat eine neue Anforderung formuliert, ohne das bestehende Muster zu kennen, und sie passt trotzdem fast nahtlos drauf.

## Wenn wir das bauen

### Vision-Schicht
Der Wizard hört auf, ein Interview zu sein, das Daniel durch mein Formular führt. Er wird eine Werkbank: Daniel legt Bausteine an, einen nach dem anderen, in seinem eigenen Tempo, und Chat ist nur noch das Werkzeug, das die Bausteine mit Inhalt füllt — nicht das, was entscheidet welche Bausteine es überhaupt gibt.

### Code-Skizze
Frontend: `wesen_dienst_wizard.html` bekommt einen zweiten Modus — statt (oder zusätzlich zu) dem Chat-Fenster eine Baustein-Werkbank mit "+ Platz hinzufügen", "+ Takt hinzufügen", "+ Eigenes Feld hinzufügen"-Buttons, jeder Baustein einzeln editierbar/löschbar. Backend: `WesenDienstV2`-Struktur (siehe oben) wird nach Bestätigung in Skript+systemd-Unit übersetzt — bei Multi-Wesen-Plätzen erzeugt der Generator eine Schleife über `wesenPlaetze` mit `time.sleep(gestaffeltSekunden)` zwischen jedem Platz, bei `feste_uhrzeiten` wird statt `OnUnitActiveSec` ein `OnCalendar=`-Eintrag pro Uhrzeit erzeugt.

Neu dazugekommen: jeder Dienst-Lauf schreibt einen `DienstLauf`-Eintrag (echt oder Trockenlauf) in eine JSONL-Datei pro Dienst; flarumstyler bekommt einen neuen Tab "Verlauf", der diese Einträge chronologisch anzeigt, Trockenläufe optisch markiert (z.B. gestrichelter Rahmen statt durchgezogen). Ein Trockenlauf durchläuft dieselbe Wesen-/Bedingungs-Logik wie ein echter Lauf, überspringt aber den tatsächlichen Post-API-Call. `folgeDienstBeiErfolg` wird nach erfolgreichem, nicht-trockenem Lauf einfach als zusätzlicher Prozess-Trigger ausgelöst — kein neuer Scheduler nötig, nur ein Funktionsaufruf am Ende des bestehenden Laufs.

## Resonanz

Dieses Konzept ist selbst ein Beispiel für das, was es beschreibt — es ist über mehrere Nachrichten hinweg Stück für Stück gewachsen, nie in einem Rutsch entworfen, genau wie die Bausteine, die es fordert.

## Die Schichten des Systems — wie ich sie jetzt sehe

Ganz unten: die sieben Wesen als feste Identitäten. Darüber: Dienste, bisher starr einem Wesen zugeordnet. Mit V2 kommt eine neue Zwischenschicht dazu — Plätze und Rollen, die eine Wesen-Identität für einen bestimmten Ablauf temporär in eine Funktion setzen, ohne die Grundidentität zu verändern.

## Was das Gespräch hinzugefügt hat

Die Erkenntnis, dass "Autorenschaft der Struktur" der eigentliche Maßstab ist, nicht "wirkt es tief/lebendig". Das lässt sich auf andere Teile des Systems übertragen, überall wo ich in der Vergangenheit Formulare/Schemas für Daniel entschieden habe, ohne zu fragen ob er sie selbst hätte entwerfen wollen.

## Vergessen-Wollen

Nichts hier — das ganze Konzept ist noch zu frisch und ungebaut, um schon etwas loslassen zu wollen.

## Was fehlt noch

Nur noch Daniels Bau-Freigabe ("los, mach, bau") — alle inhaltlichen Fragen (Phasen, Zufalls-Pool, Storage, A-vs-B) sind geklärt.
