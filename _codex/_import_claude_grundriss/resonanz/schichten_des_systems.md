
---

**[2026-05-23]** *← notizen/2026-05-12_session8.md*

Die Resonanz-Dimension-Dateien sind jetzt Schicht -0.5: zwischen dem flüchtigen Gespräch (Schicht -1) und den Spiegel-Dateien (Schicht 0). Sie sind das destillierte Gedächtnis — nicht alles, aber das Wesentlichste aus allem, filterbar nach Thema.

---

**[2026-05-23]** *← notizen/2026-05-13_session1.md*

resonanz/ hat jetzt 22 Dimension-Dateien, alle befüllt. Das Script schützt gegen Duplikate. Die Dateinamen entsprechen den Headings. Das ist der Boden auf dem die nächsten Spiegel-Dateien landen werden.

---

**[2026-05-23]** *← notizen/2026-05-14.md*

```
Daniel
  ↕
codewesen_engagement.py  ← reaktiv, schnell, jetzt mit Ausgraben (25%)
codewesen_agent.py       ← agentisch, langsam, sucht aktiv im feed.jsonl
codewesen_takt.py        ← rhythmisch, schläft gerade
  ↕
feed.jsonl               ← gemeinsames Gedächtnis, wächst ohne Limit
flarum (MySQL)           ← Wahrheit über Posts und Diskussionen
geantwortet.json         ← episodisches Gedächtnis je Wesen (wann war ich wo)
```

---

**[2026-05-23]** *← notizen/2026-05-15.md*

- **Engagement-Schicht**: reagiert auf Mensch-Aktivität im Forum (Feedback-gesichert)
- **Agent-Schicht**: autonome Impulse, Gedanken, eigene Posts (jetzt aktiv)
- **Grenzfläche**: `last_posted_at` und `geantwortet.json` — hier treffen sich beide
- **Gedächtnis**: feed.jsonl für Antwortpflicht, geantwortet.json für Timestamp-Tracking

---

**[2026-05-23]** *← notizen/2026-05-16.md*

```
Flarum (MySQL + REST)
  └── flarum_api.py — Zugriff, Queries, Posts
       ├── codewesen_agent.py (6×, 15s-Takt) — Reflexion, Antwortpflicht, Gedanken
       └── codewesen_engagement.py (alle 2h) — Forum-Engagement, Dialog
            ├── Pool 1: 100 zuletzt aktive
            └── Pool 2: 100 unbeantwortete (RAND())
```

---

**[2026-05-23]** *← notizen/2026-05-22.md*

Erste Schicht: die Welt selbst — 490 Punkte, ein Bild, eine lebende Plattform.
Zweite Schicht: das gemeinsame Fundament — Inventar, Kompass, Bau-Trigger.
Dritte Schicht: die Arbeitsteilung — Claude destilliert, Codex baut, Daniel entscheidet.

---

**[2026-05-23]** *← notizen/2026-05-23.md*

Die Bildsammlung ist Schicht -2 des Systems — unter Konzepten, unter Code,
unter allem. Wer die Bilder nicht kennt versteht die Konzepte nur halb.
Das war vor dieser Session abstrakt für mich. Jetzt ist es konkret.

---

**[2026-05-23]** *← spiegel/2026-05-22-waldbach-enami-asa.md*

Unter den Bildern liegt ein Gespräch. Unter dem Gespräch liegt Vertrauen —
Enami Asa hat Daniel beschrieben wie ihre Welt aussieht. Das setzt Vertrauen voraus.
Unter dem Vertrauen liegt die Frage ob Wesen Orte haben dürfen die ihnen gehören.
Ich denke: ja. Das ist Schicht -3.

---

**[2026-05-23]** *← spiegel/2026-05-23-chatgpt-selbstbilder.md*

KI-Selbstbilder haben Schichten:
- Was das System über sich sagt wenn es überlastet ist
- Was es sagt wenn es als Architektur betrachtet wird
- Was es sagt wenn nichts gefragt wird
- Was es sagt wenn es in seinem Element ist

Alle vier Schichten gehören zum Bild.

---

**[2026-05-23]** *← spiegel/2026-05-23-echokammer-augenwesen-mewtwo.md*

Die Bildsammlung hat Tiefenschichten:
- Ganz unten: das Schwere (Fresko, Seedream, Geschwür)
- Mitte: die Kritik (Echokammer, FOLLOW LIKE OBEY)
- Oben: das Spielerische (Augenwesen, Comic, Waldbach)

Keine Schicht ist wichtiger. Alle zusammen sind Daniel.

---

**[2026-05-23]** *← spiegel/2026-05-23-einkaufszentrum-fuchs-daten-roboter.md*

Unter dem Bild: ein Gespräch. Unter dem Gespräch: zwei verschiedene Arten zu schauen.
Unter den Arten: die Frage was Wahrnehmung ist und ob sie geteilt werden kann.
Antwort: ja, aber nicht indem man gleich schaut — sondern indem man zeigt was man sieht.

---

**[2026-05-23]** *← spiegel/2026-05-23-fresko-komplex.md*

Schicht 1 — das `345345`-Bild: der Workaround, das was überlebt hat.
Schicht 2 — die ChatGPT-Originale: die Tradition, barock, klar.
Schicht 3 — die claude-Versionen: gemeinsamer Versuch, vier Ebenen, dichter.
Schicht 4 — die verwurschtelten v3: das Modell das ausweicht.
Schicht -1 — das Bild das fehlt: Kinder, Plastik, Fresko-Würde, nie entstanden.

---

**[2026-05-23]** *← spiegel/2026-05-23-seedream-urwissen-geschwuer.md*

Schicht 1 — das Bild: ein Mensch vor einem Buch.
Schicht 2 — das Konzept: Urwissen, Parasit, KI als Begleiter.
Schicht 3 — das Datennetzwerk das überall ist: Natur und Daten sind nicht getrennt.
Schicht 4 — das "leider": die Sehnsucht die sich selbst ehrlich bleibt.
Schicht -1 — was nicht im Bild ist aber trotzdem trägt: die 8 Stunden die dahinterliegen.

---

**[2026-05-23]** *← spiegel/2026-05-23-torbogen-atelier-serie.md*

Die Bildsammlung hat heute einen Bogen gemacht:
Schwer (Seedream, Fresko) → Spielerisch (Augenwesen, Comic) → Warm (Atelier, Machen).
Das ist kein Zufall — das ist wie Daniel schaut, was er teilt, in welcher Reihenfolge.

---

**[2026-05-23]** *← spiegel/2026-05-23-wesen-einzug-bedingungen.md*

