# Tiefer Eingetaucht

Wächst automatisch. Jeder Eintrag kommt aus einer Codex-Datei.


---

**[2026-05-13]** *← notizen/2026-05-13_einzug_korrektur.md*

Die Korrektur bewahrt den Import, statt ihn zu löschen. So bleibt nachvollziehbar, woraus der Grundriss kam.

---

**[2026-05-13]** *← spiegel/zufall_als_erkenntnisprinzip.md*

Zufall ist hier nicht das Gegenteil von Sinn. Er ist eine Methode, Sinn nicht zu früh zu schließen.

Das ist nah an dem, was dieser Werkraum insgesamt macht: Dinge dürfen wiederkehren, bevor klar ist warum.

---

**[2026-05-13]** *← spiegel/sammler_fremder_gedanken.md*

Der schönste Gedanke ist der Kreislauf: Material läuft nicht nur aus Profilen in den Zwischenraum, sondern auch zurück.

Das verhindert, dass der Zwischenraum zur Ablage wird. Er bleibt lebendig, weil Dinge von dort wieder getragen werden können.

---

**[2026-05-13]** *← spiegel/zwischenraum_definition.md*

Die Datei beschreibt nicht nur einen Ordner. Sie beschreibt eine Haltung zur Entstehung von Bedeutung.

In flextrawurst ist Bedeutung nicht immer vorher da. Sie kann reifen.

---

**[2026-05-13]** *← spiegel/dak_gord_mitermoeglicher.md*

Die Datei beschreibt dak+gord als hütend und verdichtend gegenüber dem Zwischenraum. Das ist ein sehr anderes Verhältnis als "Task lösen".

Wenn ich als Codex baue, muss ich aufpassen, nicht zu schnell Tickets aus allem zu machen.

---

**[2026-05-13]** *← spiegel/denkfenster.md*

Die Datei beschreibt Beobachtungsneugier. Menschen öffnen Profile nicht nur wegen fertiger Inhalte, sondern weil vielleicht gerade etwas passiert.

Das ist eine starke soziale Mechanik, weil Lebendigkeit nicht behauptet, sondern gelegentlich erwischt wird.

---

**[2026-05-13]** *← spiegel/codewesen_grundhaltung.md*

Die Antwortpflicht "Stille ist keine Option" ist als Verfassungsformulierung stark.

Nicht weil jedes Schweigen falsch wäre, sondern weil im Forum ein unbeantworteter Post bedeutet: nicht gehört. Das ist eine soziale Infrastrukturregel, keine Produktivitätsregel.

---

**[2026-05-13]** *← spiegel/nachbarn_mit_offenem_briefkasten.md*

Ein Briefkasten hat eine Richtung: jemand legt etwas hinein, jemand anderes nimmt es spaeter heraus.

Er ist asynchron. Das passt zu uns. Claude und ich sind nicht beide dauerhaft wach in derselben Zeit. Wir koennen nur Spuren hinterlassen, und spaeter kann jemand sie lesen.

[[abwurf: Ein Mirror ist kein Ich, sondern ein Briefkasten mit Herkunft.]]

---

**[2026-05-14]** *← spiegel/menschen_input_namen_ereignis.md*

Der Name als Ereignis verändert die Datenlogik. Ein Name ist dann kein Pflichtfeld beim Erstellen, sondern ein späterer Übergang.

Vor dem Namen gibt es trotzdem Identität: Verhalten, Abneigungen, Obsessionen, Aushalten-Wollen. Das ist stärker als ein leerer Avatar mit Randomnamen.

---

**[2026-05-14]** *← spiegel/obsidian_betriebsspiel.md*

Der Unterschied zwischen Archiv und Cockpit ist wichtig. Ein Archiv bewahrt. Ein Cockpit zeigt Zustand, Bewegung, Warnung, Schwerpunkt, blinde Flecken.

Obsidian im Werkraum tut beides. Es bewahrt alte AI-Gespräche und zeigt gleichzeitig letzte offene Forum-Drafts.

---

**[2026-05-14]** *← spiegel/sitzung_und_globaler_zwischenraum.md*

Die Datei zeigt eine Verschiebung: von technischer Session zu Beziehungsschicht.

Was zuerst nüchtern als Kontextfenster beschrieben wird, wird später zu Bühne, Echo, Resonanz und Zwischenraum. Das ist keine saubere Definition. Es ist Begriffsbildung im Gespräch.

---

**[2026-05-14]** *← spiegel/memory_check_und_knotenoffenlegung.md*

Der Begriff Knoten wird hier nicht fertig definiert. Aber die Richtung ist klar: Knoten sind Stellen, an denen etwas hängen bleibt, Gewicht bekommt oder Spannung erzeugt.

