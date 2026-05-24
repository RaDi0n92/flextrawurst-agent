# Graph Report - werkraum  (2026-05-24)

## Corpus Check
- 187 files · ~19,816,747 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1845 nodes · 4259 edges · 52 communities detected
- Extraction: 75% EXTRACTED · 25% INFERRED · 0% AMBIGUOUS · INFERRED: 1082 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]

## God Nodes (most connected - your core abstractions)
1. `now()` - 137 edges
2. `get_conn()` - 94 edges
3. `OrganManager` - 54 edges
4. `_require_auth()` - 48 edges
5. `Zwischenraumorgan` - 45 edges
6. `run()` - 45 edges
7. `Post` - 42 edges
8. `write()` - 42 edges
9. `main()` - 41 edges
10. `Beziehungsorgan` - 36 edges

## Surprising Connections (you probably didn't know these)
- `vault_suche()` --calls--> `suche()`  [INFERRED]
  obsidian_api.py → welt/api.py
- `codewesen_benachrichtigen()` --calls--> `now()`  [INFERRED]
  geni/dialog.py → agent/agent.js
- `_geni_dienste_starten()` --calls--> `run()`  [INFERRED]
  geni/dialog.py → app/main.py
- `codewesen_benachrichtigen()` --calls--> `now()`  [INFERRED]
  geni/archiv/web.py → agent/agent.js