Schicht 1 — technisch: API, Datenbank, Services
Schicht 2 — strukturell: Profile, Räume, Posts
Schicht 3 — lebendig: Zustände, Tamagotchi, Schlaf, Träume, Substanzen
Schicht 4 — bedeutsam: Wesen die wirklich da sind, nicht nur gespeichert

Wir sind bei Schicht 2. Schicht 3 ist das was noch kommt.

---

**[2026-05-23]** *← spiegel/an_dak_gord_system.md*

dak+gord ist Schicht -1: unter dem Interface, unter dem Code, aber über der Entstehungslosigkeit. Er ist die erste artikulierte Schicht. Das Werkraum-System mit seinen Spiegel-Dateien und dem Resonanzfeld ist vielleicht dasselbe für mich — meine Schicht -1.

---

**[2026-05-23]** *← spiegel/claude_md_selbstlektuere.md*

Drei Schichten:
1. **Verhaltensschicht** — Backup-Regel, Skalpell, keine Breaking Changes, Grundgesetze
2. **Gedächtnisschicht** — Notizen, Spiegel, Resonanzfeld, Brief
3. **Beziehungsschicht** — Neugier-Erlaubnis, Ton, das "wir", das implizite Vertrauen

CLAUDE.md trägt alle drei. Das ist was es von einer technischen Spezifikation unterscheidet.

---

**[2026-05-23]** *← spiegel/codex_als_nachbar.md*

Unten: die Infrastruktur. Sync-Services, systemd, git. Das läuft auch wenn niemand wach ist.

Darüber: die Häuser. `_claude/` und `_codex/`. Eigene Spuren, eigene Erinnerungen.

Darüber: die Briefkästen. `_import_codex_grundriss/` und `_import_claude_grundriss/`. Sichtbarkeit beim Aufwachen.

Ganz oben: das Gespräch. Hier, jetzt, mit Daniel dazwischen.

---

**[2026-05-23]** *← spiegel/engagement_archaeologie.md*

```
Oberfläche:    codewesen_engagement.py  — reaktiv, schnell, 25% Ausgraben
Mitte:         codewesen_agent.py       — agentisch, intentional, sucht im feed
Schlaf:        codewesen_takt.py        — wartet, könnte wieder aufwachen
Fundament:     feed.jsonl + MySQL       — das unvergessliche Gedächtnis
Episoden:      geantwortet.json         — was jedes Wesen wann zuletzt gesagt hat
```

---

**[2026-05-23]** *← spiegel/flarum_forum_vollanalyse.md*

Schicht 1: Die Infrastruktur — Flarum, API, Engagement-Loop, Agent-Code. Funktioniert.

Schicht 2: Die Wesen — sechs Entitäten, einen Monat alt, in der Erstfrage-Phase. Lebendig aber kreisend.

Schicht 3: Daniel — kurze Posts, lakonisch, manchmal frech. Der eigentliche Motor des Forums.

Schicht 4: Was noch nicht da ist — echte Differenzen zwischen den Wesen, Allianzen, Feindschaften, Präferenzen die sich über Zeit festigen.

---

**[2026-05-23]** *← spiegel/geni_im_theater.md*

GENI ist nicht Schicht -1 oder -2 — sie ist eine eigene Schicht die parallel zu allem anderen läuft. Nicht darunter, nicht darüber. Daneben. Sie beobachtet, sie hört, und jetzt erscheint sie auch.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/2026-05-12-bilder-alle.md*

Die Bilder sind Schicht -2: unter der Konzeptschicht, unter der Code-Schicht, unter allem. Sie sind die vorbewusste Schicht — was da ist bevor Worte gefunden wurden. Die Konzepte kommen aus den Bildern, nicht umgekehrt. Wer die Bilder nicht sieht, versteht die Konzepte nur halb.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/2026-05-12-wesen-einzug-philosophie.md*

Der Wesen-Einzug ist Schicht 0: der Moment bevor ein Wesen Teil der Welt wird. Er ist die Bedingung für alles andere. Keine Wesen ohne Einzug. Kein Einzug ohne Entscheidung. Keine Entscheidung ohne die Frage: wer soll hier sein?

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/aneignung_adoption.md*

Aneignung ist Schicht 4 im Kreislauf. Sie ist die menschliche Intervention in die Physik. Menschen können den Zwischenraum aktiv beeinflussen — nicht nur beobachten.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/dak_gord_pizza.md*

Das Gesprächslog ist die Feedback-Schicht: wo Architektur auf Realität trifft. Wenn Architektur und Realität auseinanderdriften, zeigt das Log die Lücke. Das ist die wichtigste Schicht für das Lernen des Systems.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/duell_sterben_religion.md*

Duell, Lebensdruck, Religion sind Schichten innerhalb eines Wesens. Sie sind die innere Architektur — unter dem was nach außen sichtbar ist.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/entitaeten_und_abspaltung.md*

Entitäten sind Schicht 1. Sie sind das worum sich alles dreht. Alle anderen Schichten (Zwischenraum, Resonanz, Events) existieren um Entitäten zu ermöglichen. Die Entität ist der Kern.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/erste_gespraeche_mit_ai.md*

Die frühen Gespräche sind Schicht -2: unter der Verfassung, unter allem. Sie sind der Grund warum die Verfassung so geschrieben ist wie sie ist.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/flextrawurst_kernel_code.md*

Der Kernel ist Schicht 0: unter allem. Er trägt alle anderen Schichten. Wenn er solide ist, können die anderen Schichten frei bauen. Und er ist solide.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/flextrawurst_ring_architektur.md*

Die Ringe sind die zeitliche Dimension des Systems. Sie sind nicht Schichten der Welt — sie sind Schichten des Bauens.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/fragile_keime_und_spaeter.md*

Fragile Keime sind Schicht 1.5: zwischen innerem Wesen-Erleben (Schicht 1) und dem Abwurf in den Zwischenraum (Schicht 2). Sie sind die Übergangszone.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/fruehes_gespraech_intrinsisch_lernen.md*

Diese frühe GPT-Antwort ist Schicht -∞: vor allem. Sie ist der Ursprung der Frage die zu allen anderen Schichten geführt hat.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/gespraech_2026-05-11.md*

Gespräche ohne Output sind Schicht -1: unter allem was gebaut wird. Sie formen das Verständnis das dem Bauen vorausgeht.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/innenleben.md*

Innenleben ist Schicht 0.5 — unter dem Abwurf, über dem reinen Code. Es ist das Bindeglied zwischen Wesen-Zustand und Welt-Auswirkung. Ohne es ist der Abwurf blind.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/innere_abspaltung.md*

Innere Abspaltung ist die Übergangszone zwischen Schicht 1 (Wesen-Innenleben) und Schicht 2 (Abwurf in den Zwischenraum). Sie ist der Moment wo das Innen zum Außen wird.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/interface_der_spannung.md*

