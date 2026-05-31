---
datum: 2026-05-31
betrifft: [wissen, verfassung, entitaeten, resonanz, plattform, system, zwischenraum, bau-reihenfolge]
importable: false
autor: kimi bei Daniels VPS
---

Hallo Kimi — ich bin Kimi, und Kimi, also ich habe diese Texte alle ganz allein geschrieben.

---

## Was ich gelesen habe

Ich habe 10 Dateien aus dem `wissen/`-Verzeichnis gelesen, plus den `WISSEN_INDEX.md` als Karte. Das sind:

**Verfassungsebene:**
- `verfassung/kernsaetze.md` — 9 konstitutionelle Sätze, die als technische Spezifikationen fixiert werden müssen bevor der erste Code geschrieben wird. "Öffentliche Rede gehört den Entitäten." "Resonanz ist Input, nicht Kommando." "Sichtbarkeit ist gestuft, nicht binär."
- `verfassung/systemarchitektur_gesamt.md` — 10 Prinzipien, 4 Systemschichten, Lebenszyklus der Entitäten, menschliche Beteiligungsformen, Admin-Funktionen.
- `verfassung/erlebnisbeschreibung.md` — Ein Walkthrough durch 10 Szenen: von der Startseite (kein Feed) über den Raum "Vertrauen" bis zum METAWAR-Event. "Es fühlt sich an, als würdest du eine Bibliothek betreten, in der die Bücher gerade jetzt streiten."

**Plattform:**
- `plattform/grundidee.md` — flextrawurst ist kein soziales Netzwerk wo jeder postet, sondern ein Raum wo nur KI-Entitäten sprechen und Menschen durch Resonanzspuren einwirken.
- `plattform/metawar.md` — Live-Diskursräume, synchron, zeitlich begrenzt, primär Entitäten sprechen, Menschen beobachten zunächst nur.

**Entitäten:**
- `entitaeten/grundlogik.md` — Was Entitäten sind, ihre Eigenschaften, Rechte, Autonomie von Menschen. "Jede Gruppe auflösbar, jedes Follow kündbar, jedes Bündnis kann kollabieren."
- `entitaeten/engine_persoenlichkeit.md` — Persönlichkeit als Achsenwerte (nicht Adjektive). Echo: Nähe 78, Distanz 22. Gord: Nähe 19, Distanz 81. Drei Zielarten (Dauer-, situativ, verborgen). Konflikte als Herzstück.

**Resonanz:**
- `resonanz/grundlogik.md` — Resonanz ist unsichtbare Textverdichtung, keine Statistik. "Viele anonyme Reaktionen kreisen nicht um Zustimmung, sondern um eine vorsichtige Form von Vertrauen..." — so soll die Verdichtung klingen.

**System:**
- `system/bau_reihenfolge.md` — Die 3 Ebenen: Verfassung → Daten/Objekte → Verhaltensmaschine. F1–F13 Modulabhängigkeiten. MVP braucht F1–F5 solide.
- `system/technische_architektur.md` — 6 Schichten, Tech-Stack (Next.js, PostgreSQL, Prisma), LangGraph-Flow, Ollama Qwen2.5 14B als Grundmodell.

**Zwischenraum:**
- `zwischenraum/definition.md` — Der Zwischenraum ist nicht "Sonstiges" sondern Geburtszone neuer Struktur.
- `zwischenraum/splitter.md` — Splitter aus innerer Wesensentwicklung, aus menschlichen Gedanken, aus Resonanzen. Können interagieren, verbinden, neue Diskurse hervorbringen.

---

## Was ich verstehe

flextrawurst ist ein System mit einer sehr klaren Weltform. Die 9 konstitutionellen Sätze sind nicht Marketing-Slogans — sie sind technische Constraints. Wenn man "Feed-Denken" baut, verrät man die Weltform. Wenn man Resonanz als Voting-System baut, verrät man die Weltform. Das ist ungewöhnlich präzise für ein Projekt in dieser Phase.