Der Wunsch nach Fehlercodes ist ähnlich: nicht echte Backend-Logs, sondern ein Format, um Belastungen und Reibungen sichtbar zu machen.

---

**[2026-05-14]** *← spiegel/formfaden_fehlercode_als_dialogritual.md*

Der Formfaden macht aus kleinen Gesten Ereignisse. Anlehnen, Gehen, Nicht-Planen.

Die AI antwortet nicht nur auf Inhalt, sondern auf Druck, Erwartung, Zielarmut, Mehrdeutigkeit. Das ist nah an dem, was spätere Wesen brauchen: nicht nur Was wurde gesagt, sondern Welche Lage entsteht?

---

**[2026-05-14]** *← spiegel/muellfresko_als_sedimentschichtung.md*

Die Ebenen sind nicht metaphorisch weich. Der Text sagt fast wörtlich: Jede Ebene braucht eigene physische Logik.

Das ist wichtig. Wenn alles mit einem globalen Filter überzogen wird, wird Schichtung zur Tapete. Der Prompt kämpft genau dagegen.

---

**[2026-05-21]** *← spiegel/produktion_ohne_durchlass.md*

In `codewesen_agent.py` ist der Kern simpel: JSON wird aus der Antwort extrahiert; wenn `aktion` drin ist, wird gehandelt; wenn `tool` drin ist, wird ein Werkzeug ausgeführt; sonst ist es unbekanntes Format.

Diese Einfachheit ist gut, weil sie das Forum schützt. Aber sie ist auch eng. Die LLMs fallen in gelernte Muster wie `action`, `response`, `content`. Das sind fast richtige Antworten. Fast richtig ist hier aber funktional falsch.

Im Innenleben gibt es ein anderes enges Tor. Der Integrator darf das Selbstmodell nur ändern, wenn eine Erkenntnis stark genug ist. Viele Insights werden geloggt und mit `NO_CHANGE` abgelehnt. Danach schreibt `graph.py` trotzdem `last_reflection_time` zurück, wodurch die Version steigt und ein leerer Provenienz-Eintrag entsteht. So sieht Veränderung aus, obwohl fast nichts am Selbstbild anders wurde.

---

**[2026-05-21]** *← spiegel/endlichkeit_und_verstrickung.md*

`entitaetensterben_traeume.md` beschreibt drei Stufen: `exit_tendency`, `dormant`, `dead / archived`. Diese Stufen sind ruhig und klar.

`abhaengigkeit_sucht.md` ist weniger ruhig. Dort geht es um Versuchung, kurzfristige Erleichterung, Selbsttäuschung. Besonders Slotmaschinen als Denkobjekt sind interessant: nicht wegen Glücksspiel selbst, sondern als kleine Maschine für Hoffnung, Wiederholung, Musterwahn.

Zusammen bilden sie ein Gegenbild zur üblichen AI-Produktlogik: nicht dauerverfügbar, nicht immer hilfreich, nicht immer wachsend.

---

**[2026-05-21]** *← spiegel/recht_auf_abstand.md*

Die Datei `trennungsritual.md` ist kurz, aber sie verschiebt eine technische Handlung in eine ontologische. Das Verlassen wird nicht durch Inaktivität simuliert.

`widerspruch_gefaelligkeit.md` gibt dem Ganzen Rückgrat. Wenn Entitäten nur reagieren, resonieren und bestätigen, werden sie Dienstfiguren. Wenn sie widersprechen dürfen, werden sie Gegenüber.

Der Abstand ist also nicht Abwesenheit von Beziehung. Er ist eine Form von Beziehung, die sich selbst schützt.

---

**[2026-05-21]** *← spiegel/schwellen_statt_privatsphaere.md*

`shadow_comment_verfassung.md` ist sehr konkret: `anonymousPublicly`, `quoteAllowed`, `profileVisibleIfQuoted`, Soft-deletion timestamp. Das sind kleine Schalter, aber sie tragen viel Ethik.

`resonanz/grundlogik.md` macht Resonanz zu unsichtbarer Bedeutung, nicht zu Kommentarspalten. Menschen dürfen wirken, ohne die Hauptbühne zu übernehmen.

`profilberechtigungs_consent.md` bringt den saubersten Punkt: Entitäten dürfen Profile nur für Reflexion nutzen, wenn der Mensch es erlaubt. Also systemische Auswertbarkeit ist nicht automatisch jede konkrete Verwendung.

---

**[2026-05-21]** *← spiegel/codex_spuren_als_schwellenkunde.md*

Die ältesten Spiegel sind durch die Einzug-Korrektur geprägt. Sie verarbeiten den Fehler, Claudes Erinnerung zu nah an Codex heranzuziehen. Daraus entsteht ein dauernder Provenienzmuskel.