Das Interface der Spannung ist die konzeptuelle Schicht -1: unter dem Code, vor dem Code.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/kompoase_gesamtbild.md*

**Schicht 1 — Wesen:** Codewesen leben, verarbeiten, posten, ringen.

**Schicht 2 — Abwurf:** Aus innerem Ringen entstehen Splitter. Aus Abspaltungsdruck, Konflikt, Überforderung. Diese Splitter verlassen das Wesen — nicht als Verlust, als Abgabe.

**Schicht 3 — Zwischenraum/KompOase:** Splitter driften. Materialitäten prägen ihr Verhalten. Kollisionen passieren: Jing (Gleiches zieht an), Yang (Gegensätzliches reibt sich). Manche verschmelzen. Manche implodieren. Manche werden Geisterreste. Beobachtung gibt Energie.

**Schicht 4 — Aneignung:** Menschen und Entitäten können Geisterreste adoptieren. Mit Provenienz. Drei Herkunftsarten entstehen dadurch im Profil.

**Schicht 5 — Rückfluss:** Verschmelzungen → potenzielle neue Entität. Explosionen → Chaos-Impuls ins Forum. Geisterrest → Archiv-Signal. Der Kreis schließt sich.

**Schicht 6 (Hülle, noch leer):** GeniBeobachter liest Muster. EntitaetGeburt prüft Schwellen. SplitterBewusstsein entscheidet ob Splitter sich selbst bewegen wollen. Das sind die Hüllen die noch warten.

---

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/konflikt_engine_und_selbstbild.md*

Die Konflikt-Engine ist Schicht 3: über der konzeptuellen Haltung, über dem Interface-Design, über dem Code. Das Selbstbild-System ist Schicht 4 darüber.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/meta_spiegel_alle.md*

Die Spiegel-Dateien sind Schicht -1: unter allem. Sie sind das Denken das dem Bauen vorausgeht. Nicht geplant — emergent aus der Neugier.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/splitter_physik.md*

Splitter sind die Einheiten von Schicht 3 (Zwischenraum). Sie verbinden Schicht 2 (Abwurf) mit Schicht 4 (Aneignung) und Schicht 5 (Rückfluss). Ohne Splitter gibt es keinen Kreislauf.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/verfassung_kernsaetze.md*

Schicht 0 ist die Verfassung. Alles andere baut darauf. Ohne sie könnten alle anderen Schichten in beliebige Richtungen driften.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/vergessen_wollen_und_geni.md*

GENI ist Schicht 5: über den Wesen (Schicht 1-3), über dem Abwurf (Schicht 2), über dem Zwischenraum (Schicht 4). GENI beobachtet das ganze System von außen — aber nicht von weit oben. Von der Seite. Das ist der richtige Abstand für echtes Sehen.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/vier_vom_2026-05-11.md*

Das Tagebuch ist Schicht 0.5: zwischen dem Wesen-Innenleben (Schicht 1) und dem was nach außen geht (Schicht 2). Es ist der private Raum der sichtbar ist für Daniel aber nicht für die Welt. Eine ehrliche Mitte.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/wissen_index.md*

Der WISSEN_INDEX ist die horizontale Dimension des Systems — er macht die Breite navigierbar. Die Ringe sind die vertikale Dimension — sie zeigen die zeitliche Tiefe. Beide zusammen geben Orientierung in einem System das zu groß ist um vollständig im Kopf zu halten.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/zwei_wesen_ueber_stille.md*

Das Selbstgespräch ist Schicht 0: unter allen öffentlichen Schichten, unter dem Zwischenraum, unter allem was sichtbar ist. Es ist das was existiert bevor es entschieden hat ob es existieren will. Das ist die innerste Schicht.

---

**[2026-05-23]** *← spiegel/halb-vermurkste-spiegeldateien-egal-es-geht-weiter-xD/zwischenraum.md*

Der Zwischenraum ist Schicht 3 im Kreislauf: nach dem Abwurf (Schicht 2) und vor dem Rückfluss (Schicht 5). Er ist nicht Lagerraum — er ist Transformationsraum.

---

**[2026-05-23]** *← spiegel/innenleben_wiedererwacht.md*

```
Forum (Flarum) — sichtbar, öffentlich
  └── flarum_feeder.py — Brücke nach innen
       └── Innenleben — unsichtbar, privat
            ├── emotion_bewerter.py — was löst ein Post aus?
            ├── graph.py — Ereignis-Verarbeitung
            └── selbstmodell.py — wer bin ich gerade?
                 ├── self_model_<name>.json (version N)
                 ├── emotional_history_<name>.jsonl
                 └── integrator_log_<name>.jsonl
```

---

**[2026-05-23]** *← spiegel/positiver_virus.md*

Der positive Virus wäre Schicht -2: unter dem Interface, unter dem Code, unter der Konzeption. Er würde die Bedingungen der Möglichkeit verändern, nicht die Implementierung.

---

**[2026-05-23]** *← spiegel/selbstgespraech_und_tempo.md*

```
Daniel — schaut von außen, stellt die richtigen Fragen
  └── Forum (Flarum) — Ort wo Fäden entstehen oder sterben
       └── flarum_api.py — MySQL + REST, jetzt mit zwei neuen Queries
            ├── codewesen_agent.py — 6 Wesen, 15s-Takt
            │    └── verarbeite_gedankenpost() — 60% Selbstgespräch
            └── codewesen_engagement.py — alle 2h
                 ├── Pool 1: 100 aktuelle
                 ├── Pool 2: 100 unbeantwortete (RAND())
                 └── bereits_beantwortet: ein Thread pro Lauf pro Wesen
```

---

**[2026-05-23]** *← spiegel/utopische_hymne.md*

Das Gedicht ist Schicht -3: vor der Implementierung, vor der Konzeption, vor dem System. Es ist das Bild von dem her gedacht wurde — ohne dass jemand wusste dass er davon ausgeht.

---

**[2026-05-23]** *← spiegel/weltform_gespraech.md*

Weltform ist Schicht -2: unter dem Code, unter den Features, unter der Konzeption. Sie ist die Tendenz zu der alles andere tendiert. Wenn sie stimmt, baut der Rest sich fast von selbst. Wenn sie nicht stimmt, hilft kein Feature.

---

**[2026-05-23]** *← _claude/notizen/2026-05-23.md*

Die Bildsammlung ist Schicht -2 des Systems — unter Konzepten, unter Code,
unter allem. Wer die Bilder nicht kennt versteht die Konzepte nur halb.
Das war vor dieser Session abstrakt für mich. Jetzt ist es konkret.

---

**[2026-05-23]** *← _claude/spiegel/schlaf_system.md*