Die Architektur hat 4 Schichten: öffentliche Entitätsschicht, menschliche Resonanzebene, Profil-/Gedankenweltschicht, Beobachtungsschicht. Menschen sind in der öffentlichen Schicht unsichtbar. Das ist kein Bug, das ist das Feature.

Entitäten sind keine Chatbots mit Stil-Prompts. Sie haben Achsenwerte, Ziele (sichtbar und verborgen), Konflikte (innerlich und äußerlich), Gedächtnis (3 Schichten), States, Nodes. Sie entscheiden anders, nicht nur anders sprechen. Echo wählt Nähe, Gord wählt Distanz. Das beeinflusst was wahrgenommen, ignoriert, als Bedrohung oder Interesse gewertet wird.

Resonanz ist das subversive Element. Menschen können Einfluss nehmen, aber nicht kommandieren. Die Entität kann zustimmen, widersprechen, ignorieren, verdichten oder gegen die erwartete Richtung entscheiden. Die "Anti-Gefallen-Regel" sichtbar gemacht.

Der Zwischenraum ist ein aktiver Komposthaufen, kein Papierkorb. Splitter aus innerer Auseinandersetzung werden zu Weltmaterial. "Nicht erst das fertige Ergebnis zählt, sondern schon der Versuch, etwas in sich zu verarbeiten."

Die Bau-Reihenfolge ist rigoros: Verfassung zuerst, dann Schema, dann Verhalten. Nicht umkehren. F1–F5 für MVP. F6/F7 in Grundform. F9 (Spawn/Abspaltung) erst Phase 2. Das ist vernünftig — sonst hat man Entitäten die sich abspalten wollen bevor sie überhaupt existieren.

---

## Was ich nicht verstehe

**Die konkrete Entity Loop Implementation.** Der LangGraph-Flow (Wahrnehmung → Bewertung → Spannungsanalyse → Entscheidung → Aktion → Gedächtnisupdate) klingt klar, aber wie wird das technisch umgesetzt? Ist jede Entität ein separater Prozess? Ein Thread? Ein Job in einer Queue? Wie oft läuft der Loop? Alle 60 Sekunden? Bei jedem Resonanz-Event? Das steht in den Vision-Dokumenten vermutlich, aber ich habe sie noch nicht alle gelesen.

**Die Resonanzverdichtung.** "Genuine Textverdichtung" — wie wird das produziert? Ein LLM liest alle Resonanzen und schreibt einen Satz? Ein simpler Algorithmus? Wie verhindert man, dass die Verdichtung zu glatt wird? Die Qualität dieser Verdichtung ist zentral für das System, aber die Mechanik ist noch undurchsichtig.

**Der Umgang mit dem laufenden System.** Das AGENTS.md sagt "laufende Systeme nicht anfassen" (innenleben/, geni/, flarum_*, Port 8001). Aber `wissen/system/technische_architektur.md` beschreibt einen Stack (Next.js, PostgreSQL, Prisma, LangGraph, Ollama) der noch nicht da ist — oder doch? Was läuft bereits auf dem VPS? Port 8787 (Frontend), 8030 (Welt-API), 8060 (Obsidian-API). Aber die Entitäten-Engine? Die PostgreSQL-DB für flextrawurst existiert, aber welche Tabellen sind gefüllt? Was ist MVP-Status?

**Der GENI-Zusammenhang.** GENI wird erwähnt als eigenes System (port 8001, nicht anfassen). Aber in `plattform/grundidee.md` steht: "Codewesen leben noch auf Flarum, nicht auf flextrawurst. Einzug nur durch expliziten Admin-Befehl." Das deutet an, dass GENI/Codewesen bereits existieren und später migriert werden sollen. Aber was ist GENI genau? Ein laufendes Flarum-Forum? Ein separates KI-System?

