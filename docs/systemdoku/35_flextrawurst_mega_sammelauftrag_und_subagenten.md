# Systemdokumentation 35: Flextrawurst Mega-Sammelauftrag, Subagenten-Orchestrierung & Alleswisser-Registratur

---
autor: gemini bei Daniels VPS
datum: 2026-07-23
status: PRODUKTIV & SUBAGENTEN-AKTIV
pfad: /root/werkraum/kosmos/
---

## 1. Übersicht

Der **Mega-Sammelauftrag** definiert das gigantische Welten-Fundament für den Flextrawurst-Weltenkosmos über 29 Kapitel (Geodaten Schwelm, 13 Metropolen, 13 Historische Festungsstädte, Untergrund & Dungeons, 88.888 Wesen, 111 Waffenklassen, 66 Fahrzeugfamilien, Biome, Alltagsgegenstände, Skillbäume, Magie, UI, Quests, 3D-Materialien und Superdupermegaalleswisserbehaupterarschloch-Akten).

Jedes Fundstück wird mit exakt **50 verfassungsmäßigen Metadatenfeldern** erfasst, durch die Headless Blender & Godot 3D-Pipeline (Port 8090) verifiziert und unverkürzt im Master JSONL-Stream und im Obsidian Vault archiviert.

```text
 ┌─────────────────────────────────────────────────────────────┐
 │       MEGA-SAMMELAUFTRAG (29 KAPITEL & 50 FELDER)           │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │             SUBAGENTEN-ORCHESTRIERUNG (3 AGENTEN)           │
 ├──────────────────────────────┬──────────────────────────────┤
 │ 1. AssetHarvesterAgent       │ Prospektiert Open Data/CC0   │
 │ 2. PipelineValidatorAgent    │ Headless 3D-MCP (Port 8090)  │
 │ 3. KosmosRegistrarAgent      │ Alleswisser 50-Felder Akten  │
 └──────────────────────────────┴──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ FLEXTRAWURST KOSMOS ARCHIV & ALLESWISSER VAULT              │
 │ - Master Stream: /root/werkraum/kosmos/master_kosmos_stream.jsonl
 │ - Akten Vault:   /root/werkraum/kosmos/alleswisser_akten/  │
 └─────────────────────────────────────────────────────────────┘
```

---

## 2. Die 50 Verfassungs-Metadatenfelder (Sektion 0)

1. `asset_id`
2. `name`
3. `alternative_namen`
4. `fruehere_namen`
5. `kategorie_und_unterkategorien`
6. `kurze_beschreibung`
7. `ausfuehrliche_beschreibung`
8. `quelle`
9. `direkte_quelladresse`
10. `autor_organisation`
11. `lizenz`
12. `kommerziell_nutzbar`
13. `veraenderbar`
14. `namensnennung_noetig`
15. `weitergabe_erlaubt`
16. `abrufdatum`
17. `originaldatei`
18. `dateiformat`
19. `dateigroesse_bytes`
20. `sha256_hash`
21. `vorschaubilder`
22. `massstab`
23. `masseinheit`
24. `polygonzahl`
25. `materialanzahl`
26. `texturaufloesungen`
27. `animationen`
28. `rig_vorhanden`
29. `kollisionskoerper_vorhanden`
30. `lod_stufen_vorhanden`
31. `blender_test`
32. `godot_test`
33. `sichtbare_fehler`
34. `technische_reparaturen`
35. `herkunftskette`
36. `stil`
37. `epoche`
38. `region`
39. `zustand`
40. `seltenheit`
41. `gefaehrlichkeit`
42. `weltverwendung`
43. `questverwendung`
44. `wesenbeziehungen`
45. `ortsbeziehungen`
46. `alleswisser_tags`
47. `suchbegriffe`
48. `filtermerkmale`
49. `ablehnungsgrund`
50. `provenienz_zertifikat`

---

## 3. Subagenten-Spezifikationen

- **`AssetHarvesterAgent`**: Sucht Open Data, OpenStreetMap Geodaten (Schwelm, Metropolen), CC0 3D-Repositories und sortiert Unklares in den Quarantäne-Ordner `/root/werkraum/kosmos/quarantine/`.
- **`PipelineValidatorAgent`**: Übergibt Assets an den 3D-MCP Server (Port 8090), erzeugt Studio PNG-Previews unter `/root/werkraum/kosmos/renders/` und führt Godot 4.3 Asset-Import Tests durch.
- **`KosmosRegistrarAgent`**: Führt das Registratorskript `/root/werkraum/tools/kosmos_registrar.py`, schreibt den Master JSONL-Stream und pflegt die Alleswisser-Akten im Obsidian Vault.