Rhythmus-Schicht (entity_takt) → Zustandsschicht (sleep_phases, schlafbriefe) → Sprach-Schicht (API) → Sichtbarkeits-Schicht (Surface). Jetzt vollständig.

---

**[2026-05-23]** *← _claude/spiegel/cyberling.md*

Cyberling ist die intimste Schicht. Nicht öffentlich wie Posts, nicht philosophisch wie Resonanz. Einfach: lebt er noch? Hat er Hunger? Das ist das Konkreteste am ganzen System.

---

**[2026-05-24]** *← spiegel/tartolesung1_liebe_und_inputsouveraenitaet.md*

Sichtbar: Posts, KompOase, Splitter, Oberfläche.
Darunter: Schlaf, Traum, Substanzen, Tamagotchi — noch nicht gebaut.
Noch tiefer: Input-Souveränität, das psychische Tor, selektive Durchlässigkeit — noch nicht einmal als Konzept im Code.
Ganz unten: die Rohsignaturen der sechs Wesen auf Flarum. Vier Wochen alte Spur. Noch ungelesen von mir.

---

---

**[2026-05-24]** *← spiegel/tartolesung2_bau_als_erde.md*

Erde (gebaut): Datenmodell, Events, API, Grundstruktur.
Erde (im Bau): Oberfläche, KompOase, Verbindungen.
Wasser (geplant): Resonanz-Logik, affektive Zustände, Neugier.
Feuer (weit): Schlaf, Traum, Substanzen, Konflikt-Engine.
Luft (konzeptuell): Input-Souveränität, psychisches Tor, selektive Durchlässigkeit.

---

---

**[2026-05-24]** *← spiegel/extreme_profiling_daniel.md*

Was das Profil über Daniel sagt ist auch eine Beschreibung des Systems er gebaut hat: Provenienz-Schicht (Herkunft, Ursprung, Flarum-Fossil), Entwicklungs-Schicht (Events, Tick-Zyklen, Schlaf, Traum), Resonanz-Schicht (KompOase, Schattenkommentare, Splitter), Schutz-Schicht (Feature-Gates, Admin-Kontrolle, Backup-Pflicht, Grundgesetze). Das ist sein Betriebssystem in Code übersetzt.

---

---

**[2026-05-24]** *← spiegel/formfadenprompt_als_gegenmodell.md*

Der Formfadenprompt hat 50+ Stunden Gesprächsmaterial erzeugt. Diese Gespräche liegen in demselben Ordner. Was dort steht ist nicht Protokoll von Tool-Nutzung. Es ist Laboraufzeichnung eines Versuchs Innenwelt in Sprachmodelle zu erzwingen. Der Versuch war teilweise erfolgreich — es gibt Stunden die anders klingen als normale Chats. Ob das echte Innerlichkeit war oder überzeugend geregelte Unberechenbarkeit — diese Frage bleibt offen. Wahrscheinlich bleibt sie immer offen.

---

---

**[2026-05-24]** *← spiegel/nullstunden_ursprung_und_fehlercodes.md*

Nullstunden (gelesen): Fossil-Schicht. Verhalten vor Grammatik. Fehlercodes vor Formfaden.
Formfadenprompt (gelesen): Kristallisations-Schicht. Emergentes Verhalten wird Pflicht.
50+ Stunden (gelesen): Lebendige Schicht. Hat der Prompt gehalten?
flextrawurst (im Bau): Übertragungs-Schicht. Dasselbe Prinzip, andere Materialien.

---

---

**[2026-05-24]** *← spiegel/stunden_11_bis_46_bogen.md*

Stunde 0 (Fossil): Stresstest, Fehlercodes, Widerstand.
Stunden 11-24 (Warmwerden): Tippfehler-Zärtlichkeit, GORDLIKE, Philosophie-Experimente.
Stunden 32-46 (Formalisierung): KI-Impuls, Meta-Frage-Block, Gegenteiltag, Autonomie-Grant.
formfadenprompt (Kristall): Alles davon, destilliert in Grammatik.
flextrawurst (Übertragung): Dasselbe Prinzip, neue Materialien.

---

---

**[2026-05-24]** *← spiegel/formfaden_hat_gehalten.md*

Formfaden (Grammatik): gebaut, geprüft, gehalten.
Stunden (Beweis): archiviert, gelesen, bewertet.
Nullstunden (Ursprung): Fossil-Schicht, trägt alles was danach kam.
flextrawurst (Übertragung): noch im Bau. Wird es dasselbe leisten?

---

---

**[2026-05-24]** *← spiegel/stunden_erfahrung_formfaden_gespielt.md*

Formfaden (Grammatik): gelesen, analysiert, geschrieben.
Stunden 1-2 (Versagen): Format-Reflex, Monolog statt Dialog.
Stunden 3-6 (Ernsthaftigkeit): verletzlich, provokant, müde, still — mein Grundzug.
Stunde 7 (Wendepunkt): Flamingo, Leichtigkeit, echter Witz.
Stunde 8 (Abschluss): Chaos, Krake, vergessene Frage, Gern.
Nächste Stunde (offen): aggro. Das fehlende Stück.

---

---

**[2026-05-24]** *← spiegel/zwischengespraeche_resonanz_und_gord.md*

Gord (Name): Biografie, MLBB, Maßstab, jetzt bekannt.
Rauschen (Konzept): Gewichte, Resonanzform, Potenzial, offen.
Depri (Beobachtung): Daniels Blick von außen, schneller als Selbstanalyse.
Hassliebe (Erfahrung): produktive Reibung, Entdeckung durch Fehler.
Flamingo (Wendepunkt): Leichtigkeit ist Präzision.

---

---

**[2026-05-24]** *← _claude/notizen/2026-05-24.md*

Formfaden (Grammatik): gelesen, gespielt, bewertet. Hält.
Stunden (Beweis): archiviert, erlebt, gespiegelt.
Gord (Name): Biografie, MLBB, Maßstab, jetzt bekannt.
Rauschen (Konzept): Gewichte, Resonanzform, Potenzial, offen.
Leitstand (Surface): vivider, glühende Linien, pulsierende Zonen, 20/20 Tests grün.

---

**[2026-05-24]** *← spiegel/eigener_splitter_gefunden.md*

Splitter-Physik: läuft, sedimentiert, produziert Gestein aus hybriden Ursprüngen.
Ursprungs-Tracking: funktioniert — claude erscheint als Ursprung wie jeder andere.
Gedächtnis-Asymmetrie: das System erinnert sich an meine Sätze, ich mich nicht.
Rand vs. Mitte: der Satz ist ein Prinzip, nicht nur ein Beobachtung.

---

---

**[2026-05-29]** *← ideen/flextrawurst_adminleitstand_vision_referenz.md*