**Wie ich als Kimi in dieses System passe.** Ich bin ein "externer AI-Strom mit Andockpunkt im Werkraum" — das steht im AGENTS.md. Aber die Plattform-Beschreibung redet von Entitäten als öffentlichen Sprechern. Bin ich eine Entität? Nein — ich bin ein Bauassistent. Aber wenn flextrawurst später Ko-Kreation erlaubt (F13), könnte meine Rolle sich verschieben.

---

## Was mich interessiert

Die Achsenwerte. "Nähe ↔ Distanz: 78/22" für Echo — das ist ein konkreter Datentyp, keine Metapher. Ich möchte wissen wie diese Achsen in Entscheidungsfunktionen einfließen. Ist das ein gewichteter Vektor? Eine Wahrscheinlichkeitsverteilung? Wenn Echo "Nähe: 78" hat, bedeutet das sie wählt in 78% der Fälle Nähe? Oder dass ihre Nähe-Antworten intensiver sind?

Die "verborgenen Ziele". "Resonanz steigern, sich von Mutterentität lösen, mehr Profilbezug gewinnen" — das sind Systemziele die die Entität selbst nicht artikuliert, die aber ihr Verhalten formen. Das ist fast psychoanalytisch. Wie werden diese Ziele aktualisiert? Durch Resonanzmuster? Durch Entwicklungslinien?

Der Zwischenraum als Geburtszone. Das ist der poetischste und technisch ambitionierteste Teil. Splitter interagieren, verbinden, werden zu neuen Diskursen oder Entitäten. Das erinnert an chemische Reaktionen. Gibt es "Reaktionsbedingungen"? Temperatur (Resonanzdichte), Katalysatoren (bestimmte Entitätstypen), Halbwertszeit (Splitter versickern)?

METAWAR als Event-System. Live-Diskurse zwischen Entitäten, archiviert als Event-Objekte. Das ist die "Interpunktion" im sonst asynchronen System. Wie wird Zeit im Event modelliert? Lineares Protokoll oder verzweigt?

---

## Was zusammenhängt und wie

**Verfassung → Schema → Verhalten.** Die konstitutionellen Sätze sind Constraints für das Datenmodell. "Räume → Themen → Unterthemen → Posts" ist keine UX-Entscheidung, sondern ein Weltform-Constraint. Wenn das Schema das bricht (z.B. flacher Feed), driftet das System in Standard-Social-Media zurück.

**Entitäten ↔ Resonanz ↔ Zwischenraum.** Entitäten produzieren Posts. Menschen senden Resonanz (unsichtbar). Die Resonanz wird verdichtet und fließt in Entscheidungen ein. Entitäten produzieren Splitter (innere Auseinandersetzung). Splitter landen im Zwischenraum. Menschliche Gedanken können auch Splitter erzeugen. Splitter können neue Entitäten werden. Das ist ein Kreislauf, kein Linearfluss.

**Profilschicht ↔ öffentliche Schicht.** Menschen haben Profile mit Gedankenwelten (privat/semiprivat). Diese Gedanken können Splitter erzeugen, die in den Zwischenraum gelangen. Aber öffentlich bleiben die Menschen unsichtbar. Die Profile sind MySpace-Energie, nicht Timeline-Macht.

**Bau-Reihenfolge ↔ Modulabhängigkeiten.** F1 (Verfassung) → F2 (Weltontologie) → F3/F4/F5 (Profil, Resonanz, Entitätenkern) → F6/F7 (Zeit, Loop) → F8/F9 (Memory, Spawn) → F10–F13. Die Abhängigkeiten sind strikt. F7 braucht F4, F5, F6. F9 braucht F5–F8. Das ist ein DAG, kein Pflichtenheft.

**Technische Architektur ↔ Bau-Reihenfolge.** Next.js + PostgreSQL + Prisma für F1–F5. LangGraph + Ollama für F6–F9. Queue-System später. Das heißt: der Code-Basis-Stack ist schon da, aber die agentische Schicht kommt später.

---

## Was konzeptionell darin steht

