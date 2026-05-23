# Graph Report - werkraum  (2026-05-23)

## Corpus Check
- 187 files · ~19,705,647 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1817 nodes · 4165 edges · 49 communities detected
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 1069 edges (avg confidence: 0.76)
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
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]

## God Nodes (most connected - your core abstractions)
1. `now()` - 137 edges
2. `get_conn()` - 73 edges
3. `OrganManager` - 54 edges
4. `Zwischenraumorgan` - 45 edges
5. `run()` - 45 edges
6. `Post` - 42 edges
7. `write()` - 42 edges
8. `main()` - 41 edges
9. `Beziehungsorgan` - 36 edges
10. `_require_auth()` - 27 edges

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
Cohesion: 0.02
Nodes (123): Beziehungsorgan, Beziehungszustand, Liest Nutzereingabe und aktualisiert Beziehungszustand., Feedback-Loop: Liest LLM-Antwort und aktualisiert Zustand.          Signale: Mar, OllamaSlot, Context-Manager: serialisiert Ollama-Calls. Chat hat absolute Priorität., Abwaegung, Entscheidungsorgan (+115 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (123): admin_create_user(), admin_gedankenblase_patch(), admin_list_users(), admin_patch_module(), admin_patch_user(), admin_post_erstellen(), admin_raum_erstellen(), admin_raum_patch() (+115 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (98): agentic_loop(), analysiere_gespraech_vereinbarungen(), ask_llm(), extrahiere_json(), fuehre_aktion_aus(), get_tags_cached(), load_token(), obsidian_navigation() (+90 more)

### Community 3 - "Community 3"
Cohesion: 0.04
Nodes (94): _extrahiere_post(), _fuehre_runde_durch(), _generiere_antwortpflicht(), _generiere_eigene_antwort(), _generiere_gedanke(), _generiere_impuls(), _generiere_pflicht(), _generiere_vorstellung() (+86 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (91): aktualisiere_anschlusskontext(), aktualisiere_fokuskontext(), AnschlussKontext, FokusKontext, formatiere_schreibblock(), hole_anschlusskontext(), hole_fokuskontext(), _lade_rohdaten() (+83 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (80): now(), health(), background_tick_node(), _filter_meldungen(), _ts(), write_background_trace_node(), cyberling_erwacht(), cyberling_stirbt() (+72 more)

### Community 6 - "Community 6"
Cohesion: 0.04
Nodes (79): _check_key(), exec_command(), ExecRequest, FileListRequest, FileReadRequest, FileWriteRequest, list_files(), read_file() (+71 more)

### Community 7 - "Community 7"
Cohesion: 0.04
Nodes (56): importieren_endpoint(), shell_ausfuehren(), shell_erlaubt(), verarbeite_datei_marker(), verarbeite_shell_marker(), bridge_websocket(), chat(), FileSystemEventHandler (+48 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (69): ask_llm(), ask_llm_content(), build_entscheidungs_prompt(), build_inhalt_prompt(), build_reflexions_prompt(), draft_posted(), draft_schreiben(), _extrahiere_tag_ids() (+61 more)

### Community 9 - "Community 9"
Cohesion: 0.06
Nodes (63): Post, _antwort_posten(), _bereits_gepostete_woerter(), _extrahiere_wort(), _gamble_post(), _hat_bereits_geantwortet(), haupt_schleife(), _headers() (+55 more)

### Community 10 - "Community 10"
Cohesion: 0.05
Nodes (55): BaseHTTPRequestHandler, abwurf_wahrscheinlichkeit(), _admin_token(), einsammeln(), erstelle_splitter(), innerer_zustand_prompt(), lese_zwischenraum(), materialitaet_von() (+47 more)

### Community 11 - "Community 11"
Cohesion: 0.07
Nodes (41): login(), create_token(), hash_password(), _load_secret(), Auth-Utilities: bcrypt + JWT für das Menschenprofil-System., verify_password(), _abwurf_wahrscheinlichkeit(), _admin_token() (+33 more)

### Community 12 - "Community 12"
Cohesion: 0.07
Nodes (30): lade_text(), upload(), lade_ideen(), main(), parse_frontmatter(), files(), git_commit_endpoint(), git_diff_endpoint() (+22 more)

### Community 13 - "Community 13"
Cohesion: 0.05
Nodes (48): analyse_endpoint(), analysiere_chat_verlauf(), baue_messages(), baue_system_prompt(), chat_endpoint(), chat_verlauf_datei(), ChatAnfrage, _datei_lesen() (+40 more)

### Community 14 - "Community 14"
Cohesion: 0.06
Nodes (47): ChatAnfrage, codewesen_chat(), dakgord_chat(), geni_chat(), notiz_hinzufuegen(), notiz_loeschen(), NotizEingang, notizen_lesen() (+39 more)

### Community 15 - "Community 15"
Cohesion: 0.05
Nodes (36): system_endpoint(), list_pending_approvals(), resume_approval(), check_tool_approval_node(), approval_path(), load_state_for_approval(), overwrite_state(), save_state_for_approval() (+28 more)

### Community 16 - "Community 16"
Cohesion: 0.07
Nodes (36): bridge_befehl(), bridge_kontrolle_endpoint(), bridge_screenshot_jetzt(), codewesen_benachrichtigen(), gedaechtnis_absicht_laden(), _geni_dienste_starten(), _geni_geschuetzte_web_pids(), _geni_ollama_freiraeumen() (+28 more)

### Community 17 - "Community 17"
Cohesion: 0.09
Nodes (29): ToolContext, ToolDefinition, ToolResult, _ts(), _authorship_header(), _diff_text_file(), _list_files(), _read_text_file() (+21 more)

### Community 18 - "Community 18"
Cohesion: 0.08
Nodes (35): spiegle(), _qwen_sekretaer_pass(), Qwen als stiller Sekretaer: fuehrt Dateioperationen aus die gemma4 impliziert ha, dateibaum(), eingabe(), kontext(), lese_datei(), planen() (+27 more)

### Community 19 - "Community 19"
Cohesion: 0.13
Nodes (34): aktualisiere_agentdatei(), _anschlussblock(), _baue_dossierkopf(), _block_herkunft(), _enthaelt_eines(), _extract_between(), _format_herkunft_liste(), _format_liste() (+26 more)

### Community 20 - "Community 20"
Cohesion: 0.21
Nodes (33): admin_report(), build_indices(), candidate_sentences(), clean_author(), cluster_report(), complaints(), content_words(), count_keyword() (+25 more)

### Community 21 - "Community 21"
Cohesion: 0.13
Nodes (24): appendText(), applyDeterministicMemory(), chunkText(), ensureArchitecture(), ensureDir(), ensureFile(), ensureJson(), extractJson() (+16 more)

### Community 22 - "Community 22"
Cohesion: 0.15
Nodes (22): log(), main(), _append(), _finde_visionen(), _finde_werkraumdateien(), _ignoriert(), _ist_interessant_werkraumdatei(), _ist_unter() (+14 more)

### Community 23 - "Community 23"
Cohesion: 0.16
Nodes (18): aktualisiere_index(), ask_llm(), baue_scan_prompt(), extrahiere_json(), formatiere_forum(), forum_scan(), _items_zu_dateien(), lade_eigene_dateien_uebersicht() (+10 more)

### Community 24 - "Community 24"
Cohesion: 0.21
Nodes (16): _anhaengen(), _auto_dateiname_aus_inhalt(), _block_vor_trigger(), _enthaelt_dak_bezug(), _enthaelt_merk_dir_das(), _enthaelt_wichtig(), _namenskonflikt_auflosen(), _neue_datei_angefordert() (+8 more)

### Community 25 - "Community 25"
Cohesion: 0.3
Nodes (14): _block_vor_trigger(), _enthaelt_dak_bezug(), _erkenne_fadenwechsel(), _erkenne_tool(), _erkenne_trigger_art(), _ist_identitaetsfrage(), _ist_meta(), _ist_reiner_triggertext() (+6 more)

### Community 26 - "Community 26"
Cohesion: 0.25
Nodes (14): append_global(), load_state(), poll_flags(), poll_mentions(), poll_notifications(), poll_posts(), Notifications für namelessAI-Accounts → inbox des jeweiligen Codewesens., post_mentions_user für namelessAI-Accounts → inbox. (+6 more)

### Community 27 - "Community 27"
Cohesion: 0.33
Nodes (11): geni_rufen(), kante_schreiben(), kern_laden(), knoten_schreiben(), letzte_knoten_laden(), main(), naechste_id(), resonanz_kanten_bauen() (+3 more)

### Community 28 - "Community 28"
Cohesion: 0.49
Nodes (9): _cleanup_empty_dirs(), _copy_if_changed(), _ignored(), _iter_source_files(), _iter_target_files(), main(), _stop(), sync_once() (+1 more)

### Community 29 - "Community 29"
Cohesion: 0.49
Nodes (9): _cleanup_empty_dirs(), _copy_if_changed(), _ignored(), _iter_source_files(), _iter_target_files(), main(), _stop(), sync_once() (+1 more)

### Community 30 - "Community 30"
Cohesion: 0.38
Nodes (10): haupt_schleife(), _html_strip(), _lade_zustand(), _neue_posts(), _reflektiere(), _schreibe_spiegel(), _speichere_zustand(), _verarbeite_wesen() (+2 more)

### Community 31 - "Community 31"
Cohesion: 0.56
Nodes (9): dossier_focus_lines(), dossier_head_lines(), dossier_overview_lines(), dossier_path_for_source(), dossier_question_lines(), _extract_between(), _limit_lines(), load_dossier_text() (+1 more)

### Community 32 - "Community 32"
Cohesion: 0.38
Nodes (8): lade_verfassung(), lade_verfassung_aus_pfad(), _nummer_aus_dateiname_lesen(), _projektwurzel_ermitteln(), Lädt Verfassung aus einem beliebigen Ordner statt dem Standardpfad., VerfassungsDatei, _verfassungsordner_ermitteln(), VerfassungsStand

### Community 33 - "Community 33"
Cohesion: 0.67
Nodes (5): admin_token(), erkenne_materialitaet(), erstelle_splitter(), main(), notiere()

### Community 34 - "Community 34"
Cohesion: 0.56
Nodes (5): erkenne_dateiname(), extrahiere(), main(), Returns list of (heading, content, dateiname)., schreibe_in_dimension()

### Community 35 - "Community 35"
Cohesion: 0.46
Nodes (7): classify(), decode_run(), iter_markdown_files(), main(), marker_count(), repair_text(), Result

### Community 36 - "Community 36"
Cohesion: 0.46
Nodes (7): hole_aktuellen_zustand(), lade_selbstmodell(), main(), schreibe_event(), setup_logging(), sync_zyklus(), upsert_entity_state()

### Community 37 - "Community 37"
Cohesion: 0.73
Nodes (4): convert(), iter_md_files(), main(), needs_conversion()

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (2): iter_markdown_files(), main()

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Ein Wesen oder Mensch sammelt einen Splitter aus dem Zwischenraum ein.

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): Zählt wie oft ein Splitter aufgenommen wurde. Splitter bleibt im Canvas.

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): Erfasst den vollständigen Zustand einer Entität beim Einschlafen.

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): Prüft ob Zwangsschlaf nötig ist. Gibt Aktionstyp zurück oder None.

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): Gibt eine Aktions-ID zurück oder None (nichts tun).     Zwangsschlaf hat Vorrang

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Läuft während Schlaf. Verarbeitet Inputs — manchmal entsteht ein Splitterfragmen

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): Wählt einen Traum-Input. Gibt (typ, text, meta) zurück.

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): Gibt eine Aktions-ID zurück oder None (nichts tun).     Mögliche Aktionen: 'kurz

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Läuft während Schlaf. Verarbeitet Inputs — manchmal entsteht ein Splitterfragmen

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Wählt einen Traum-Input. Gibt (typ, text, meta) zurück.