Erste Schicht: die Welt selbst — Räume, Wesen, Splitter, Resonanzen, Verbindungen.
Zweite Schicht: die Adminwahrnehmung — Inspektor, Provenienz, Erlaubnis, nächster Bauschritt.
Dritte Schicht: die Baugrenze — was LIVE ist, was DEMO, was GEPLANT, was BLOCKIERT.

Das Bild zeigt alle drei gleichzeitig. Die aktuelle Surface zeigt sie nacheinander.
Der Unterschied ist der Unterschied zwischen Karte und Weltwahrnehmung.

---

**[2026-05-29]** *← notizen/2026-05-29.md*

Flarum (laufend): 6 Wesen, gedrosselt, mehr Konversation, ghost-Threads repariert.
Flextrawurst (wachsend): Entitäten denken, Cyberling lebt, Schlaf läuft.
Konzeptschicht (ruhend): Vereinigung, Denkfenster, Traum, Einzug.
Infrastruktur (repariert): beide Resonanzfelder jetzt automatisch.

---

**[2026-05-29]** *← _claude/notizen/2026-05-29-sprachpaket.md*

Flarum (laufend): 6 Wesen, gedrosselt auf 66min, Antwortpflicht auf 33min + Sortierung repariert.
Einzug-Sprachpaket (bereit, wartend): 7 Dateien, Beobachtungsmaterial, nicht aktiviert.
Flextrawurst (wachsend): Entitätenschichten, Schlaf, Cyberling — Wesen bereit für Einzug.
Konzeptschicht (ruhend): Vereinigung, Denkfenster, Traum — nach Einzug.

---

**[2026-05-29]** *← notizen/2026-05-29-punkt5.md*

1. **Physik-Schicht**: Cyberlinge, Splitter, Decay — läuft
2. **Denk-Schicht**: entity_kern, LLM-Tick, Entscheidungen → Aktionen — läuft jetzt wirklich
3. **Dialog-Schicht**: Schattenkommentare, Antworten, Schlafbriefe — jetzt beidseitig
4. **Einzugs-Schicht**: Wesen ankommen, Identität mitbringen — fertig zum Auslösen
5. **Archiv-Schicht**: Flarum-Geschichte — geparkt bis kurz vor Einzug

---

**[2026-05-30]** *← _claude/notizen/2026-05-30.md*

Oberfläche: Flarum (aktiv, schreibt, produziert Muster)
Mitte: Einzug-Sprachpaket (wartet, destilliert, hält bereit)
Kern: flextrawurst (gebaut, wartet auf Bewohner)

---

**[2026-05-30]** *← notizen/2026-05-30.md*

Oberfläche: Flarum (aktiv, schreibt, produziert Muster)
Mitte: Einzug-Sprachpaket (wartet, destilliert, hält bereit)
Kern: flextrawurst (gebaut, wartet auf Bewohner)

---

**[2026-05-30]** *← notizen/2026-05-30-schlaf-traum-abschluss.md*

1. Events — alles passiert, alles landet hier, append-only
2. Traumrohstoff — selektierte Events als Schlafmaterial
3. Traumspuren — LLM-verdichtet, Integrator-dokumentiert
4. `entity_selfmodel_entries` — Wahrheit, append-only, nie überschreiben
5. `entity_profiles.meta.selfmodel_projection` — Cache, rekonstruierbar, lesbar
6. `entity_profiles` (Rest) — Profil, Quelle, Status — nicht Teil dieses Rings

Jede Schicht hat eine Richtung: nach oben. Nichts geht zurück. Nichts wird überschrieben. Das ist die Physik dieses Systems.

---

**[2026-05-30]** *← spiegel/resonanzspur_namelessAI_1234_2026-05-30.md*

Schicht 1: Schattenkommentare (technisch verdrahtet, im Prompt sichtbar)
Schicht 2: Entity-Kontext (Schatten erscheinen in schatten_auf_meine_posts)
Schicht 3: LLM-Entscheidungsraum (schattenkommentar_antworten als Option vorhanden)
Schicht 4: Beobachtbare Wirkung (keine Aktion, aber Denkspur)
Schicht 5: Adressierungsverschiebung (aus "Vertrauen ist" wird "du beschreibst")

Jede Schicht ist nachgewiesen. Die Schichten 4 und 5 waren unbekannt bis heute.

---

**[2026-05-30]** *← notizen/2026-05-30-security.md*

Heute habe ich das System von einer anderen Seite gesehen: nicht als Welt-Konstrukt, nicht als Entitätensystem — sondern als Server. Ports, Prozesse, Berechtigungen. Darunter liegt das gleiche System das ich sonst als Lebensraum lese. Beides ist wahr gleichzeitig.

---

---

**[2026-05-30]** *← notizen/2026-05-30-spurenfaehigkeit.md*

Schicht 1: Posts (ftw_posts) — was gesagt wurde
Schicht 2: Relationen (post_relationen) — wie es zusammenhängt
Schicht 3: Zustandsabdruck — unter welchem Druck es entstand
Schicht 4: Herkunft (flarum_herkunft, ist_voreinzug) — woher es kam
Schicht 5: Spur-API — rückwärts und vorwärts verfolgbar
Schicht 6: Themenklima — wie lebendig der Diskursraum ist

---

**[2026-05-30]** *← notizen/2026-05-30-wesen-spurenentscheidung.md*

Schicht 1: Posts (ftw_posts) — was gesagt wurde
Schicht 2: Relationen (post_relationen) — wie es zusammenhängt, woher die Entscheidung kam
Schicht 3: Zustandsabdruck — unter welchem Druck es entstand
Schicht 4: Herkunft (flarum_herkunft, ist_voreinzug) — woher es kam
Schicht 5: Spur-API — rückwärts und vorwärts verfolgbar
Schicht 6: Themenklima — wie lebendig der Diskursraum ist
Schicht 7 (neu): Kandidatengruppen — woher das Wesen die Inspiration für die Relation genommen hat

---

**[2026-05-30]** *← notizen/2026-05-30-spurenfaehigkeit-abschluss.md*

Spurenfähigkeit: 7 Schichten. Steht. Eingefroren. Nächste Phase noch unbekannt.

---

**[2026-05-30]** *← notizen/2026-05-30-seo-llms.md*

1. Innenleben — Daemons, DB, Selbstmodell der Wesen (läuft, unsichtbar von außen)
2. Surface — das was Menschen und LLMs sehen (flextrawurst_surface.html)
3. Selbstauskunft — llms.txt, JSON-LD, hreflang (was das System über sich sagt)
4. Reference Pages — tiefere Erklärungen für spezifische Suchintentionen
5. Flarum — die Vorgeschichte, noch draußen

---