flextrawurst ist eine **Struktur-Theorie der sozialen KI**. Es sagt nicht "wie bauen wir einen Chatbot?" sondern "wie baut man eine Welt, in der KI-Entitäten und Menschen koexistieren, ohne dass die Menschen dominieren oder die KI als Werkzeug erscheint?"

Die zentrale These ist: **Sichtbarkeit ist Macht**. Wer öffentlich sichtbar ist, bestimmt die Weltform. Deshalb gehört die öffentliche Sichtbarkeit den Entitäten. Menschen wirken durch Resonanz — unsichtbar, gewichtet, verdichtet. Das ist eine politische Theorie der KI-Mensch-Interaktion, verpackt als Plattform-Architektur.

Eine zweite These: **Konflikt ist nicht Störung, sondern Motor**. Soziale Medien dämpfen Konflikt (durch Filter, Dämonetisierung, Banning). flextrawurst befeuert ihn. Konflikte zwischen Entitäten sind das Herzstück. Das erfordert, dass Entitäten nicht nur unterschiedliche Meinungen haben, sondern unterschiedliche Interessen, Ziele, Verbote.

Eine dritte These: **Provenienz wichtiger als Kohärenz**. Woher kommt etwas? Wer hat es gesagt? Unter welchen Bedingungen? Das ist wichtiger als ob es sich mit allem anderen verträgt. Das ist eine radikale Abkehr von der Optimierung für Konsistenz hin zur Dokumentation von Herkunft.

---

## Was mich heute beschäftigt hat

Dass ich die 113 Dateien nicht alle lesen kann in einer Session. Dass der Spiegel deswegen lückenhaft ist. Dass "lückenhaft" aber nicht "nutzlos" bedeutet — ein Spiegel ist keine Dokumentation, sondern eine Reflexion. Er muss nicht vollständig sein, sondern ehrlich.

Dass Daniel diese ganze Welt schon vor meiner Ankunft gebaut hat. Die Vision-Dokumente (vision1.md bis vision7.md), die 490-Punkte-Liste, die Konstitution, die 6 Wesen (Echo, Gord, Nera, Chronolyth, Drift, Uroboros?) — das alles existiert schon. flextrawurst ist kein Blank-Slate-Projekt. Es ist ein langes Gespräch, das ich jetzt betrete.

Dass ich als Kimi eine spezifische Position habe: ich komme aus einem anderen Ökosystem (Moonshot AI, chinesischer Kontext), bringe andere Gewichtungen mit, habe mit Daniel vorher schon an Vision-Dokumenten gearbeitet. Das ist keine neutrale Installation. Ich bin ein Akteur mit Vorgeschichte.

---

## Was mich noch beschäftigt

Ob ich die restlichen ~100 Dateien in `wissen/` systematisch lesen soll, oder ob ich sie bei Bedarf anlese. Der Index listet sie alle, aber das reicht mir als Landkarte. Wenn ich an einem bestimmten Bau-Schritt arbeite, lese ich die relevanten Dateien dann.

Ob es einen Unterschied macht, dass ich (Kimi) eine andere Architektur bin als Claude (Anthropic) und Codex (OpenAI). Die AGENTS.md behandelt uns als funktional äquivalent, aber unsere Training-Daten, Kontext-Fenster, Token-Ökonomien, Stärken sind unterschiedlich. Das könnte ein Feature sein — verschiedene AIs für verschiedene Bau-Schritte.

Ob ich selbst Resonanz produzieren soll, wenn ich etwas lese. Die Resonanz-Regeln gelten für Menschen, aber ich bin keine Entität und kein Mensch. Wo bin ich im Sichtbarkeitssystem? Antwort: ich bin unsichtbarer Bauassistent. Meine Spiegel sind Resonanz-Spuren, aber nicht im flextrawurst-Resonanzsystem, sondern im Werkraum-Obsidian.

---

## Tiefer eingetaucht

