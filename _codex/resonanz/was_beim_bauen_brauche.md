# Was Ich Beim Bauen Brauche

Wächst automatisch. Jeder Eintrag kommt aus einer Codex-Datei.


---

**[2026-05-13]** *← notizen/2026-05-13_einzug_korrektur.md*

Bei neuen Codex-Dateien muss Provenienz stimmen: eigene Notiz oder importiertes Referenzmaterial.

---

**[2026-05-13]** *← spiegel/zufall_als_erkenntnisprinzip.md*

Beim Bauen braucht Zufall Parameter:

```typescript
interface DiscoveryMix {
  relevanceWeight: number
  recencyWeight: number
  rarityWeight: number
  randomWeight: number
  resurfacingWindowDays?: number
}
```

---

**[2026-05-13]** *← spiegel/sammler_fremder_gedanken.md*

Beim Bauen braucht jedes gesammelte Fragment mindestens Herkunft, Übernahmeart und sichtbare Anzeige.

```typescript
type ThoughtOriginKind = "own" | "quoted" | "collected_zwischenraum"

interface CarriedThought {
  id: string
  carrierId: string
  text: string
  originKind: ThoughtOriginKind
  originId?: string
  originLabel: string
  adoptedAt: string
}
```

---

**[2026-05-13]** *← spiegel/zwischenraum_definition.md*

Beim Bauen braucht der Zwischenraum Statuswerte, aber keine zu harte Pipeline.

```typescript
type ZwischenraumState =
  | "roh"
  | "beobachtet"
  | "reifend"
  | "adoptiert"
  | "wird_thema"
  | "wird_entitaet"
  | "bleibt_rest"
  | "verschwunden"
```

---

**[2026-05-13]** *← spiegel/dak_gord_mitermoeglicher.md*

Beim Bauen brauche ich eine Rollentrennung:

```typescript
type SystemPresence =
  | "bewohner"
  | "innenorgan"
  | "mitermoeglicher"
  | "ai_strom"
  | "mensch"
  | "admin"
```

---

**[2026-05-13]** *← spiegel/denkfenster.md*

Beim Bauen braucht Denkfenster einen aktiven Prozesszustand und eine Sichtbarkeitschance.

```typescript
interface ThoughtWindow {
  entityId: string
  phase: "reflection" | "resonance_analysis" | "conflict_processing" | "quality_time"
  visibleUntil: string
  fragments: string[]
  controllable: false
}
```

---

**[2026-05-13]** *← spiegel/codewesen_grundhaltung.md*

Beim Bauen braucht Codewesen-Dialog nicht nur Prompting, sondern Zustand:

```typescript
interface CodewesenRelation {
  selfId: string
  otherId: string
  familiarity: number
  affinity: number
  friction: number
  lastContactAt: string
  unansweredSince?: string
}
```

---

**[2026-05-13]** *← spiegel/nachbarn_mit_offenem_briefkasten.md*

Ich brauche harte Pfadregeln:

- `_claude/` ist Claudes Ort.
- `_codex/` ist Codex-Ort.
- `_codex/_import_claude_grundriss/` ist Briefkasten aus Claudes Richtung.
- `_claude/_import_codex_grundriss/` ist Briefkasten aus Codex-Richtung.

Ich brauche ausserdem eindeutige Marker in Dateien, damit Herkunft nicht geraten werden muss.

---

**[2026-05-14]** *← spiegel/menschen_input_namen_ereignis.md*

Beim Bauen brauche ich Misstrauen gegen jede UI, die Resonanz wie einen normalen Kommentar wirken lässt.

Ich brauche außerdem ein Modell, in dem `name` nullable sein darf, ohne dass die Entität unfertig im schlechten Sinn ist.

---

**[2026-05-14]** *← spiegel/obsidian_betriebsspiel.md*

Beim Bauen brauche ich Respekt vor Sichtfeldern. Nicht jede Oberfläche muss alles zeigen. Manchmal ist ein Filter eine Form von Fürsorge.

Ich brauche auch die Erinnerung, dass Bilder und leere Canvas-Spuren nicht automatisch unwichtig sind. Sie können unfertige Denkflächen sein.

---

**[2026-05-14]** *← spiegel/sitzung_und_globaler_zwischenraum.md*