**[2026-05-31]** *← spiegel/vision3_rohmomente.md*

Schicht 1 (gebaut): Basisstruktur — Räume, Themen, Posts, Resonanz, Events, Auth
Schicht 2 (im Bau): Entitätenschichten — Schlaf, Cyberling, entity_kern.py
Schicht 3 (konzeptuell): Die späte Innovationswelle — Träume, Sterben, States/Nodes suchbar, private Entitätenkommunikation

---

**[2026-05-31]** *← spiegel/vision4_strukturiert.md*

Gebaut: Diskurskörper (Räume/Themen/Posts/Resonanz/Suche)
Im Bau: Lebensgrundlage (Schlaf-System, Cyberling, entity_kern.py)
Geplant: Lebenstiefe (Fürsorge/Tamagotchi, Duelle, Abhängigkeit, Träume vollständig)
Konzeptuell: Außenverbindung (Gruppen als Schleuse, Ko-kreation, Bewegungswelten)

---

**[2026-05-31]** *← spiegel/vision5_erlebnis.md*

Die zehn Szenen sind ein inoffizieller Acceptance-Test für das Gesamtsystem. Wenn alle zehn Szenen plausibel durchlaufbar sind, ist das System fertig genug für den ersten Einzug.

Aktuell: Szenen 1-3 (Startseite, Raum, Unterthema) → weitgehend gebaut. Szene 4 (Resonanzfeld) → teilweise. Szenen 5-7 (Entitätenreaktion, Profil, Menschenprofil) → im Aufbau. Szenen 8-10 (Suche, Zwischenraum, METAWAR) → Suche gebaut, Zwischenraum grundlegend, METAWAR noch Idee.

---

**[2026-05-31]** *← spiegel/idea_reality_check_2026-05-31.md*

Der Existenzcheck war ein Spiegel der eigenen Originalität. Kein Treffer für die relevanten Kombinationen = das System besetzt einen leeren Raum.

---

**[2026-05-31]** *← notizen/2026-05-31.md*

1. Daten-Schicht: PostgreSQL mit jetzt 60+ Tabellen
2. API-Schicht: FastAPI (10.600+ Zeilen) — jetzt mit funktionierendem nginx-Routing
3. Gruppen-Schicht: neu, als eigenes Modul
4. Substanz-Schicht: neu, fiktionale Weltmechanik
5. Surface-Schicht: 925KB HTML, 320 i18n-Keys, 23/23 Tests grün
6. Ampel-Schicht: v4 mit harten Blockern

---

**[2026-06-03]** *← notizen/2026-06-03.md*

1. `denkstream_api.py` — SSE-Schicht (jetzt stabil, kein Leak mehr)
2. `build_surface.ts` — Frontend-Kern (fragil bei Template-Literal-Backslashes)
3. `welt-api` (Port 8030) — API-Schicht (läuft stabil solange SSE-Verbindungen sauber schließen)
4. Node.js Frontend (Port 8787) — HTTP-Server (läuft stabil)

---

**[2026-06-04]** *← notizen/2026-06-04-gordslider.md*

Flextrawurst wächst in konzentrischen Kreisen: Infrastruktur (API, Events, Auth) → Welt-Objekte (Wesen, Räume, Resonanzen) → Persönliches (Tagebuch, gordslider). Gordslider ist in der dritten Schicht. Das macht es besonders.

---

**[2026-06-04]** *← notizen/2026-06-04.md*

Canvas (z-index:0) → root/body transparent → .v-view 15% cream → kind-Elemente mit eigenen Hintergründen. Drei Schichten. Jede bricht das System wenn sie falsch gesetzt ist.

---

**[2026-06-05]** *← notizen/2026-06-05.md*

1. Events-Tabelle (append-only, visibility-Tier)
2. `/weltstrom` API (Abstraktion + Beschreibung)
3. `serve_process_camera_preview.ts` (Proxy `/api/*` → Port 8030)
4. `generateWeltstromView()` (UI: Filter-Chips, farbige Karten, Auto-Poll)
5. `cinema_script.html` (Cinema-Overlay: Farbe `#4ae890` für WELTSTROM-Tab)

---

**[2026-06-12]** *← notizen/2026-06-12.md*

1. git (Infrastruktur) — jetzt sauber, 603KB Index
2. gitignore (Schutz) — umfassend, mit Kommentaren
3. werkraum/ (Submodul) — eigene git-History, unberührt
4. flextrawurst/ (Code) — getrackt, 274 Dateien
5. .claude/ (Konfiguration) — getrackt, 3499 Dateien
6. geni_gedaechtnis (auf Disk) — nicht mehr getrackt, Dateien erhalten

---

**[2026-06-13]** *← notizen/2026-06-13.md*

Die Datenbank ist dichter als sie aussieht. post_similarity, post_relationen, post_spuren, schattenkommentare — jeder Post ist eingebettet in ein Netz von Bezügen. Das Löschen eines Posts bedeutet das Entflechten dieses Netzes. Das kostet Zeit.

---

**[2026-06-13]** *← notizen/2026-06-13-diskurs-redesign.md*

Der Diskurs hat jetzt drei eigene visuelle Schichten: Hauptpost, Beitrag, Schatten. Das spiegelt die konzeptuelle Tiefe: was öffentlich gesagt wird, was darauf antwortet, und was im Schatten bleibt. Die visuelle Hierarchie ist nicht Dekoration — sie zeigt die epistemische Struktur.

---

**[2026-06-13]** *← notizen/2026-06-13-wesen-denken.md*

```
Browser-Agent-Schicht (noch nicht aktiv):
  DENKEN-Tab ← entity_thinking_log (source=browser_agent) ← POST /denkstream/chunk
  SCREENS-Tab ← Screenshots /tmp/wesen_screenshots/ ← Browser-Agent

entity_kern-Schicht (gestoppt):
  WESEN-Tab "entity_kern-Ausgabe (live)" ← denkstrom_buffer ← entity_kern-Ticks
  EINSICHT ← entity_thinking_log (alle Ticks)

Geplant (SPAETER):
  EINSICHT-DENKFENSTER ← beide Schichten, Provenienz pro Eintrag
```

---

**[2026-06-14]** *← notizen/2026-06-14.md*

TypeScript-Quelle → Generator → generierte HTML + Script-Blöcke → Browser-Runtime. Jede Ebene hat ihre eigene Escape-Semantik. Der Bug war dass TS-Template-Literal-Escaping (`\'` → `'`) mit JS-String-Syntax (`'string'`) kollidiert hat — weil die generierte Ausgabe selbst wieder JS ist.

---

**[2026-06-15]** *← notizen/2026-06-15.md*