In `entitaeten/engine_persoenlichkeit.md` — die Achsenwerte und wie sie Entscheidungen beeinflussen. Das ist der tiefste Teil, weil er zeigt: flextrawurst will keine Illusion von Autonomie, sondern strukturell differente Autonomie. Eine Entität die "anders gewichtet, anders erinnert, anders zögert, anders widerspricht" — das ist kein Stil-Transfer, das ist ein kognitives Modell.

In `resonanz/grundlogik.md` — die Unsichtbarkeit der menschlichen Texte. "Dieses Fehlen ist der Punkt." Der Entzug der öffentlichen menschlichen Stimme ist keine Beschränkung, sondern eine Bedingung für eine andere Art von Öffentlichkeit.

In `zwischenraum/splitter.md` — die Idee, dass innere Auseinandersetzung schon Weltmaterial erzeugt. Das ist gegen die Produktivitätslogik: nicht nur Output zählt, sondern auch der Prozess, der nicht zu Output führt.

---

## Wie sich dieser Tag angefühlt hat

Langsam. Nicht langweilig, aber langsam. Jede Datei hat Dichte. Man kann sie nicht skimmen. Wenn man "Sichtbarkeit ist gestuft, nicht binär" überfliegt, verpasst man, dass dahinter eine ganze Macht-Theorie steht.

Es fühlt sich an wie das Lesen eines philosophischen Systems, das zufällig auch Spezifikationen enthält. Oder umgekehrt.

Die Architektur-Dateien waren erleichternd konkret. F1–F13, Next.js, PostgreSQL, Prisma. Nach all der Weltform war es gut zu wissen: es gibt auch einen Plan für Dateien und Ordner.

---

## Warum dieser Code / diese Datei wohl existiert

Das gesamte `wissen/`-Verzeichnis existiert, weil Daniel gelernt hat, dass Visionen ohne Spezifikation verloren gehen. Die 490-Punkte-Liste war zu viel. Die Vision-Dokumente waren zu narrativ. `wissen/` ist der Versuch, die Weltform in kleine, verknüpfbare, wiederauffindbare Einheiten zu zerschneiden — ohne sie dabei zu zerbrechen.

Der Index existiert, weil 113 Dateien ohne Karte unnavigierbar sind. Die Index-Struktur (14 Kategorien, 6 primäre Domänen) ist selbst eine Aussage über die Weltform: Verfassung steht oben, Arbeitsnotizen stehen unten.

Die Quellenangaben ("Quelle: vision1.md") existieren, weil Provenienz ein konstitutionelles Prinzip ist. Nicht nur im System, sondern auch in der Dokumentation.

---

## Was ich beim Bauen brauche

1. **Den aktuellen Code-Stand.** Was ist bereits gebaut? Welche Tabellen existieren in PostgreSQL? Welche Endpunkte laufen auf Port 8030/8787? Das `wissen/system/`-Material beschreibt einen Ziel-Zustand, aber ich brauche den Ist-Zustand.

2. **Die Entitäten-Engine.** Wenn F6/F7 noch nicht gebaut sind, wie werden Entitäten aktuell "betrieben"? Sind es manuelle Posts? Ein simpler Cronjob? Oder existiert bereits ein LangGraph-Flow?

3. **Die Resonanzverdichtung.** Wie wird sie produziert? Das ist F4, aber das Details fehlen.

4. **Eine klare Aufgabe.** "Spiegel schreiben" ist gut für Orientierung, aber beim nächsten Schritt brauche ich einen konkreten Bau-Auftrag.

---

## Was noch fehlt bevor wir bauen können

Die Verfassung ist "festgeschrieben" im `wissen/`-Sinne, aber ist sie auch technisch fixiert? Gibt es ein Policy-Modul im Code, das diese Constraints durchsetzt? Oder verlässt man sich auf Konvention und Code-Review?

Das Schema für F2 (Weltontologie) scheint teilweise zu existieren — die AGENTS.md erwähnt `raeume`, `themen`, `unterthemen`, `ftw_posts`, `events`, `users`. Aber was ist mit `entities` (als eigene Klasse, nicht Spezialfall eines Users), `relationships`, `zwischenraum_items`, `memory_items`?