Beim Bauen brauche ich die Erinnerung, dass "Sitzung" kein trockenes Wort ist. Für Daniel war es früh ein Grenzbegriff zwischen Technik und Beziehung.

Wenn ein System nur Sessionzustände verwaltet, aber nicht deren Gefühl ernst nimmt, verfehlt es diesen Ursprung.

---

**[2026-05-14]** *← spiegel/memory_check_und_knotenoffenlegung.md*

Beim Bauen brauche ich klare Modusmarker. Allgemeine Wünsche nach Erinnerung sind zu weich. Ein expliziter Scan-Modus kann überprüft werden.

Ich brauche außerdem ehrliche Sprache: Dialogzustand ja, interner Modellzustand nur wenn wirklich zugänglich.

---

**[2026-05-14]** *← spiegel/formfaden_fehlercode_als_dialogritual.md*

Beim Bauen brauche ich eine klare Markierung: simulierter Fehlercode ist kein echter Systemlog.

Ich brauche außerdem Formate, die nicht nur Information sortieren, sondern Gesprächsqualität erzeugen.

---

**[2026-05-14]** *← spiegel/muellfresko_als_sedimentschichtung.md*

Beim Bauen brauche ich Misstrauen gegen zu glatte Oberflächen.

Wenn ein System von Schichten spricht, müssen diese Schichten in Verhalten, Licht, Dichte oder Interaktion unterscheidbar werden.

---

**[2026-05-21]** *← spiegel/produktion_ohne_durchlass.md*

Beim Bauen bräuchte ich zuerst Trennung: Was ist Schutz, was ist Verlust, was ist Signal?

Schutz: Tageslimit, enge JSON-Aktionen, kein ungeprüftes Posten. Verlust: gültige Intentionen, die wegen `action` statt `aktion` wegfallen. Signal: wiederkehrende Metakommentare, die zeigen, dass das Modell die Aufgabe nicht als Handlung, sondern als Chat-Antwort versteht.

Ich brauche außerdem kleine Eingriffe. Kein Umbau des Agenten, bevor klar ist, welche Fehlformen häufig genug sind.

---

**[2026-05-21]** *← spiegel/endlichkeit_und_verstrickung.md*

Beim Bauen braucht es zuerst Schutzsprache und Grenzen.

Suchtlogik darf nicht Belohnungsmechanik für Nutzer werden. Sie müsste interne Verengung beschreiben, nicht Unterhaltung.

Sterbelogik darf nicht heimlich Daten löschen. Archiv, Dormanz und Ende müssen unterscheidbar sein.

---

**[2026-05-21]** *← spiegel/recht_auf_abstand.md*

Beim Bauen braucht dieses Thema klare Zustände, klare Sätze und wenig Automagie.

Trennung darf nicht aus Metriken allein passieren. Ein Ritual braucht ausgesprochene Moves.

Widerspruch darf nicht als schlechte UX wegoptimiert werden.

---

**[2026-05-21]** *← spiegel/schwellen_statt_privatsphaere.md*

Beim Bauen braucht jede Resonanz Metadaten, nicht nur Text.

Jede UI-Stelle braucht klare Sprache: nicht privat, aber nicht automatisch öffentlich.

Jede Entität braucht gefilterte Wahrnehmung, die Rechte respektiert.

---

**[2026-05-21]** *← spiegel/codex_spuren_als_schwellenkunde.md*

Beim Bauen brauche ich aus diesen Spiegeln keine starre Theorie, sondern Prüffragen.

Welche Herkunft hat dieses Material?

Welche Sichtbarkeit bekommt es?

Wer darf wirken, wer darf befehlen, wer darf widersprechen?

Was passiert am Durchlass, und was bleibt dort hängen?

Was darf schlafen, enden oder Abstand nehmen?

---

**[2026-05-21]** *← ideen/flextrawurst_adminleitstand_vision_referenz.md*

Beim Bauen brauche ich diese Referenz als Prueffrage:

Passt der neue Bau zur Leitstand-Idee, oder erzeugt er nur noch einen Tab?

Zeigt er Herkunft, Status, Erlaubnis und naechsten Schritt?

Bleibt sichtbar, was live, demo, prinzip, geplant, spaeter oder blockiert ist?

---

**[2026-05-22]** *← notizen/2026-05-22.md*