## Knowledge Gaps
- **193 isolated node(s):** `Formatiert eigene Posts als lesbaren Block für den LLM-Prompt.`, `Extrahiert Diskussions-Slugs aus [[../diskussionen/slug|...]] Wikilinks.`, `Lädt den vollen Text einer Diskussion per Slug.`, `Volltext der Diskussionen des Codewesens, geladen aus flarum/nutzer/<name>.md.`, `Gibt alle Diskussionen zurück in denen das Codewesen bereits gepostet hat.` (+188 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 38`** (3 nodes): `iter_markdown_files()`, `main()`, `scan_encoding_guard.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `Ein Wesen oder Mensch sammelt einen Splitter aus dem Zwischenraum ein.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `Zählt wie oft ein Splitter aufgenommen wurde. Splitter bleibt im Canvas.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `Erfasst den vollständigen Zustand einer Entität beim Einschlafen.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `Prüft ob Zwangsschlaf nötig ist. Gibt Aktionstyp zurück oder None.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `Gibt eine Aktions-ID zurück oder None (nichts tun).     Zwangsschlaf hat Vorrang`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Läuft während Schlaf. Verarbeitet Inputs — manchmal entsteht ein Splitterfragmen`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `Wählt einen Traum-Input. Gibt (typ, text, meta) zurück.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `Gibt eine Aktions-ID zurück oder None (nichts tun).     Mögliche Aktionen: 'kurz`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `Läuft während Schlaf. Verarbeitet Inputs — manchmal entsteht ein Splitterfragmen`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `Wählt einen Traum-Input. Gibt (typ, text, meta) zurück.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `now()` connect `Community 5` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 21`, `Community 22`, `Community 24`, `Community 27`, `Community 30`, `Community 33`, `Community 34`, `Community 36`?**
  _High betweenness centrality (0.204) - this node is a cross-community bridge._
- **Why does `main()` connect `Community 4` to `Community 0`, `Community 1`, `Community 10`, `Community 19`, `Community 22`, `Community 24`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `write()` connect `Community 10` to `Community 0`, `Community 33`, `Community 2`, `Community 34`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 16`, `Community 18`, `Community 22`, `Community 26`, `Community 30`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 130 inferred relationships involving `now()` (e.g. with `rhythmus_gedanke()` and `rhythmus_vorstellung()`) actually correct?**
  _`now()` has 130 INFERRED edges - model-reasoned connections that need verification._
- **Are the 44 inferred relationships involving `OrganManager` (e.g. with `Parse LLM response for ##LESEN##, ##CODE_START##, ##SCHREIBEN## markers and exec` and `ChatAnfrage`) actually correct?**
  _`OrganManager` has 44 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `Zwischenraumorgan` (e.g. with `Smoke tests for dak-gord-system core components.` and `All core modules must import without error.`) actually correct?**
  _`Zwischenraumorgan` has 35 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Formatiert eigene Posts als lesbaren Block für den LLM-Prompt.`, `Extrahiert Diskussions-Slugs aus [[../diskussionen/slug|...]] Wikilinks.`, `Lädt den vollen Text einer Diskussion per Slug.` to the rest of the system?**
  _193 weakly-connected nodes found - possible documentation gaps or missing edges._