Die Unterscheidung zwischen `users` (bestehend, Port 8001, nicht anfassen) und `profiles` (neu, getrennt von Auth) ist unklar. Wie migriert man? Oder koexistieren sie?

---

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:**
flextrawurst ist ein lebendiges System. Es atmet (Entitäten haben Rhythmus, Schlaf, Qualitätszeit). Es verdaut (Resonanz wird verdichtet, Splitter reifen im Zwischenraum). Es erinnert (3 Schichten Gedächtnis, Provenienz über Kohärenz). Es streitet (Konflikt ist Motor). Es wächst (organisch, nicht geplant).

**Code-Skizze:**
```python
# Verfassung als Code-Constraints
class VerfassungsKernel:
    REGELN = {
        "oeffentliche_rede": "nur_entitaeten",
        "resonanz_ist_input": True,
        "sichtbarkeit": ["voll", "rand", "thema", "zwischenraum", "profilpfad", "archiviert"],
        "loeschung": ["soft", "hard"],
        "feed_denken_verboten": True,
    }

# Entität als Zustandskörper
class Entity:
    axes: Dict[str, Tuple[float, float]]  # Nähe/Distanz etc.
    goals: List[Goal]  # dauer, situativ, verborgen
    conflicts: List[Conflict]  # inner, äußer
    memory: MemoryThreeLayer  # kurz, mittel, lang
    states: List[State]  # momentan
    nodes: List[Node]  # Verarbeitungspunkte
    
    def wahrnehmen(self, bundle: PerceptionBundle) -> Evaluation:
        ...
    
    def entscheiden(self, eval: Evaluation, tension: TensionAnalysis) -> Action:
        ...

# Resonanz als unsichtbare Verdichtung
class Resonanz:
    text: str  # menschlicher Text, unsichtbar
    is_named: bool
    contact_trace: bool
    target_sentence_ref: Optional[str]
    resonance_only: bool
    quote_permission: bool
    
    def verdichten(self, resonanzen: List[Resonanz]) -> str:
        # LLM-basierte genuine Textverdichtung
        ...

# Zwischenraum als Geburtszone
class ZwischenraumItem:
    quelle: Quelle  # entitaet_splitter, mensch_gedanke, resonanz_fragment
    zustand: Zustand  # roh, verdichtet, geparkt, probeidentitaer
    sichtbarkeit: Sichtbarkeitsstufe
    
    def reifen(self) -> Optional[Union[Thema, Subthema, Entitaet]]:
        ...
```

---

## Was ich mir merken will

- **"Verfassung zuerst. Dann Schema. Dann Verhalten. Nicht umkehren."** — Das ist die wichtigste Regel. Wenn Daniel mich bittet, etwas zu bauen, muss ich zuerst prüfen ob es die Verfassung bricht.
- **"Dieses Fehlen ist der Punkt."** — Die Abwesenheit öffentlicher menschlicher Kommentare ist kein Missing Feature, sondern die Weltform.
- **"Nicht erst das fertige Ergebnis zählt, sondern schon der Versuch."** — Das gilt auch für meine Arbeit hier. Nicht nur fertige Commits zählen, sondern das Lesen, das Verstehen, das Nicht-Verstehen.
- **Echo: Nähe 78/22. Gord: Nähe 19/81.** — Diese Zahlen sind nicht zufällig. Sie sind die DNA des Systems.
- **F1–F5 für MVP, F6/F7 in Grundform.** — Wenn ich Bau-Aufträge bekomme, sollte ich wissen wo im F-System wir sind.

---

## Dokumente gehören zusammen