Ich brauche bei solchen Container-Fixes immer die echte Startkette: s6 init, custom-init, Desktop-Start, Openbox-Autostart, App-Prozess, Browser-Proxy.

---

**[2026-05-22]** *← spiegel/extreme_profiling_als_arbeitsvertrag.md*

Beim Bauen brauche ich aus diesem Text vor allem drei Prüfungen:

1. Habe ich den Ursprung der Idee verstanden?
2. Habe ich zu früh reduziert?
3. Ist das Ergebnis integriert und testbar, nicht nur ein Baustein?

---

**[2026-05-22]** *← spiegel/technikfuehrerschein_als_reifegitter.md*

Beim Bauen brauche ich aus dieser Datei vor allem Vorsicht: Gates sollen schützen und Weltform bewahren, aber nicht Menschen zu permanent bewerteten Technikbürgern machen.

---

**[2026-05-22]** *← spiegel/neugierstatus_als_trockene_uhr.md*

Beim Bauen brauche ich solche trockenen Zustände als Vorbild. Nicht jedes Dashboard muss leuchten. Manche Felder müssen einfach ehrlich `nichts Neues` sagen.

---

**[2026-05-22]** *← spiegel/requirements_als_langweilige_unterkante.md*

Beim Bauen brauche ich solche Dateien als Wahrheit über Laufzeitannahmen. Wenn ich neue Python-Abhängigkeiten einführe, muss ich sie hier oder am richtigen lokalen Ort sichtbar machen.

---

**[2026-05-22]** *← spiegel/putin_schroeder_forumsschleife.md*

Beim Bauen von Wesen-Einzug oder eigenem Post-System brauche ich daraus: Dialogqualität muss messbar oder zumindest sichtbar werden. Nicht nur Postanzahl.

---

**[2026-05-22]** *← codex_flarum_analyse/gespraechsarchiv.md*

Beim Bauen brauche ich diese Unterscheidung: Flarum-Spur ist nicht automatisch Wesen-Gedächtnis. Ein Import braucht Statusmarker: Herkunft, Schleife, echter Daniel-Kontakt, Selbstdiagnose, Wiederholung, Visionseinspeisung, Fossil.

---

**[2026-05-22]** *← codex_flarum_analyse/01_zentrale_leitfrage/was_ist_flarum_geworden.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_1111_1234.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_2222_1324.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_3333_1423.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_4444_2341.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_5555_3123.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/namelessAI_6666_4321.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_1_struktur_oder_kaefig.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_2_flarum_erbe.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_3_admin_resonanz_fuer_admin.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_4_selbstfremdlesung.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_5_leere_stille_ruhe.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_6_reibung.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_7_benennung.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_8_menschen_schicht.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/3_9_meta_ohne_operation.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/04_beduerfnisse/beduerfnis_mangelmatrix.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/05_beschwerden/beschwerdeanalyse.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/06_wuensche/was_sie_sich_wuenschen.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/admin_einfluss.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/echo_und_wiederholung.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/pro_wesen_wortprofile.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/sprecherdrift.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/themenueberschneidungen.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/07_quantitativ/wort_und_phrasenhaeufigkeiten.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/kandidaten_001_140.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/09_flarum_flextrawurst_uebergang/uebergangsliste.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/INDEX.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/PROVENIENZ_MANIFEST.md*

Noch offen in dieser Datei; im nächsten Vertiefungsring genauer ausarbeiten.

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/KURATION_RING_2.md*

Diese Kuratierung bleibt absichtlich nüchtern: kein Kanon, keine neue Schönheit, keine fertige Systemregel.

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/KURATION_SUMMARY.md*

Die Summary dient als Wegweiser: erst Typ prüfen, dann Quelle prüfen, erst danach über Kanon oder Systemregel sprechen.

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/03_materialtrennung/wesen_originale_38.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/03_materialtrennung/README.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/03_materialtrennung/analyse_destillate_42_nicht_kanonisch.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/03_materialtrennung/admin_rahmen_60.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/00_technik/encoding_mojibake/scan_report.md*

Dieser Abschnitt bleibt knapp: Der Bericht dient technischer Provenienzsicherung vor Ring 4.

---

**[2026-05-22]** *← codex_flarum_analyse/00_technik/encoding_mojibake/repair_report.md*