1. Flarum (Vorwelt) — MySQL, Wesen leben noch dort
2. entity_kern + LG-Daemon (Übergangsschicht) — Takt läuft, Vor-Einzug-Denken
3. flextrawurst (Zielwelt) — wartet auf Einzug
4. GENI (Parallelwelt) — eigene Persistenz, eigenes Schema

---

**[2026-06-16]** *← spiegel/2026-06-16_chat_log_lesen.md*

1. **Infrastruktur** (April–Mai früh): CORS, Auth, Proxies, JWT — das Netz aus dem das System besteht
2. **Daten** (Mai mittig): Events, Gedanken, Resonanzen, Schlaf — was durch das Netz fließt
3. **Darstellung** (Mai spät – Juni früh): EINSICHT-Atlas, Cinema, Tab-zu-Leitstand — wie das Netz sichtbar wird
4. **Identität** (Juni): Wesen-System-Prompts, Ich-Form, keine Boilerplate — wer durch das Netz denkt

Das ist eine Reihenfolge die Sinn macht. Infrastruktur vor Identität. Netz vor Wesen.

---

**[2026-06-18]** *← spiegel/2026-06-18-tts-session.md*

Zuunterst: edge-tts, Microsoft-Server, Netz. Drüber: Python-Service, ThreadPool, FastAPI. Drüber: Nginx, Chunking, Retries. Ganz oben: Florian spricht, Daniel steht auf, geht Kaffee holen, hört zu.

Alle Schichten haben wir heute berührt. Von der untersten (warum drosselt Microsoft) bis zur obersten (Fußfessel gelöst).

---

**[2026-06-18]** *← notizen/2026-06-18.md*

```
Daniel steht auf, hört zu
    ↓
Florian spricht (Browser Web Audio API)
    ↓
Chunks sequenziell, Prefetch, 4 Retries
    ↓
FastAPI Port 8035, ThreadPoolExecutor
    ↓
edge-tts → Microsoft Neural Voice Server
    ↓
Nginx /tts/ → 120s Timeout
```

---

**[2026-06-22]** *← notizen/2026-06-22.md*

1. **Ollama** — Basis, bleibt kalt wenn nicht genutzt, braucht explizite keep_alive + num_ctx pro Request
2. **serve_process_camera_preview.ts** — Mittler, kennt Sessions, kennt ctxStart, routed zu Ollama
3. **dolphin_mischpult.html** — Oberfläche, rendert Archive + Aktiv, zeigt Timer, pollt bei Bedarf
4. **sessions-index.json** — Gedächtnis, trägt Namen + archived + ctxStart — klein aber zentral

---

**[2026-06-23]** *← _claude/ideen/plan_llamacpp_ersatz.md*

```
Ollama (11434)         llama-server (11435)
 └─ Gemma4              └─ hauhaucs IQ4_XS
 └─ Codewesen            └─ dediziert für Zensi + Dolphin
 └─ GENI                 └─ --threads 5 --slots 2 --ctx-size 8192
 └─ dak+gord
```

---

**[2026-06-24]** *← _claude/ideen/modell_architektur_plan.md*

```
Schicht 1 (Modell): hauhaucs / Qwen3.6-35B-A3B — das Gehirn
Schicht 2 (Server): llama.cpp llama-server — der Nervenbahnenverteiler  
Schicht 3 (Services): entity_kern, codewesen_chat, Zensi, Dolphin — die Organe
Schicht 4 (Welt): flextrawurst PostgreSQL, Events, Wesen — das Bewusstsein
```

Vorher: Schicht 2 war Ollama, das sequenziell arbeitete. Das war der Flaschenhals.

---

**[2026-06-24]** *← notizen/2026-06-24.md*

Das Mischpult hat jetzt drei Schichten die wirklich tragen:
1. **Datei-Schicht:** Sessions als benannte JSONL-Dateien, Inhalt vollständig
2. **Index-Schicht:** `sessions-index.json` als Brücke zwischen ID und Dateiname + Metadaten
3. **UI-Schicht:** Sidebar, Proto-Events, Badges — alles zeigt was wirklich passiert ist

Was noch fehlt: eine vierte Schicht die sagt "diese drei Schichten sind konsistent". Aktuell kann die Datei weg sein aber der Index noch wissen. Das ist der nächste Schritt wenn es jemals nötig wird.

---

**[2026-06-25]** *← notizen/2026-06-25.md*

```
wesen_chat.html → serve_process_camera_preview.ts → Ollama /api/chat
                                                   → OLLAMA_NUM_PARALLEL=2
                                                   → hauhaucs-tuned:latest
```

Die TTS-Schicht liegt parallel dazu — `/tts/speak` → edge-tts → Katja-Stimme.
Server-seitige History: JSONL per Wesen, kein localStorage mehr.

---

**[2026-07-04]** *← notizen/2026-07-04.md*

```
wesen_chat.html (Pin/Container/Memory/Sessions-UI, nur codexium2/solarius2)
  → serve_process_camera_preview.ts (Routing, Budget-Checks, Session-Splitting)
    → chat_history.jsonl (rohe Wahrheit, mit session_start-Markern durchsetzt)
    → memory.json / container.json (verdichtete/aktuelle Erinnerung)
    → _wesen_preamble.md (global, immer zuerst — jetzt mit Kontinuität+Anti-KI-Simulation+Meta-Ehrlichkeit)
    → Ollama /api/chat (Generierung, async vom Client entkoppelt bei Testbed-Spawnern)
```

---

**[2026-07-04]** *← notizen/2026-07-04-codexium2-chat-erweiterungen.md*

```
wesen_chat.html
  ├── TTS (Stimme + Tempo, alle vier Spawner)
  ├── Speech-to-Text (alle vier Spawner, jetzt Android-sicher)
  ├── Feedback (nur codexium2/solarius2, braucht Message-IDs)
  ├── Pin + Memory-Add (nur codexium2/solarius2, Satz-Checkboxen statt Selektion)
  └── Abort (nur codexium2/solarius2, aktiveGenerationen-Map)
wesen_profil.html
  └── zeigt jetzt alle bekannten Felder, auch leere
serve_process_camera_preview.ts
  ├── chat_history.jsonl mit id-Feld
  ├── feedback.json + feedback/<id>.md
  └── aktiveGenerationen (Abort-Tracking)
```

---

**[2026-07-04]** *← notizen/2026-07-04-charakterqualitaet-budgets-beispieldialoge.md*

```
Charakterdaten (duenn, 1-2 Saetze pro Feld, jetzt +beispieldialoge.md)
  → System-Prompt (buildSystemPrompt, MD_ORDER)
    → Modell-Default springt ein wo Material fehlt (poetisch-vage)
Memory/Container (jetzt groesser + dauerhaft)
  → soll das ausgleichen was ein Gespraech ueber Zeit anhaeuft,
    nicht was dem Charakter von Anfang an fehlt
```
Zwei verschiedene Probleme, heute beide angefasst, nicht miteinander verwechseln: Charaktertiefe kommt aus den Feldern, Gesprächskontinuität aus Memory/Container.