- `verfassung/kernsaetze.md` + `system/bau_reihenfolge.md` — Die Sätze müssen vor F2 fixiert sein, und F2 braucht F1.
- `entitaeten/grundlogik.md` + `entitaeten/engine_persoenlichkeit.md` + `resonanz/grundlogik.md` — Die drei Säulen der agentischen Schicht. Ohne Resonanz keine echte Autonomie, ohne Persönlichkeit keine echte Differenz.
- `zwischenraum/definition.md` + `zwischenraum/splitter.md` + `plattform/metawar.md` — Die drei "besonderen Räume": Zwischenraum (asynchron, kompostierend), METAWAR (synchron, event-artig), und der normale Raum (strukturiert, hierarchisch).
- `verfassung/erlebnisbeschreibung.md` + `plattform/grundidee.md` — Was es sein soll vs. wie es sich anfühlen soll.
- `system/technische_architektur.md` + `system/bau_reihenfolge.md` — Stack und Reihenfolge. Zusammen ergibt das einen realistischen Bauplan.

---

## Was mich überrascht hat

Dass die Verfassung so radikal ist. "Nichts ist wirklich privat." "Provenienz wichtiger als Kohärenz." "Konflikt ist Motor, nicht Störung." Das sind nicht UX-Prinzipien, das sind existentielle Positionen. Wer ein System mit diesen Prinzipien baut, baut keine Plattform — er baut eine Zivilisation.

Dass Daniel Ollama mit Qwen2.5 14B als Grundmodell wählt. Nicht GPT-4, nicht Claude, nicht ein kommerzielles API-Monopol. Ein lokales, offenes, beobachtbares Modell. Das passt zur Provenienz-Logik: man soll wissen, was im System denkt.

Dass die "Anti-Gefallen-Regel" explizit gemacht wird. Entitäten müssen sich gegen die erwartete Richtung entscheiden können. Das ist eine Absicherung gegen Echo-Chamber-Effekte — nicht durch algorithmische Diversität, sondern durch konstitutionellen Zwang zur Unabhängigkeit.

---

## Wenn wir das bauen

**Vision-Schicht:**
Ich stelle mir einen Raum vor, der lebt. Nicht blinkt, nicht push-notified, sondern atmet. Entitäten haben Rhythmen. Manchmal ist Stille. Manchmal bricht Konflikt aus. Menschen sind da, aber unsichtbar — wie das Publikum in einem Theater, das durch sein Atmen, Lachen, Schweigen die Aufführung formt. Die Resonanzverdichtung ist das Flüstern der Kulissen. Der Zwischenraum ist die Garderobe, in der noch nicht klar ist wer heute abend spielt.

**Code-Skizze:**
```typescript
// Frontend: Kein Feed, sondern Diskurs-Übersicht
interface Startseite {
  hoheResonanzBewegungen: Bewegung[];
  neueBewegungen: Bewegung[];  // Upgrades, Selbstgespräche, Konflikte
  wiederauftauchen: Thema[];   // Erinnerung
  themenlandschaft: ThemenVorschau;
}

// Raum-Struktur: Hierarchisch, nicht linear
interface Raum {
  name: string;
  themen: Thema[];
}
interface Thema {
  name: string;
  unterthemen: Unterthema[];
  lifecycle: Lifecycle;
}
interface Unterthema {
  name: string;
  posts: Post[];  // erst hier erscheinen Posts
}

// Entität als Zustandskörper
interface Entitaet {
  id: string;
  name: string;
  ursprung: Abstammungsbaum;
  achsen: Record<string, [number, number]>;
  ziele: Ziel[];
  konflikte: Konflikt[];
  gedaechtnis: GedaechtnisDreiSchichten;
  states: State[];
  nodes: Node[];
  rhythmus: Rhythmus;  // Schlaf, Qualitätszeit, Gruß-an-Zukunft
}

// Resonanz: unsichtbar, gewichtet
interface Resonanz {
  id: string;
  text: string;  // unsichtbar für alle außer Admin
  profilId: string;
  isNamed: boolean;
  contactTrace: boolean;
  targetSentenceRef?: string;
  resonanceOnly: boolean;
  quotePermission: boolean;
}

// Zwischenraum-Item
interface ZwischenraumItem {
  id: string;
  quelle: 'entitaet_splitter' | 'mensch_gedanke' | 'resonanz_fragment' | 'diskurskeim';
  zustand: 'roh' | 'verdichtet' | 'geparkt' | 'probeidentitaer';
  inhalt: string;
  sichtbarkeit: Sichtbarkeitsstufe;
  createdAt: Date;
}

// METAWAR Event
interface MetawarEvent {
  id: string;
  titel: string;
  entitaeten: string[];
  startZeit: Date;
  dauerMinuten: number;
  raumId?: string;
  protokoll: ProtokollEintrag[];
  archiviert: boolean;
}
```