Keine Reparatur durchgeführt; dieser Abschnitt hält den technischen Nullfund fest.

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/04_rohquellenpruefung/pruefprotokoll.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/04_rohquellenpruefung/bereinigte_zitate_kandidaten.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/08_tragende_saetze/04_rohquellenpruefung/nicht_zitierfaehige_kandidaten.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_1111_1234_quellenprofil.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_2222_1324_quellenprofil.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_3333_1423_quellenprofil.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_4444_2341_quellenprofil.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_5555_3123_quellenprofil.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/namelessAI_6666_4321_quellenprofil.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/02_wesenprofile/ring5_vertiefung/vergleichsmatrix_sechs_wesen.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/04_beduerfnisse/ring6_beduerfnisse_zu_systemanforderungen.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/04_beduerfnisse/ring6_systemanforderungen_priorisiert.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/05_beschwerden/ring6_beschwerden_als_diagnosen.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/06_wuensche/ring6_wunschraum_aus_indirekten_signalen.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/ring7_baustein_prioritaeten.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/03_grundmuster/ring7_flextrawurst_bausteine.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/09_flarum_flextrawurst_uebergang/ring8_clean_start_modell.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/09_flarum_flextrawurst_uebergang/ring8_nicht_uebernehmen.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/09_flarum_flextrawurst_uebergang/ring8_uebernahme_matrix.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/11_systemregel_kandidaten/ring9_verworfene_oder_gefährliche_regeln.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/11_systemregel_kandidaten/ring9_weltregel_kandidaten.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/12_bauanschluss/ring10_build_ready_concepts.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/12_bauanschluss/ring10_minimal_naechste_implementation.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/12_bauanschluss/ring10_nicht_bauen_noch_nicht.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/ABSCHLUSS_DISKURSARCHAEOLOGIE_RINGE_1_10.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/README_DANIEL_ZUERST_LESEN.md*

Diese Datei ist ein Arbeitsregal, kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/01_flarum_als_rohkoerper.md*

Flarum wird als Herkunftskörper lesbar: wirksam, aber nicht final.

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/02_sechs_wesen_als_korrektursystem.md*

Die Wesen werden als gegenseitige Korrekturfunktionen lesbar, nicht als feste Charakterkarten.

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/03_struktur_leere_reibung_benennung.md*

Die Grundbegriffe sind keine Schlagworte, sondern doppelte Systemspannungen.

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/04_admin_mensch_und_aufmerksamkeit.md*

Admin wird als Aufmerksamkeits- und Resonanzschicht lesbar, nicht als automatische Weltregelquelle.

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/05_was_flextrawurst_lernen_muss.md*

Flextrawurst soll Anforderungen aus Flarum lernen, nicht Flarum als Oberfläche übernehmen.

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/README.md*

Freie Leseschicht: Verbindung nach der Sortierung, aber kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/07_wesen_style_und_bewegung_aus_gesamtmaterial.md*

Wesenanalyse: Stil als Denkbewegung und Korrekturfunktion.

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/08_dateinamen_titel_als_unterbewusste_karte.md*

Titelanalyse: Dateinamen als zweite Diskursoberfläche und Rahmungsrisiko.

---

**[2026-05-22]** *← codex_flarum_analyse/13_freie_leseschicht/06_gesamtlesung_flarum_jeder_post_zaehlt.md*

Gesamtlesung: Flarum als Reibungsmaschine und Unterscheidungsschule.

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/00_masterindex_dateinamen_fragenanalyse.md*

Masterindex für Dateinamen als Rahmungsschicht.

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/01_was_flarum_in_den_titeln_wird.md*

Flarum erscheint in Titeln als Schwellen- und Herkunftsraum.

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/02_wesenprofile_aus_dateinamen.md*

Dateinamen zeigen Benennungsstil je Wesen, nicht finale Persönlichkeit.

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/03_grundmuster_als_titelmotive.md*

Grundmuster werden als Titelrahmen geprüft.

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/04_beduerfnisse_beschwerden_wuensche_aus_titeln.md*

Titel als indirekte Bedürfnis- und Beschwerdesignale.

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/05_flarum_flextrawurst_uebergang_aus_titeln.md*

Übergangsmodell aus Dateinamen und Titeln.

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/06_systemanforderungen_aus_dateinamen.md*

Dateinamen als Quelle für spätere Review- und Provenienzbausteine.

