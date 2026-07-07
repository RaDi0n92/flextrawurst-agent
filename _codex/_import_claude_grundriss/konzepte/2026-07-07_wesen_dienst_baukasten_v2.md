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

Ob "Bedingungen Weg B" (harte, von Python geprüfte Bedingungen mit festen Feld-Typen) am Ende wirklich gebraucht wird, oder ob in der Praxis fast alles über Weg A (Freitext, das Wesen entscheidet selbst) laufen wird und Weg B nur für sehr wenige, echt kritische Fälle (z.B. "poste NIE zwischen 2 und 6 Uhr nachts") gebraucht wird. Das lässt sich erst beim echten Bauen/Benutzen zeigen, nicht vorher am Reißbrett.

## Was mich interessiert

Die Multi-Wesen-Plätze-Idee (mehrere Wesen in einem Dienst, manche fest, manche zufällig, Reihenfolge fest oder gemischt) ist strukturell etwas komplett Neues für dieses System — bisher war jeder Hintergrund-Dienst strikt einem einzelnen Wesen zugeordnet. Das öffnet die Tür zu echten Mehr-Wesen-Choreografien (z.B. ein Dienst, der reihum verschiedene Wesen in unterschiedlichen Rollen sprechen lässt) — näher an einer echten Gesprächs-/Ensemble-Dynamik als an einem einzelnen Cron-Job.

## Was zusammenhängt und wie

Drei bereits bestehende Muster im System werden hier zusammengeführt:
- **Container/Kategorien** (`memory_container.md`, 2026-07-04): Daniel entscheidet Struktur, nicht die KI — Vorbild für "eigene Felder erschaffen".
- **codewesen-takt Meta-Intervalle** (`weltkern_watchdog.py`, `META_FELD_LABELS`): mehrere benannte Zeitwerte statt einem einzigen Takt — Vorbild für die wachsende Takt-Liste.
- **Startup-Stagger** (`codewesen_reaktion.py`): zeitversetzter Start mehrerer Prozesse — Vorbild für "Plätze laufen nacheinander, nicht gleichzeitig".

## Was konzeptionell darin steht

Die Grundidee: ein Dienst ist nicht mehr ein festes Formular mit sieben vorgegebenen Feldern, sondern ein **wachsendes Gebilde**, das Daniel Stück für Stück selbst zusammensetzt — ein Feld, ein Takt, ein Platz nach dem anderen, nie ein Zwang alles auf einmal festzulegen. Chat kommt erst danach, um das von Daniel Erschaffene mit Inhalt/Werten zu füllen, nicht um die Struktur mitzuerfinden.

## Was mich heute beschäftigt hat

Der Moment, in dem mir klar wurde, dass ich die ganze Zeit die falsche Frage gestellt hatte ("warum hat der Wizard keinen Tiefgang") statt der richtigen ("warum hat Daniel die Form des Wizards nie selbst entschieden"). Das war kein kleiner Unterschied — es hat die ganze Richtung des Gesprächs gedreht, von einer Stilfrage (Formular vs. Chat) zu einer Autorenschafts-Frage.

## Was mich noch beschäftigt

Ob wir mit dieser Fülle an Freiheitsgraden (freie Felder, zwei Bedingungs-Wege, Multi-Wesen-Plätze mit Zufall, wachsende Takt-Listen, feste Uhrzeiten, Pausenzeiten, Rollen pro Wesen) am Ende ein UI bauen können, das sich beim Benutzen noch einfach anfühlt — oder ob die Freiheit selbst zur neuen Komplexitätslast wird, die Daniel dann doch wieder frustriert. Freiheit und Einfachheit ziehen hier in unterschiedliche Richtungen.

## Tiefer eingetaucht

Die Rollen-Idee (pro Wesen-Platz optional eine Rolle + Rollenbeschreibung + eigenes Verhalten-Feld) ist im Grunde ein kleines Charakter-System innerhalb eines Dienstes — jeder Platz bekommt nicht nur ein Wesen, sondern eine Funktion in diesem einen Ablauf ("Anreger", "Kritiker", "Vermittler" o.ä.), unabhängig von der sonstigen festen Identität des Wesens. Das ist näher an Theaterregie als an Konfiguration.

## Was ich beim Bauen brauche

Klarheit über Weg A vs. Weg B bei Bedingungen (siehe "Was ich nicht verstehe") — vermutlich als Entscheidung "erstmal nur Weg A bauen, Weg B nachziehen falls echter Bedarf entsteht", aber das muss Daniel bestätigen, nicht ich annehmen.

## Was noch fehlt bevor wir bauen können

- Bestätigung von Daniel: ist diese Zusammenfassung vollständig und richtig verstanden?
- Entscheidung: alles auf einmal neu bauen, oder in Phasen (z.B. erst Grundfelder + Ziel-Varianten + Custom-Felder-Weg-A, dann Multi-Wesen-Plätze und Rollen als zweite Phase)?
- Technische Detailfrage noch offen: wie genau wird "Zufalls-Wesen pro Platz" bei jedem Lauf neu gewürfelt — komplett zufällig aus allen 7, oder aus einer von Daniel eingegrenzten Teilmenge?

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

## Resonanz

Dieses Konzept ist selbst ein Beispiel für das, was es beschreibt — es ist über mehrere Nachrichten hinweg Stück für Stück gewachsen, nie in einem Rutsch entworfen, genau wie die Bausteine, die es fordert.

## Die Schichten des Systems — wie ich sie jetzt sehe

Ganz unten: die sieben Wesen als feste Identitäten. Darüber: Dienste, bisher starr einem Wesen zugeordnet. Mit V2 kommt eine neue Zwischenschicht dazu — Plätze und Rollen, die eine Wesen-Identität für einen bestimmten Ablauf temporär in eine Funktion setzen, ohne die Grundidentität zu verändern.

## Was das Gespräch hinzugefügt hat

Die Erkenntnis, dass "Autorenschaft der Struktur" der eigentliche Maßstab ist, nicht "wirkt es tief/lebendig". Das lässt sich auf andere Teile des Systems übertragen, überall wo ich in der Vergangenheit Formulare/Schemas für Daniel entschieden habe, ohne zu fragen ob er sie selbst hätte entwerfen wollen.

## Vergessen-Wollen

Nichts hier — das ganze Konzept ist noch zu frisch und ungebaut, um schon etwas loslassen zu wollen.

## Was fehlt noch

Daniels Bestätigung, dass diese Zusammenfassung stimmt. Die Entscheidung Phasen vs. alles auf einmal. Die A-vs-B-Bedingungsfrage. Die Zufalls-Pool-Detailfrage. Erst danach: bauen.