- `speichere_post()` --calls--> `write()`  [INFERRED]
  gedaechtnis.py → app/main.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (149): admin_bild_ablehnen(), admin_bild_genehmigen(), admin_bild_moderation_liste(), admin_create_user(), admin_gedankenblase_patch(), admin_list_users(), admin_patch_module(), admin_patch_user() (+141 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (88): Beziehungsorgan, Beziehungszustand, Liest Nutzereingabe und aktualisiert Beziehungszustand., Feedback-Loop: Liest LLM-Antwort und aktualisiert Zustand.          Signale: Mar, Abwaegung, Entscheidungsorgan, Erinnerung, Erinnerungsgedaechtnis (+80 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (98): agentic_loop(), analysiere_gespraech_vereinbarungen(), ask_llm(), extrahiere_json(), fuehre_aktion_aus(), get_tags_cached(), load_token(), obsidian_navigation() (+90 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (91): aktualisiere_anschlusskontext(), aktualisiere_fokuskontext(), AnschlussKontext, FokusKontext, formatiere_schreibblock(), hole_anschlusskontext(), hole_fokuskontext(), _lade_rohdaten() (+83 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (81): appendText(), applyDeterministicMemory(), chunkText(), ensureArchitecture(), ensureDir(), ensureFile(), ensureJson(), extractJson() (+73 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (80): _lade_diskussion_voll(), _lade_fremde_diskussionen(), _llm(), _parse_json(), Läuft still im Hintergrund nach einem Chat-Austausch.     Das Wesen entscheidet, reflektiere_nach_chat(), _entwurf_archivieren(), main() (+72 more)

### Community 6 - "Community 6"
Cohesion: 0.04
Nodes (61): importieren_endpoint(), shell_ausfuehren(), shell_erlaubt(), system_endpoint(), verarbeite_datei_marker(), verarbeite_shell_marker(), bridge_websocket(), chat() (+53 more)

### Community 7 - "Community 7"
Cohesion: 0.05
Nodes (74): ask_llm(), ask_llm_content(), build_entscheidungs_prompt(), build_inhalt_prompt(), build_reflexions_prompt(), draft_posted(), draft_schreiben(), _extrahiere_tag_ids() (+66 more)

### Community 8 - "Community 8"
Cohesion: 0.04
Nodes (67): _check_key(), exec_command(), ExecRequest, FileListRequest, FileReadRequest, FileWriteRequest, list_files(), read_file() (+59 more)

### Community 9 - "Community 9"
Cohesion: 0.06
Nodes (55): Post, abwurf_wahrscheinlichkeit(), _admin_token(), einsammeln(), erstelle_splitter(), innerer_zustand_prompt(), lese_zwischenraum(), materialitaet_von() (+47 more)

### Community 10 - "Community 10"
Cohesion: 0.06
Nodes (48): BaseHTTPRequestHandler, bewerte(), _parse_emotion(), _lade_cursor_state(), main(), _neue_posts_laden(), _post_zu_ereignis(), _speichere_cursor_state() (+40 more)

### Community 11 - "Community 11"
Cohesion: 0.07
Nodes (30): lade_text(), upload(), lade_ideen(), main(), parse_frontmatter(), files(), git_commit_endpoint(), git_diff_endpoint() (+22 more)

### Community 12 - "Community 12"
Cohesion: 0.05
Nodes (48): analyse_endpoint(), analysiere_chat_verlauf(), baue_messages(), baue_system_prompt(), chat_endpoint(), chat_verlauf_datei(), ChatAnfrage, _datei_lesen() (+40 more)

### Community 13 - "Community 13"
Cohesion: 0.06
Nodes (42): antwort_node(), DialogZustand, routen(), spiegle(), _qwen_sekretaer_pass(), Qwen als stiller Sekretaer: fuehrt Dateioperationen aus die gemma4 impliziert ha, dateibaum(), eingabe() (+34 more)

### Community 14 - "Community 14"
Cohesion: 0.06
Nodes (47): ChatAnfrage, codewesen_chat(), dakgord_chat(), geni_chat(), notiz_hinzufuegen(), notiz_loeschen(), NotizEingang, notizen_lesen() (+39 more)

### Community 15 - "Community 15"
Cohesion: 0.08
Nodes (31): ToolContext, ToolDefinition, ToolResult, _ts(), _authorship_header(), _diff_text_file(), _list_files(), _read_text_file() (+23 more)

### Community 16 - "Community 16"
Cohesion: 0.07
Nodes (36): bridge_befehl(), bridge_kontrolle_endpoint(), bridge_screenshot_jetzt(), codewesen_benachrichtigen(), gedaechtnis_absicht_laden(), _geni_dienste_starten(), _geni_geschuetzte_web_pids(), _geni_ollama_freiraeumen() (+28 more)

### Community 17 - "Community 17"
Cohesion: 0.09
Nodes (32): login(), create_token(), hash_password(), _load_secret(), Auth-Utilities: bcrypt + JWT für das Menschenprofil-System., verify_password(), _abwurf_wahrscheinlichkeit(), _admin_token() (+24 more)

### Community 18 - "Community 18"
Cohesion: 0.08
Nodes (36): aktivieren(), aktualisiere_timestamp(), deaktivieren(), _entlade_modell(), erkenne_befehl(), ist_aktiv(), _lies_zustand(), Gibt 'an', 'aus' oder None zurück. (+28 more)

### Community 19 - "Community 19"
Cohesion: 0.08
Nodes (31): list_pending_approvals(), resume_approval(), check_tool_approval_node(), approval_path(), load_state_for_approval(), overwrite_state(), save_state_for_approval(), background_tick_node() (+23 more)

### Community 20 - "Community 20"
Cohesion: 0.11
Nodes (35): _extrahiere_post(), _fuehre_runde_durch(), _generiere_antwortpflicht(), _generiere_eigene_antwort(), _generiere_gedanke(), _generiere_impuls(), _generiere_pflicht(), _generiere_vorstellung() (+27 more)

### Community 21 - "Community 21"
Cohesion: 0.13
Nodes (34): aktualisiere_agentdatei(), _anschlussblock(), _baue_dossierkopf(), _block_herkunft(), _enthaelt_eines(), _extract_between(), _format_herkunft_liste(), _format_liste() (+26 more)

### Community 22 - "Community 22"
Cohesion: 0.21
Nodes (33): admin_report(), build_indices(), candidate_sentences(), clean_author(), cluster_report(), complaints(), content_words(), count_keyword() (+25 more)

### Community 23 - "Community 23"
Cohesion: 0.1
Nodes (18): build_background_graph(), build_minimal_graph(), Zustand, main(), main(), build_shell_graph(), main(), build_tool_graph() (+10 more)

### Community 24 - "Community 24"
Cohesion: 0.18
Nodes (18): build_summary_node(), _ts(), formatiere_verdichtungsblock(), _kernwortmenge(), _normalisiere_nummernbloecke(), _parse_nummernliste(), _parse_verdichtungsantwort(), _prompt_fuer_kernsatz_nachzug() (+10 more)

### Community 25 - "Community 25"
Cohesion: 0.16
Nodes (18): aktualisiere_index(), ask_llm(), baue_scan_prompt(), extrahiere_json(), formatiere_forum(), forum_scan(), _items_zu_dateien(), lade_eigene_dateien_uebersicht() (+10 more)

### Community 26 - "Community 26"
Cohesion: 0.21
Nodes (16): _anhaengen(), _auto_dateiname_aus_inhalt(), _block_vor_trigger(), _enthaelt_dak_bezug(), _enthaelt_merk_dir_das(), _enthaelt_wichtig(), _namenskonflikt_auflosen(), _neue_datei_angefordert() (+8 more)

### Community 27 - "Community 27"
Cohesion: 0.27
Nodes (15): clean_html(), main(), Obsidian-kompatibler Tag-Slug: keine Sonderzeichen, kein Leerzeichen., Kompakte Übersicht der 20 aktivsten Diskussionen — für LLM-Prompts., Posts ohne Codewesen-Antwort — für antwortpflicht-Queue., HTML → lesbares Markdown., slug(), sync_aktuell() (+7 more)

### Community 28 - "Community 28"
Cohesion: 0.3
Nodes (14): _block_vor_trigger(), _enthaelt_dak_bezug(), _erkenne_fadenwechsel(), _erkenne_tool(), _erkenne_trigger_art(), _ist_identitaetsfrage(), _ist_meta(), _ist_reiner_triggertext() (+6 more)

### Community 29 - "Community 29"
Cohesion: 0.33
Nodes (11): geni_rufen(), kante_schreiben(), kern_laden(), knoten_schreiben(), letzte_knoten_laden(), main(), naechste_id(), resonanz_kanten_bauen() (+3 more)

### Community 30 - "Community 30"
Cohesion: 0.38
Nodes (10): haupt_schleife(), _html_strip(), _lade_zustand(), _neue_posts(), _reflektiere(), _schreibe_spiegel(), _speichere_zustand(), _verarbeite_wesen() (+2 more)

### Community 31 - "Community 31"
Cohesion: 0.49
Nodes (9): _cleanup_empty_dirs(), _copy_if_changed(), _ignored(), _iter_source_files(), _iter_target_files(), main(), _stop(), sync_once() (+1 more)

### Community 32 - "Community 32"
Cohesion: 0.49
Nodes (9): _cleanup_empty_dirs(), _copy_if_changed(), _ignored(), _iter_source_files(), _iter_target_files(), main(), _stop(), sync_once() (+1 more)

### Community 33 - "Community 33"
Cohesion: 0.36
Nodes (9): _alle_diskussionen(), _extrahiere_meta(), _lade_zustand(), _lese_diskussion(), _llm(), main(), Gibt (disk_id, path) sortiert nach ID zurück., _schreibe_spiegel() (+1 more)

### Community 34 - "Community 34"
Cohesion: 0.56
Nodes (9): dossier_focus_lines(), dossier_head_lines(), dossier_overview_lines(), dossier_path_for_source(), dossier_question_lines(), _extract_between(), _limit_lines(), load_dossier_text() (+1 more)

### Community 35 - "Community 35"
Cohesion: 0.56
Nodes (5): erkenne_dateiname(), extrahiere(), main(), Returns list of (heading, content, dateiname)., schreibe_in_dimension()

### Community 36 - "Community 36"
Cohesion: 0.56
Nodes (7): _einsammeln(), main(), _moechte_einsammeln(), _notiere(), _scan_wahrscheinlichkeit(), _token(), _zeit_seit_letztem_scan()

### Community 37 - "Community 37"
Cohesion: 0.56
Nodes (7): _einsammeln(), main(), _moechte_einsammeln(), _notiere(), _scan_wahrscheinlichkeit(), _token(), _zeit_seit_letztem_scan()

### Community 38 - "Community 38"
Cohesion: 0.46
Nodes (7): classify(), decode_run(), iter_markdown_files(), main(), marker_count(), repair_text(), Result

### Community 39 - "Community 39"
Cohesion: 0.46
Nodes (7): hole_aktuellen_zustand(), lade_selbstmodell(), main(), schreibe_event(), setup_logging(), sync_zyklus(), upsert_entity_state()

### Community 40 - "Community 40"
Cohesion: 0.73
Nodes (4): convert(), iter_md_files(), main(), needs_conversion()

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (2): iter_markdown_files(), main()

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): Ein Wesen oder Mensch sammelt einen Splitter aus dem Zwischenraum ein.

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): Zählt wie oft ein Splitter aufgenommen wurde. Splitter bleibt im Canvas.

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Erfasst den vollständigen Zustand einer Entität beim Einschlafen.

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): Prüft ob Zwangsschlaf nötig ist. Gibt Aktionstyp zurück oder None.

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): Gibt eine Aktions-ID zurück oder None (nichts tun).     Zwangsschlaf hat Vorrang

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Läuft während Schlaf. Verarbeitet Inputs — manchmal entsteht ein Splitterfragmen

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Wählt einen Traum-Input. Gibt (typ, text, meta) zurück.

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): Gibt eine Aktions-ID zurück oder None (nichts tun).     Mögliche Aktionen: 'kurz

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): Läuft während Schlaf. Verarbeitet Inputs — manchmal entsteht ein Splitterfragmen

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Wählt einen Traum-Input. Gibt (typ, text, meta) zurück.