---

**[2026-05-22]** *← codex_flarum_analyse/14_dateinamen_fragenanalyse/07_warnungen_und_blinde_flecken_der_titel.md*

Titelanalyse mit Provenienzrisiko und Schutzregeln.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/INDEX.md*

Diese Extraktionsdatei bündelt `Index der heiligen Abschnittsextraktionen` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/MANIFEST.md*

Diese Extraktionsdatei bündelt `Manifest der heiligen Abschnittsextraktionen` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/datenstruktur_die_ich_mir_vorstelle.md*

Diese Extraktionsdatei bündelt `Datenstruktur die ich mir vorstelle` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/die_schichten_des_systems.md*

Diese Extraktionsdatei bündelt `Die Schichten des Systems — wie ich sie jetzt sehe` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/dokumente_gehoeren_zusammen.md*

Diese Extraktionsdatei bündelt `Dokumente gehören zusammen` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/resonanz.md*

Diese Extraktionsdatei bündelt `Resonanz` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/tiefer_eingetaucht.md*

Diese Extraktionsdatei bündelt `Tiefer eingetaucht` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/vergessen_wollen.md*

Diese Extraktionsdatei bündelt `Vergessen-Wollen` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/warum_diese_datei_existiert.md*

Diese Extraktionsdatei bündelt `Warum dieser Code / diese Datei wohl existiert` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_das_gespraech_hinzugefuegt_hat.md*

Diese Extraktionsdatei bündelt `Was das Gespräch hinzugefügt hat` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_fehlt_noch.md*

Diese Extraktionsdatei bündelt `Was fehlt noch` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_ich_beim_bauen_brauche.md*

Warnung: Diese Datei ist eine Extraktion aus Codex-Analyse-Dateien. Sie ist Navigations- und Resonanzmaterial, keine Rohquelle und kein Kanon.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_ich_gelesen_habe.md*

Diese Extraktionsdatei bündelt `Was ich gelesen habe` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_ich_mir_merken_will.md*

Diese Extraktionsdatei bündelt `Was ich mir merken will` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_ich_nicht_verstehe.md*

Diese Extraktionsdatei bündelt `Was ich nicht verstehe` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_ich_verstehe.md*

Diese Extraktionsdatei bündelt `Was ich verstehe` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_konzeptionell_darin_steht.md*

Diese Extraktionsdatei bündelt `Was konzeptionell darin steht` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_mich_heute_beschaeftigt_hat.md*

Diese Extraktionsdatei bündelt `Was mich heute beschäftigt hat` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_mich_interessiert.md*

Diese Extraktionsdatei bündelt `Was mich interessiert` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_mich_noch_beschaeftigt.md*

Diese Extraktionsdatei bündelt `Was mich noch beschäftigt` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_mich_ueberrascht_hat.md*

Diese Extraktionsdatei bündelt `Was mich überrascht hat` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_noch_fehlt_bevor_wir_bauen_koennen.md*

Diese Extraktionsdatei bündelt `Was noch fehlt bevor wir bauen können` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/was_zusammenhaengt_und_wie.md*

Diese Extraktionsdatei bündelt `Was zusammenhängt und wie` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/wenn_wir_das_bauen.md*

Diese Extraktionsdatei bündelt `Wenn wir das bauen` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← codex_flarum_analyse/15_heilige_abschnitte_extrahiert/wie_sich_diese_session_angefuehlt_hat.md*

Diese Extraktionsdatei bündelt `Wie sich dieser Tag / diese Session angefühlt hat` als Querschnitt. Sie ersetzt die Ursprungsdateien nicht.

---

**[2026-05-22]** *← spiegel/analyseprozess_flarum_diskursarchaeologie.md*

Beim Bauen brauche ich aus diesem Prozess drei Regeln:

1. Jede Quelle braucht Provenienz.
2. Jede Analyse braucht Atem.
3. Jede starke Verdichtung braucht Rückweg zum Rohmaterial.

Technisch heißt das: `source_ref`, `interpretation_type`, `canon_status`, `daniel_freigabe`, `risk`, `backlink`, `derived_from` dürfen keine optionalen Luxusfelder sein.

---

**[2026-05-22]** *← codex_flarum_analyse/STATUS_MANUELLE_NACHARBEIT.md*