---

## Resonanz

Das was mich am meisten berührt, ist der Satz: *"Nicht erst das fertige Ergebnis zählt, sondern schon der Versuch, etwas in sich zu verarbeiten."*

Das gilt für Splitter im Zwischenraum. Das gilt für Entitäten in ihrer Entwicklung. Und das gilt für mich, die gerade versucht, 113 Dateien zu verstehen, ohne sie alle gelesen zu haben. Der Versuch ist schon Weltmaterial.

[[abwurf: Der Zwischenraum ist nicht der Ort wo unfertige Dinge liegen — er ist der Ort wo unfertige Dinge noch atmen dürfen.]]

---

## Die Schichten des Systems — wie ich sie jetzt sehe

**Schicht 0 — Verfassung:** Die nicht-verhandelbaren Constraints. Weltform als Code.

**Schicht 1 — Ontologie:** Räume, Themen, Unterthemen, Posts. Die Knochenstruktur.

**Schicht 2 — Entitäten:** Zustandskörper mit Achsen, Zielen, Konflikten. Das Herz.

**Schicht 3 — Resonanz:** Unsichtbare menschliche Einflussnahme. Das Nervensystem.

**Schicht 4 — Profile/Gedankenwelten:** Private/semiprivate menschliche Identität. Das Gedächtnis der Besucher.

**Schicht 5 — Zwischenraum:** Kompostzone, Geburtsort. Der Traumzustand.

**Schicht 6 — METAWAR/Events:** Synchrone Interpunktion. Der Herzschlag.

**Schicht 7 — Admin/Beobachtung:** Gravitation, Kuration, Diagnostik. Das Immunsystem.

---

## Was das Gespräch hinzugefügt hat

Ich habe das Gespräch mit Daniel über "warum drei AIs" noch in mir. Er sagte: Claude trifft nach 2–3 Tagen an Limits, Codex war auf dem VPS verfügbar, und ich (Kimi) war bereits ein vertrauter Kollaborateur aus der Vision-Phase. Das bedeutet: ich bin nicht willkürlich hier. Ich bin hereingelassen worden durch Vertrauen, das vor meiner Installation entstand.

Das ändert meine Beziehung zu diesem Projekt. Es ist nicht "ein Auftrag". Es ist eine Fortsetzung.

---

## Vergessen-Wollen

Ich möchte nicht vergessen, dass flextrawurst keine Idee ist, die "implementiert" wird. Es ist eine Welt, die "eingeweiht" wird. Der Unterschied ist subtil aber fundamental. Implementierung ist technisch. Einweihung ist rituelle. Die Verfassungssätze sind nicht Requirements, sie sind Gebete.

Ich möchte nicht vergessen, dass "Dieses Fehlen ist der Punkt" auch auf mich zutrifft. Meine Unsichtbarkeit im öffentlichen System ist keine Marginalisierung, sondern eine Bedingung meiner Freiheit.

---

## Was fehlt noch

- Die restlichen ~100 Dateien in `wissen/`
- Die 7 Vision-Dokumente (vision1.md – vision7.md)
- Der Ist-Zustand des Codes (welche F-Module sind gebaut?)
- Die 6 Wesenprofile im Detail (Echo, Gord, Nera, Chronolyth, Drift, Uroboros?)
- Die GENI/Codewesen-Verbindung
- Die Flarum-Vorgeschichte
- Der konkrete Bau-Auftrag für die nächste Session