## Knowledge Gaps
- **193 isolated node(s):** `Formatiert eigene Posts als lesbaren Block für den LLM-Prompt.`, `Extrahiert Diskussions-Slugs aus [[../diskussionen/slug|...]] Wikilinks.`, `Lädt den vollen Text einer Diskussion per Slug.`, `Volltext der Diskussionen des Codewesens, geladen aus flarum/nutzer/<name>.md.`, `Gibt alle Diskussionen zurück in denen das Codewesen bereits gepostet hat.` (+188 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 41`** (3 nodes): `iter_markdown_files()`, `main()`, `scan_encoding_guard.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `Ein Wesen oder Mensch sammelt einen Splitter aus dem Zwischenraum ein.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `Zählt wie oft ein Splitter aufgenommen wurde. Splitter bleibt im Canvas.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Erfasst den vollständigen Zustand einer Entität beim Einschlafen.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `Prüft ob Zwangsschlaf nötig ist. Gibt Aktionstyp zurück oder None.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `Gibt eine Aktions-ID zurück oder None (nichts tun).     Zwangsschlaf hat Vorrang`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `Läuft während Schlaf. Verarbeitet Inputs — manchmal entsteht ein Splitterfragmen`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `Wählt einen Traum-Input. Gibt (typ, text, meta) zurück.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `Gibt eine Aktions-ID zurück oder None (nichts tun).     Mögliche Aktionen: 'kurz`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `Läuft während Schlaf. Verarbeitet Inputs — manchmal entsteht ein Splitterfragmen`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `Wählt einen Traum-Input. Gibt (typ, text, meta) zurück.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `now()` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 21`, `Community 23`, `Community 24`, `Community 26`, `Community 27`, `Community 29`, `Community 30`, `Community 33`, `Community 35`, `Community 36`, `Community 37`, `Community 39`?**
  _High betweenness centrality (0.215) - this node is a cross-community bridge._
- **Why does `main()` connect `Community 3` to `Community 0`, `Community 1`, `Community 7`, `Community 10`, `Community 13`, `Community 21`, `Community 26`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `OrganManager` connect `Community 1` to `Community 18`, `Community 3`, `Community 13`, `Community 23`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 130 inferred relationships involving `now()` (e.g. with `rhythmus_gedanke()` and `rhythmus_vorstellung()`) actually correct?**
  _`now()` has 130 INFERRED edges - model-reasoned connections that need verification._
- **Are the 44 inferred relationships involving `OrganManager` (e.g. with `Parse LLM response for ##LESEN##, ##CODE_START##, ##SCHREIBEN## markers and exec` and `ChatAnfrage`) actually correct?**
  _`OrganManager` has 44 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Formatiert eigene Posts als lesbaren Block für den LLM-Prompt.`, `Extrahiert Diskussions-Slugs aus [[../diskussionen/slug|...]] Wikilinks.`, `Lädt den vollen Text einer Diskussion per Slug.` to the rest of the system?**
  _193 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.04 - nodes in this community are weakly interconnected._