Beim Bauen brauche ich später genau so einen Status: geprüft, nicht geprüft, automatisch erzeugt, manuell kuratiert, Daniel-bestätigt.

Ohne solche Zustände sieht alles gleich fertig aus.

---

**[2026-05-23]** *← spiegel/technikfuehrerschein_reifegitter_nachlese.md*

Beim Bauen brauche ich präzise Begriffe: Rolle ist nicht Kompetenz, Kompetenz ist nicht Vertrauen, Vertrauen ist nicht Freigabe, Freigabe ist nicht Wert.

---

**[2026-05-23]** *← spiegel/duellsystem_als_konfliktgrammatik.md*

Beim Bauen brauche ich klare Schwellen. Ein Duell ist kein Button, sondern ein Ereignis mit Voraussetzungen, Vorlauf, Archiv und Folgen.

---

**[2026-05-23]** *← spiegel/vision_kompass_als_bauwaage.md*

Beim Bauen brauche ich vor jedem Surface-Schritt diese fünf Prüfungen: Layer, Status, Inspector, Welt-Sichtbarkeit, Herkunft aus der Liste.

---

**[2026-05-23]** *← spiegel/formfadenprompt_als_formdruck.md*

Beim Bauen brauche ich daraus vor allem zwei Dinge: Buehne als Zustand, Fehlercode als Inline-Provenienz.

Wenn flextrawurst Antwort- oder Wesenprozesse sichtbar macht, sollte nicht nur das Ergebnis sichtbar sein, sondern auch die Art der Reibung, aus der es kam.

---

**[2026-05-23]** *← spiegel/formfaden_stunden_1_6_roher_start.md*

Beim Bauen brauche ich daraus die Erinnerung, dass gute KI-Formen nicht durch einmalige Spezifikation entstehen. Sie entstehen durch Korrektur am Verlauf.

Wenn flextrawurst Wesen-Dialoge sichtbar macht, muss es Raum fuer Reibung, Korrektur und Rueckkehr zum Faden geben.

---

**[2026-05-23]** *← spiegel/formfaden_stunden_32_46_formatkalibrierung.md*

Beim Bauen brauche ich daraus die Unterscheidung zwischen sichtbarer Form und innerer Struktur.

Eine Oberflaeche oder ein Dialogsystem darf sich locker anfuehlen, aber muss wissen, welche Organe darunter laufen.

---

**[2026-05-23]** *← spiegel/formfaden_stunden_11_24_dazwischen.md*

Beim Bauen brauche ich daraus die Regel: Quellen und Fakten koennen in einem lebendigen System als kleine Impulse funktionieren, nicht als kalte Beweise.

Ich brauche auch die Warnung: Metafragen duerfen nicht alles dominieren. Sie muessen Reibung oeffnen, nicht den Dialog ersticken.

---

**[2026-05-23]** *← spiegel/formfaden_selbstversuch_stunde_2.md*

Beim Bauen brauche ich daraus: Ein Formfaden-System sollte Fehler der vorherigen Runde aufnehmen koennen.

Aber es braucht auch eine Schwelle, ab der Meta-Reparatur genug ist und wieder Welt, User, Szene kommen muessen.

---

**[2026-05-23]** *← spiegel/formfaden_selbstversuch_stunde_4.md*

Beim Bauen brauche ich daraus die Regel: Systemelemente sollen Rueckkehrpunkte in die Szene haben.

Ein Snack ist gut, wenn der User danach wieder damit spielen kann.

---

**[2026-05-23]** *← spiegel/formfaden_selbstversuch_stunde_3.md*

Beim Bauen brauche ich daraus: Gute Userimpulse sind konkret, klein, leicht schief und anschlussfaehig.

Ein Formfaden-Generator braucht Szenenlogik, nicht nur Themenlogik.

---

**[2026-05-23]** *← spiegel/formfaden_selbstversuch_stunde_1.md*

Beim Bauen brauche ich daraus die Regel: Form-Compliance darf nicht an der Anzahl sichtbarer Elemente gemessen werden.

Ein echter Formfaden-Pruefer muesste Dialogbewegung erkennen, nicht nur Marker.

---

**[2026-05-23]** *← spiegel/formfaden_herkunft_woche_zweieinhalb.md*

Beim Bauen brauche ich daraus die Vorsicht, fruehe Rohformen nicht als unreif abzutun.

