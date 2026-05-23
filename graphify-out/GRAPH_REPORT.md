# Graph Report - werkraum  (2026-05-23)

## Corpus Check
- 185 files · ~19,309,952 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1771 nodes · 4081 edges · 35 communities detected
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 1056 edges (avg confidence: 0.76)
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

## God Nodes (most connected - your core abstractions)
1. `now()` - 131 edges
2. `get_conn()` - 66 edges
3. `OrganManager` - 54 edges
4. `Zwischenraumorgan` - 45 edges
5. `run()` - 45 edges
6. `write()` - 42 edges
7. `main()` - 41 edges
8. `Post` - 40 edges
9. `Beziehungsorgan` - 36 edges
10. `main()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `vault_suche()` --calls--> `suche()`  [INFERRED]
  obsidian_api.py → welt/api.py
- `codewesen_benachrichtigen()` --calls--> `now()`  [INFERRED]
  geni/archiv/web.py → agent/agent.js
- `speichere_post()` --calls--> `write()`  [INFERRED]
  gedaechtnis.py → app/main.py
- `speichere_post()` --calls--> `fuehre_aktion_aus()`  [INFERRED]
  gedaechtnis.py → codewesen_agent.py
- `speichere_post()` --calls--> `fuehre_post_aus()`  [INFERRED]
  gedaechtnis.py → codewesen_chat.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.03
Nodes (86): Beziehungsorgan, Beziehungszustand, Liest Nutzereingabe und aktualisiert Beziehungszustand., Feedback-Loop: Liest LLM-Antwort und aktualisiert Zustand.          Signale: Mar, Abwaegung, Entscheidungsorgan, Erinnerung, Erinnerungsgedaechtnis (+78 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (100): list_pending_approvals(), resume_approval(), check_tool_approval_node(), approval_path(), load_state_for_approval(), overwrite_state(), save_state_for_approval(), aktualisiere_index() (+92 more)

### Community 2 - "Community 2"
Cohesion: 0.04
Nodes (122): admin_create_user(), admin_gedankenblase_patch(), admin_list_users(), admin_patch_module(), admin_patch_user(), admin_post_erstellen(), admin_raum_erstellen(), admin_raum_patch() (+114 more)

### Community 3 - "Community 3"
Cohesion: 0.04
Nodes (93): appendText(), applyDeterministicMemory(), chunkText(), ensureArchitecture(), ensureDir(), ensureFile(), ensureJson(), extractJson() (+85 more)

### Community 4 - "Community 4"
Cohesion: 0.03
Nodes (98): agentic_loop(), analysiere_gespraech_vereinbarungen(), ask_llm(), extrahiere_json(), fuehre_aktion_aus(), get_tags_cached(), load_token(), obsidian_navigation() (+90 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (80): create_token(), BaseHTTPRequestHandler, _abwurf_wahrscheinlichkeit(), _admin_token(), _erstelle_splitter(), _klassifiziere(), main(), _notiere() (+72 more)

### Community 6 - "Community 6"
Cohesion: 0.05
Nodes (83): aktualisiere_anschlusskontext(), aktualisiere_fokuskontext(), AnschlussKontext, FokusKontext, formatiere_schreibblock(), hole_anschlusskontext(), hole_fokuskontext(), _lade_rohdaten() (+75 more)

### Community 7 - "Community 7"
Cohesion: 0.04
Nodes (80): _lade_diskussion_voll(), _lade_fremde_diskussionen(), _llm(), _parse_json(), Läuft still im Hintergrund nach einem Chat-Austausch.     Das Wesen entscheidet, reflektiere_nach_chat(), _entwurf_archivieren(), main() (+72 more)

### Community 8 - "Community 8"
Cohesion: 0.05
Nodes (73): BaseHTTPMiddleware, _geni_dienste_starten(), _geni_geschuetzte_web_pids(), _geni_ollama_freiraeumen(), PIDs der drei interaktiven Chat-Webserver — niemals killen., aktives_fenster_info(), handle_befehl(), handle_fenster_anfrage() (+65 more)

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (74): ask_llm(), ask_llm_content(), build_entscheidungs_prompt(), build_inhalt_prompt(), build_reflexions_prompt(), draft_posted(), draft_schreiben(), _extrahiere_tag_ids() (+66 more)

### Community 10 - "Community 10"
Cohesion: 0.04
Nodes (55): importieren_endpoint(), shell_ausfuehren(), shell_erlaubt(), verarbeite_datei_marker(), verarbeite_shell_marker(), upload(), FileSystemEventHandler, DateiHoerer (+47 more)

### Community 11 - "Community 11"
Cohesion: 0.04
Nodes (58): system_endpoint(), antwort_node(), DialogZustand, lese(), routen(), ChatAnfrage, codewesen_chat(), dakgord_chat() (+50 more)

### Community 12 - "Community 12"
Cohesion: 0.05
Nodes (56): aktivieren(), aktualisiere_timestamp(), deaktivieren(), _entlade_modell(), erkenne_befehl(), ist_aktiv(), _lies_zustand(), Gibt 'an', 'aus' oder None zurück. (+48 more)

### Community 13 - "Community 13"
Cohesion: 0.05
Nodes (48): analyse_endpoint(), analysiere_chat_verlauf(), baue_messages(), baue_system_prompt(), chat_endpoint(), chat_verlauf_datei(), ChatAnfrage, _datei_lesen() (+40 more)

### Community 14 - "Community 14"
Cohesion: 0.07
Nodes (28): lade_text(), lade_ideen(), main(), parse_frontmatter(), files(), git_commit_endpoint(), git_diff_endpoint(), git_status_endpoint() (+20 more)

### Community 15 - "Community 15"
Cohesion: 0.1
Nodes (36): Post, haupt_schleife(), _html_strip(), _lade_zustand(), _neue_posts(), _reflektiere(), _schreibe_spiegel(), _speichere_zustand() (+28 more)

### Community 16 - "Community 16"
Cohesion: 0.11
Nodes (35): _extrahiere_post(), _fuehre_runde_durch(), _generiere_antwortpflicht(), _generiere_eigene_antwort(), _generiere_gedanke(), _generiere_impuls(), _generiere_pflicht(), _generiere_vorstellung() (+27 more)

### Community 17 - "Community 17"
Cohesion: 0.11
Nodes (24): ToolContext, ToolDefinition, ToolResult, _ts(), _authorship_header(), _diff_text_file(), _list_files(), _read_text_file() (+16 more)

### Community 18 - "Community 18"
Cohesion: 0.13
Nodes (34): aktualisiere_agentdatei(), _anschlussblock(), _baue_dossierkopf(), _block_herkunft(), _enthaelt_eines(), _extract_between(), _format_herkunft_liste(), _format_liste() (+26 more)

### Community 19 - "Community 19"
Cohesion: 0.21
Nodes (33): admin_report(), build_indices(), candidate_sentences(), clean_author(), cluster_report(), complaints(), content_words(), count_keyword() (+25 more)

### Community 20 - "Community 20"
Cohesion: 0.11
Nodes (25): refresh_focus_node(), _ts(), read_file_node(), resolve_file_node(), _ts(), build_summary_node(), _ts(), _ts() (+17 more)

### Community 21 - "Community 21"
Cohesion: 0.1
Nodes (18): build_background_graph(), build_minimal_graph(), Zustand, main(), main(), build_shell_graph(), main(), build_tool_graph() (+10 more)

### Community 22 - "Community 22"
Cohesion: 0.15
Nodes (22): log(), main(), _append(), _finde_visionen(), _finde_werkraumdateien(), _ignoriert(), _ist_interessant_werkraumdatei(), _ist_unter() (+14 more)

### Community 23 - "Community 23"
Cohesion: 0.27
Nodes (15): clean_html(), main(), Obsidian-kompatibler Tag-Slug: keine Sonderzeichen, kein Leerzeichen., Kompakte Übersicht der 20 aktivsten Diskussionen — für LLM-Prompts., Posts ohne Codewesen-Antwort — für antwortpflicht-Queue., HTML → lesbares Markdown., slug(), sync_aktuell() (+7 more)

### Community 24 - "Community 24"
Cohesion: 0.3
Nodes (14): _block_vor_trigger(), _enthaelt_dak_bezug(), _erkenne_fadenwechsel(), _erkenne_tool(), _erkenne_trigger_art(), _ist_identitaetsfrage(), _ist_meta(), _ist_reiner_triggertext() (+6 more)

### Community 25 - "Community 25"
Cohesion: 0.33
Nodes (11): geni_rufen(), kante_schreiben(), kern_laden(), knoten_schreiben(), letzte_knoten_laden(), main(), naechste_id(), resonanz_kanten_bauen() (+3 more)

### Community 26 - "Community 26"
Cohesion: 0.49
Nodes (9): _cleanup_empty_dirs(), _copy_if_changed(), _ignored(), _iter_source_files(), _iter_target_files(), main(), _stop(), sync_once() (+1 more)

### Community 27 - "Community 27"
Cohesion: 0.49
Nodes (9): _cleanup_empty_dirs(), _copy_if_changed(), _ignored(), _iter_source_files(), _iter_target_files(), main(), _stop(), sync_once() (+1 more)

### Community 28 - "Community 28"
Cohesion: 0.56
Nodes (9): dossier_focus_lines(), dossier_head_lines(), dossier_overview_lines(), dossier_path_for_source(), dossier_question_lines(), _extract_between(), _limit_lines(), load_dossier_text() (+1 more)

### Community 29 - "Community 29"
Cohesion: 0.56
Nodes (7): _einsammeln(), main(), _moechte_einsammeln(), _notiere(), _scan_wahrscheinlichkeit(), _token(), _zeit_seit_letztem_scan()

### Community 30 - "Community 30"
Cohesion: 0.56
Nodes (5): erkenne_dateiname(), extrahiere(), main(), Returns list of (heading, content, dateiname)., schreibe_in_dimension()

### Community 31 - "Community 31"
Cohesion: 0.46
Nodes (7): classify(), decode_run(), iter_markdown_files(), main(), marker_count(), repair_text(), Result

### Community 32 - "Community 32"
Cohesion: 0.46
Nodes (7): hole_aktuellen_zustand(), lade_selbstmodell(), main(), schreibe_event(), setup_logging(), sync_zyklus(), upsert_entity_state()

### Community 33 - "Community 33"
Cohesion: 0.73
Nodes (4): convert(), iter_md_files(), main(), needs_conversion()

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (2): iter_markdown_files(), main()

## Knowledge Gaps
- **177 isolated node(s):** `Formatiert eigene Posts als lesbaren Block für den LLM-Prompt.`, `Extrahiert Diskussions-Slugs aus [[../diskussionen/slug|...]] Wikilinks.`, `Lädt den vollen Text einer Diskussion per Slug.`, `Volltext der Diskussionen des Codewesens, geladen aus flarum/nutzer/<name>.md.`, `Gibt alle Diskussionen zurück in denen das Codewesen bereits gepostet hat.` (+172 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 34`** (3 nodes): `iter_markdown_files()`, `main()`, `scan_encoding_guard.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `now()` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 20`, `Community 21`, `Community 22`, `Community 23`, `Community 25`, `Community 29`, `Community 30`, `Community 32`?**
  _High betweenness centrality (0.239) - this node is a cross-community bridge._
- **Why does `main()` connect `Community 6` to `Community 0`, `Community 1`, `Community 3`, `Community 9`, `Community 18`, `Community 22`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `run()` connect `Community 8` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 6`, `Community 10`, `Community 13`, `Community 14`, `Community 17`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 124 inferred relationships involving `now()` (e.g. with `rhythmus_gedanke()` and `rhythmus_vorstellung()`) actually correct?**
  _`now()` has 124 INFERRED edges - model-reasoned connections that need verification._
- **Are the 44 inferred relationships involving `OrganManager` (e.g. with `Parse LLM response for ##LESEN##, ##CODE_START##, ##SCHREIBEN## markers and exec` and `ChatAnfrage`) actually correct?**
  _`OrganManager` has 44 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `Zwischenraumorgan` (e.g. with `Smoke tests for dak-gord-system core components.` and `All core modules must import without error.`) actually correct?**
  _`Zwischenraumorgan` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 44 inferred relationships involving `run()` (e.g. with `check_services()` and `check_innenleben()`) actually correct?**
  _`run()` has 44 INFERRED edges - model-reasoned connections that need verification._