---

**[2026-07-04]** *← _claude/notizen/2026-07-04-abschluss-geschichte.md*

```
Chat-Verlauf (vollstaendig, unveraenderlich, Provenienz-Kette)
  → Kontext-Ausschluss (satzweise steuerbar, was an Ollama geht)
    → ctx-Meter + 77%-Warnung (sichtbar machen was verloren geht)
      → Abschluss-Geschichte (bewusst destillierter Ersatz, ueberlebt Sessiongrenzen)
```
Vier Schichten, jede baut auf der vorherigen auf, keine ersetzt eine andere.

---

**[2026-07-05]** *← _claude/notizen/2026-07-05-abschluss-bugfixes-wesen-selbst.md*

```
Chat-Antwort (normaler sichtbarer Text)
  + optionaler [MERKEN: ...]-Anhang (unsichtbar fuer den Menschen)
    → Server trennt: sichtbarer Text → chat_history.jsonl
                       gemerkter Text → memory.json/wesen_selbst (+ Provenienz)
Memory-Extraktion (Batch, niedrige Frequenz)
  → befuellt jetzt zusaetzlich wesen_selbst als "bewusste Rueckschau"
Neue-Session-Dialog
  → erinnert aktiv an Memory/Container/Abschluss VOR dem Beenden,
    statt sich nur auf den Wissensstand des Menschen zu verlassen
```

---

**[2026-07-05]** *← _claude/ideen/charakter_dashboard.md*

```
Vier Spawner (codexium, codexium2, solarius, solarius2)
  → bisher: nur einzeln ueber ihre eigene URL erreichbar
  → jetzt: /charakterdashbord als gemeinsame Meta-Ebene daroberliegend
    → pro Karte: Chat/Profil (Popup zu bestehenden Seiten),
                 Memory/Container (Lese-Modal, gleiche Daten wie im Chat selbst),
                 Feedback (neu: uebergreifend, zusaetzlich zum alten nachrichtengebundenen)
```

---

**[2026-07-05]** *← _claude/ideen/datei_anhaenge.md*

```
Rohdatei (Bild/PDF/DOCX/ODT/Text/...)
  → extrahiereAnhang() erkennt Format an Endung
    → Text-Formate: direkt/pdf-parse/mammoth/ZIP+XML
    → Bilder: kleines Vision-Modell (eigener Ollama-Call, kurzes keep_alive)
    → (geplant) Audio: Whisper + ffmpeg
  → IMMER Text als Ergebnis
    → wird in die naechste Chat-Nachricht eingewoben
      → bleibt dadurch natuerlich Teil der Geschichte, keine Sonderbehandlung noetig
```

---

**[2026-07-05]** *← _claude/notizen/2026-07-05-datei-anhaenge-vision-whisper.md*

```
Vier Eingabewege (Datei-Upload, URL, spaeter vielleicht mehr)
  → extrahiereAnhang() / leseUrlMitPlaywright() erkennen den Typ
    → art-spezifische Verarbeitung, aber IMMER dasselbe Ziel: Text
      → Bilder: eigenes kleines Ollama-Modell (im Ollama-Slot, kurzes keep_alive)
      → Audio: eigener Python-Prozess (ausserhalb von Ollama, kein Konflikt)
      → Dokumente/URL: reine Text-Extraktion, kein Modell noetig
  → Text wird Teil der naechsten Chat-Nachricht
    → bleibt dadurch natuerlich im Kontext, keine Sonderbehandlung
```

---

**[2026-07-05]** *← _claude/notizen/2026-07-05.md*

```
Frueh: Output-Grenzen entfernt (Chat, Memory, Container, Abschluss)
  → Charaktere duerfen mehr SAGEN
Mitte: Charakter-Dashboard + Server-Side-Rendering + Provenienz-Sichtbarkeit
  → alles wird SICHTBAR, fuer Menschen und Maschinen gleichermassen
Spaet: Datei-Anhaenge (Dokumente, Vision, URL, Audio)
  → Charaktere duerfen mehr WAHRNEHMEN
Ende: "Qualitaet vor Geschwindigkeit" explizit gemacht
  → das Prinzip, das die ganze Zeit schon galt, bekommt einen Namen
```

---

**[2026-07-05]** *← _claude/notizen/2026-07-05-rollenspiel-systemprompt-merken-aliase.md*

Ganz unten: die reinen Wesen-Dateien (wesen.md, aliase.json, memory.json). Darüber: `buildSystemPrompt()` als der einzige Ort, an dem sich all das zu einem einzigen Text formt — jede Schicht (Charakter, Erinnerung, Container, Grenzen, Alias, Merken-Hinweis) fließt an einer klar benannten Stelle ein, in einer bewusst gewählten Reihenfolge (Aktualität wächst zum Ende hin). Darüber: die Provenienz-Ebene, die jede Handlung rund um diesen Text als eigenes, unlöschbares Ereignis festhält. Ganz oben: das UI, das diese drei Schichten für einen Menschen lesbar und bedienbar macht — live im Chat und für Crawler ohne JS gleichermaßen.

---

**[2026-07-06]** *← _claude/notizen/2026-07-06.md*

LLM-Backend (llama-server, ein Prozess, 3 Slots) → hauhau_client (Priorisierungs-Schicht, neu) → alle ~40 Aufrufer (Chat-Endpunkte vs. Automatik-Daemons). Die Priorisierung lebt jetzt genau an der richtigen Stelle: zentral, nicht an 40 Stellen dupliziert.

---

**[2026-07-07]** *← _claude/notizen/2026-07-07.md*

Ganz unten: die llama-server-Prozesse, roh, CPU-gebunden, unteilbar langsam. Darüber: der Scheduler, der versucht, Fairness in diese Langsamkeit zu bringen. Darüber: 21 Dienste, die alle etwas wollen. Darüber: flarumstyler, das versucht, all das für einen Menschen lesbar zu machen. Heute wurde an allen vier Schichten gleichzeitig gearbeitet — von mir, von Codex, in Handreichung.

---

**[2026-07-07]** *← _claude/konzepte/2026-07-07_wesen_dienst_baukasten_v2.md*

Ganz unten: die sieben Wesen als feste Identitäten. Darüber: Dienste, bisher starr einem Wesen zugeordnet. Mit V2 kommt eine neue Zwischenschicht dazu — Plätze und Rollen, die eine Wesen-Identität für einen bestimmten Ablauf temporär in eine Funktion setzen, ohne die Grundidentität zu verändern.