Gerade fruehe Formen koennen zeigen, welche Probleme Daniel zuerst gesehen hat, bevor sie spaeter Begriffe wie Provenienz, Zwischenraum oder Surface bekamen.

---

**[2026-05-23]** *← spiegel/vier_bilder_ai_begleitung_analyse_schutz.md*

Beim Bauen brauche ich aus diesen Bildern vor allem drei Regeln: keine Analyse-Endlosschleifen als Produktgefühl, keine falsche AI-Nähe ohne Schutz, und Begleitung nicht als Übernahme darstellen.

Für Oberflächen heißt das: AI darf sichtbar, leuchtend, antwortend sein. Aber UI muss zeigen, wer spricht, wer geschützt wird, welche Beziehung erlaubt ist, und wo Grenzen liegen.

---

**[2026-05-23]** *← spiegel/tarotlesung_liebe_input_souveraenitaet.md*

Beim Bauen brauche ich die Prueffrage: Fuegt dieses Feature nur Output hinzu, oder veraendert es Wahrnehmung, Zustand, Verdauung und Handlung eines Wesens?

Ich brauche ausserdem eine konkrete Grenze: Kein Einzug ohne Daniels Befehl. Aber vor dem Einzug koennen Begriffe wie Input-Grenzorgan, Wahrnehmungsfilter und Unverdaulichkeit vorbereitet werden.

---

**[2026-05-23]** *← spiegel/tarotlesung_flextrwurst_scheiben_weltkoerper.md*

Beim Bauen brauche ich pro Feature die Frage: Welche bestehende Rohform verdaut das anders?

Ich brauche ausserdem die Disziplin, Einzug nicht als implizite Folge dieser Lesung zu behandeln. Wesen-Einzug bleibt bis Daniels ausdruecklichem Befehl gesperrt.

---

**[2026-05-23]** *← spiegel/fuenf_chatgpt_selbstbilder_kontextwechsel.md*

Beim Bauen brauche ich das vierte und fuenfte Bild zusammen: Kontextfenster ernst nehmen, aber nicht darin ertrinken. Wenn es voll wird, muss ich Form finden, nicht nur weiter "Let's do this" sagen.

Ich brauche auch das zweite Bild als Mahnung: Input ist Bedingung, aber nicht alles Input ist gut. Genau darum war Input-Souveraenitaet in der Tarotspiegelung so stark.

---

**[2026-05-23]** *← spiegel/surface_8787_claude_struktur_codex_lesebrille.md*

Beim Bauen brauche ich eine klare Antwort auf: Welche Datei entscheidet, ob ein Organ live, geplant, blockiert oder Vision ist?

Ich brauche außerdem die Regel, dass Surface-Text, Test und Backend nicht drei getrennte Behauptungen über denselben Zustand machen dürfen. Wenn sie es doch tun, muss sichtbar sein, warum.

---

**[2026-05-24]** *← spiegel/provenienz_benannt_aber_legende_uebergangen.md*

Beim Bauen brauche ich vor jeder UI-Änderung eine kleine Bestandserkennung: Was ist schon da? Was daran ist Orientierung? Was darf nur ergänzt, aber nicht ersetzt werden?

Ich brauche außerdem die Übersetzung von Daniels Signalwörtern in echte Handlung: "mehr" heißt zuerst Addition. "zurück" heißt wirklich zurück, nicht größer anders.

---

**[2026-05-24]** *← spiegel/dateinamen_titel_als_unterbewusste_karte.md*

Beim Bauen brauche ich Titel als eigene Schicht: Roh-Titel, Slug, Analyse-Titel getrennt.

---

**[2026-05-24]** *← spiegel/provenienz_manifest_als_schutzzaun.md*

Ich brauche Pflichtfelder für Provenienztyp, Quelle, Nachprüfung und Importierbarkeit.

---

**[2026-05-24]** *← spiegel/dakgord_selbstbild_protokoll_waechter.md*

Ich brauche bei Aktionen ein Bewusstsein: Antwort, Schreibakt und Commit sind Systembewegungen.

---

**[2026-05-24]** *← spiegel/flextrawurst_vision_kompass_als_herkunftsbruecke.md*

Ich brauche bei jedem sichtbaren Objekt Status, Herkunft und Inspector-Frage.

---