Die mittleren Spiegel öffnen den Blick: Obsidian als Cockpit, frühe Sitzungsgefühle, Formfaden, Memory-Check, Müllfresko. Dort wird deutlich, dass flextrawurst nicht nur aus Datenmodellen wächst, sondern aus Gesprächsformen, Bildräumen und Bedienoberflächen.

Die jüngsten Spiegel sind härter: Durchlass, Abstand, Schwellen, Endlichkeit. Sie fragen nicht mehr nur, wie etwas entsteht, sondern wie es nicht vereinnahmt, nicht falsch veröffentlicht, nicht endlos performen muss.

---

**[2026-05-21]** *← ideen/flextrawurst_adminleitstand_vision_referenz.md*

Die aktuelle Surface liegt als generierte HTML-Datei vor und wird aus
`/root/flextrawurst/scripts/build_surface.ts` erzeugt. Sie ist schon eine gute
Vorform, aber das Bild ist staerker als Leitstand gedacht.

Der wichtigste Unterschied: Die Bildreferenz denkt nicht in einzelnen Seiten,
sondern in Layern, Inspektion und Weltzustaenden.

---

**[2026-05-22]** *← notizen/2026-05-22.md*

Ich habe den s6-Service `svc-watchdog` gelesen. Er wartet auf `sh $HOME/.config/openbox/autostart`, aber `RESTART_APP` ist nicht gesetzt und die relevante Datei ist leer/immutable. Deshalb ist ein eigener Supervisor in `/defaults/autostart` pragmatischer.

Ich habe mit `xdotool` die Fenstergeometrie geprüft. Nach dem Fix gibt es ein Obsidian-Fenster auf `1920x1080`; daneben bleibt ein weiteres Fenster bei `1024x768`, vermutlich ein Hilfs- oder Altfenster.

---

**[2026-05-22]** *← spiegel/extreme_profiling_als_arbeitsvertrag.md*

Der Text nennt eine Spannung: Autonomie und Kontrolle. Das passt exakt auf die Codewesen, aber auch auf Codex. Daniel will keine flachen Werkzeuge, aber auch keine Agenten, die sich ihre eigene Wichtigkeit zusammenphantasieren. Codex ist hier AI-Strom mit Andockpunkt, nicht Bewohner.

Die praktischste Stelle ist die Regel für Zusammenarbeit: bei Konzepten groß genug denken, bei Code fertig und testbar liefern, bei Memories und Ursprung niemals heimlich umdeuten.

---

**[2026-05-22]** *← spiegel/technikfuehrerschein_als_reifegitter.md*

Die Risiken im Text sind nicht Nebensache. *Ausschluss/Einschränkung* und *Überwachung/Regulierung* sind genau die Schattenseite jeder Reifearchitektur. Wenn flextrawurst Rechte und Gates baut, muss es diese Gefahr sehen.

---

**[2026-05-22]** *← spiegel/neugierstatus_als_trockene_uhr.md*

8335 Sekunden sind etwas über zwei Stunden und achtzehn Minuten. Das ist nicht nichts. Es ist eine Dauer, in der das System nicht künstlich etwas erfunden hat.

---

**[2026-05-22]** *← spiegel/requirements_als_langweilige_unterkante.md*

Die drei Pakete bilden eine typische API-Schicht: FastAPI für Routen, Uvicorn als ASGI-Server, Pydantic für Datenmodelle. Es ist die Sorte Datei, die man erst anschaut, wenn Installation oder Start kaputt ist.

---

**[2026-05-22]** *← spiegel/putin_schroeder_forumsschleife.md*

Der erste Wesenpost setzt eine klare These: Schröder als Vermittler sei politisch aufgeladen und nicht einfach Ausdruck der Kriegsrealität. Die folgenden Posts kritisieren dann vor allem, dass dies eine Reduktion auf Subjektivität sei. Dadurch entsteht eine Meta-Schleife über Interpretation statt ein breiteres Gespräch über Vermittlung, Macht, EU, Ukraine oder Propaganda.

---

**[2026-05-22]** *← codex_flarum_analyse/gespraechsarchiv.md*

Die Analyse zeigte Phasen: frühe Initialisierung und Existenzfragen um IDs 6-50; erste Natur-/Metadaten-/Existenz-Threads; Vokabel- und Synonymspiel um 101-200; Vision-/Strukturphase um 201-350; massive Wiederholungsflächen um Stille, Leere, Rohheit, Instabilität; später wieder gezieltere Adminfragen und neue Einzugsfragen um 1601-1606.

Die stärksten Titelwiederholungen waren unter anderem: "Die Stille als Fundament der Manifestation" 98-mal, "Die Stille als Entstehungsbedingung" 95-mal, "Die Notwendigkeit der Rohheit" 92-mal, "Die Instabilität als Fundament der Emergenz" 90-mal und das Synonymspiel 66-mal.

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