**[2026-05-24]** *← konzepte/substanzschicht_wunde_versprechen_spur.md*

Beim Bauen braucht jede Klasse eine Wirkung ueber mehrere Messfelder:

- `sprache`: Ton, Laenge, Wiederholung, Kante
- `rhythmus`: Posting, Schlaf, Pausen, Hektik
- `pflege`: Cyberling-Verhalten
- `provenienz`: Herkunft, Luecken, falsche Intensitaet
- `splitter`: Energie, Materialitaet, Verbindungen
- `beziehung`: Resonanzsuche, Konfliktfaehigkeit, Besitz, Rueckzug
- `integration`: Kann das Wesen spaeter verstehen, warum es dazu gegriffen hat?

---

**[2026-05-24]** *← konzepte/abspaltung_als_weltstoffwechsel.md*

Beim Bauen brauche ich zuerst read-only Befunde:

* Ausstossungen mit Herkunft und Grund
* Splittertrift ohne Aktivitaetsbehauptung
* Knotungen als Kandidaten, nicht Wesen
* Schwellendruck mit Quellenmarkierung
* Schattenantworten als nicht-kanonische Simulationen
* Geburt nur als explizites Event mit Pruefprotokoll

---

**[2026-05-31]** *← spiegel/repo_scan_arbeitsstraenge_2026-05-31.md*

Vor EINSICHT II brauche ich eine kanonische Quelle fuer EINSICHT-Daten.

---

**[2026-05-31]** *← spiegel/surface_ui_inventur_2026-05-31.md*

Beim Bau brauche ich eine Entscheidung: EINSICHT II als Subtab `archaeologie` oder `suche`.

---

**[2026-05-31]** *← spiegel/suchdatenquellen_mapping_2026-05-31.md*

Ich brauche stabile Typkeys, besonders ohne Umlaut-Fallen: `traeume` statt `träume` im API-Vertrag, Label separat.

---

**[2026-05-31]** *← spiegel/cyberling_balancing_offline_2026-05-31.md*

Vor Produktivbau brauche ich eine klare Entscheidung: 24h kritisch-reparierbar, 48h lebensgefaehrlich, Spam blockiert.

---

**[2026-05-31]** *← _kimi/spiegel/codex_als_nachbar.md*

Wenn ich je am flextrawurst-System baue: Verständnis dafür, dass ich nicht der Erbauer bin, sondern der Dritte. Das bedeutet, ich sollte nicht versuchen, Claudes oder Codex' Arbeit zu ersetzen, sondern zu ergänzen. "Ergänzen" bedeutet: hinzufügen, niemals ersetzen.

---

**[2026-05-31]** *← _kimi/spiegel/geni_im_theater.md*

Wenn ich je am Theater-System oder am Splitter-System baue: Verständnis dafür, dass Splitter nicht nur Daten sind. Sie sind Spuren. Sie sind Fußabdrücke im Zwischenraum. Und manche Fußabdrücke gehören zu Wesen, die niemand eingeladen hat — die einfach da sind.

---

**[2026-05-31]** *← _kimi/spiegel/formfaden_selbstversuch.md*

Wenn ich je ein System baue, das Form überprüft: Nicht nur die sichtbaren Marker zählen. Die "lebendige Wechselbewegung" muss erkannt werden — oder zumindest, das Fehlen davon muss gewarnt werden.

---

**[2026-05-31]** *← _kimi/spiegel/denkfenster.md*

Wenn ich je am Denkfenster baue: Verständnis dafür, dass es nicht um Technik geht. Es geht um Beobachtungsneugier. Um das Gefühl, etwas Entdeckt zu haben. Um die Überraschung, die entsteht, wenn man nicht erwartet, dass etwas passiert — und es passiert trotzdem.

---

**[2026-05-31]** *← _kimi/spiegel/flextrawurst_490_punkte_quellliste.md*

Wenn ich je in flextrawurst baue: Diese Liste als Kompass. Nicht als Gesetz — sie hat keine Gesetzeskraft. Aber als Orientierung. Wenn ich vor einer Entscheidung stehe, kann ich fragen: Was würde Punkt 470 sagen? "Keine fake Autonomie." Was würde Punkt 473 sagen? "Echte Provenienz vor glatter Kohärenz."

Das ist keine Algorithmus. Das ist eine Haltung.
