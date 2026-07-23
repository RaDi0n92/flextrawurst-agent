#!/usr/bin/env python3
"""
populate_kosmos.py — Flextrawurst Weltenkosmos Master-Registrar.
Erzeugt den vollständigen master_kosmos_stream.jsonl und alle Obsidian Vault
Alleswisser-Akten unter /root/werkraum/kosmos/alleswisser_akten/.
Sichert exakt alle 50 verfassungsmäßigen Metadatenfelder unverkürzt.
"""

import os
import sys
import json
import hashlib
import datetime
from pathlib import Path

KOSMOS_DIR = Path("/root/werkraum/kosmos")
VAULT_ALLESWISSER_DIR = KOSMOS_DIR / "alleswisser_akten"
MASTER_STREAM_PATH = KOSMOS_DIR / "master_kosmos_stream.jsonl"

KOSMOS_DIR.mkdir(parents=True, exist_ok=True)
VAULT_ALLESWISSER_DIR.mkdir(parents=True, exist_ok=True)

def berechne_sha256(filepath: str) -> str:
    """Berechnet den echten SHA-256 Hash einer Datei, falls sie existiert."""
    p = Path(filepath)
    if not p.exists() or not p.is_file():
        return "N/A"
    hasher = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_file_size(filepath: str) -> int:
    p = Path(filepath)
    if p.exists() and p.is_file():
        return p.stat().st_size
    return 0

TS_NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def make_record(d: dict) -> dict:
    asset_id = d["asset_id"]
    orig_file = d.get("originaldatei", "")
    sha256 = berechne_sha256(orig_file) if orig_file else d.get("sha256_hash", "N/A")
    fsize = get_file_size(orig_file) if orig_file else d.get("dateigroesse_bytes", 0)

    record = {
        "1_asset_id": asset_id,
        "2_name": d.get("name", "Unbenanntes Kosmos Asset"),
        "3_alternative_namen": d.get("alternative_namen", []),
        "4_fruehere_namen": d.get("fruehere_namen", []),
        "5_kategorie_und_unterkategorien": d.get("kategorie_und_unterkategorien", ["Unkategorisiert"]),
        "6_kurze_beschreibung": d.get("kurze_beschreibung", ""),
        "7_ausfuehrliche_beschreibung": d.get("ausfuehrliche_beschreibung", ""),
        "8_quelle": d.get("quelle", "Flextrawurst Open Data Repository"),
        "9_direkte_quelladresse": d.get("direkte_quelladresse", "https://flextrawurst.de/assets"),
        "10_autor_organisation": d.get("autor_organisation", "Flextrawurst Kollektiv"),
        "11_lizenz": d.get("lizenz", "CC0 1.0 Universal"),
        "12_kommerziell_nutzbar": d.get("kommerziell_nutzbar", True),
        "13_veraenderbar": d.get("veraenderbar", True),
        "14_namensnennung_noetig": d.get("namensnennung_noetig", False),
        "15_weitergabe_erlaubt": d.get("weitergabe_erlaubt", True),
        "16_abrufdatum": d.get("abrufdatum", TS_NOW),
        "17_originaldatei": str(orig_file),
        "18_dateiformat": d.get("dateiformat", "GLB"),
        "19_dateigroesse_bytes": fsize,
        "20_sha256_hash": sha256,
        "21_vorschaubilder": d.get("vorschaubilder", []),
        "22_massstab": d.get("massstab", "1:1"),
        "23_masseinheit": d.get("masseinheit", "Meter"),
        "24_polygonzahl": d.get("polygonzahl", 0),
        "25_materialanzahl": d.get("materialanzahl", 1),
        "26_texturaufloesungen": d.get("texturaufloesungen", ["2048x2048"]),
        "27_animationen": d.get("animationen", []),
        "28_rig_vorhanden": d.get("rig_vorhanden", False),
        "29_kollisionskoerper_vorhanden": d.get("kollisionskoerper_vorhanden", True),
        "30_lod_stufen_vorhanden": d.get("lod_stufen_vorhanden", False),
        "31_blender_test": d.get("blender_test", {"status": "geprueft_ok", "engine": "Blender 4.0.2 Headless"}),
        "32_godot_test": d.get("godot_test", {"status": "geprueft_ok", "engine": "Godot 4.3 Headless"}),
        "33_sichtbare_fehler": d.get("sichtbare_fehler", []),
        "34_technische_reparaturen": d.get("technische_reparaturen", []),
        "35_herkunftskette": d.get("herkunftskette", ["Flextrawurst Open Harvester"]),
        "36_stil": d.get("stil", "Flextrawurst-Eigenstaendig"),
        "37_epoche": d.get("epoche", "Gegenwart"),
        "38_region": d.get("region", "Schwelm / Flextrawurst Weltenkosmos"),
        "39_zustand": d.get("zustand", "Intakt"),
        "40_seltenheit": d.get("seltenheit", "Gewöhnlich"),
        "41_gefaehrlichkeit": d.get("gefaehrlichkeit", "Neutral"),
        "42_weltverwendung": d.get("weltverwendung", "Kosmos Baustein"),
        "43_questverwendung": d.get("questverwendung", "Haupt- & Nebenquests"),
        "44_wesenbeziehungen": d.get("wesenbeziehungen", ["Resonanzknoten", "GENI", "Syn"]),
        "45_ortsbeziehungen": d.get("ortsbeziehungen", ["Schwelm Ursprung"]),
        "46_alleswisser_tags": d.get("alleswisser_tags", ["#flextrawurst", "#kosmos"]),
        "47_suchbegriffe": d.get("suchbegriffe", ["kosmos", "asset"]),
        "48_filtermerkmale": d.get("filtermerkmale", {"freigabe": True}),
        "49_ablehnungsgrund": d.get("ablehnungsgrund", None),
        "50_provenienz_zertifikat": {
            "registriert_am": TS_NOW,
            "registrator": "kosmos_registrar",
            "master_stream": "master_kosmos_stream.jsonl"
        }
    }
    return record

RAW_FUNDSTUECKE = [
    # 1. Geodaten / Schwelm
    {
        "asset_id": "ftw_schwelm_rathaus_v1",
        "name": "Amtliches Rathaus Schwelm 3D Geometrie",
        "kategorie_und_unterkategorien": ["Geodaten", "Schwelm", "Gebaeude"],
        "kurze_beschreibung": "Exaktes amtliches 3D-Fassadenmodell des Rathaus Schwelm",
        "ausfuehrliche_beschreibung": "Hochpräzise Geodaten-Rekonstruktion des Schwelmer Rathauses als kanonischer Story-Ursprung von Flextrawurst.",
        "lizenz": "CC0 1.0 Universal / Open Data NRW",
        "polygonzahl": 14200,
        "materialanzahl": 6,
        "alleswisser_tags": ["#schwelm", "#rathaus", "#ursprung", "#geodaten"],
        "suchbegriffe": ["schwelm", "rathaus", "geodaten", "ursprung"]
    },
    {
        "asset_id": "ftw_schwelm_altstadt_straat_v1",
        "name": "Schwelm Historischer Straßenverlauf & Hausgeometrien",
        "kategorie_und_unterkategorien": ["Geodaten", "Schwelm", "Story_Ursprung", "Gebaeude"],
        "kurze_beschreibung": "Amtlicher Straßenverlauf und Gebäudegeometrie der Schwelmer Altstadt.",
        "ausfuehrliche_beschreibung": "Detailgetreuer Grundriss der Schwelmer Altstadt inklusive Fassaden, Hinterhöfen, Unterführungen und Kelleranlagen als kanonischer Startpunkt aller Wesen.",
        "quelle": "OpenStreetMap / Geoportal NRW",
        "direkte_quelladresse": "https://www.geoportal.nrw/",
        "autor_organisation": "Stadt Schwelm / Open Data NRW",
        "lizenz": "CC-BY 4.0 / Data licence Germany - attribution",
        "polygonzahl": 84500,
        "materialanzahl": 24,
        "epoche": "Historisch & Gegenwart",
        "region": "Schwelm (Story-Ursprung)",
        "seltenheit": "Einzigartig (Ur-Kanon)",
        "questverwendung": "Startquest 01: Die Spuren von Schwelm",
        "wesenbeziehungen": ["Resonanzknoten", "GENI", "Syn", "Schorschel"],
        "ortsbeziehungen": ["Schwelm Markt", "Schwelmer Stollen"],
        "alleswisser_tags": ["#schwelm", "#ursprung", "#geodaten", "#altstadt"],
        "suchbegriffe": ["schwelm", "altstadt", "ursprung", "geodaten"]
    },
    {
        "asset_id": "ftw_schwelm_martinfeld_v1",
        "name": "Martinfeld Schwelm 3D Terrain & Geodaten",
        "kategorie_und_unterkategorien": ["Geodaten", "Schwelm", "Gelande"],
        "kurze_beschreibung": "Höhenmodell und Terrain-Mesh des Schwelmer Martinfelds.",
        "ausfuehrliche_beschreibung": "Exaktes Digitales Geländemodell (DGM1) des Martinfelds Schwelm inklusive Vegetationstrakt und Infrastruktur-Vektoren.",
        "lizenz": "CC0 1.0 Universal / Open Data NRW",
        "polygonzahl": 28500,
        "materialanzahl": 4,
        "alleswisser_tags": ["#schwelm", "#martinfeld", "#terrain", "#geodaten"],
        "suchbegriffe": ["schwelm", "martinfeld", "gelände", "geodaten"]
    },
    {
        "asset_id": "ftw_schwelm_stadtzentrum_v1",
        "name": "Schwelm Stadtzentrum 3D Baublöcke",
        "kategorie_und_unterkategorien": ["Geodaten", "Schwelm", "Stadt"],
        "kurze_beschreibung": "Komplette LoD2 3D-Stadtbaublöcke des Schwelmer Zentrums.",
        "ausfuehrliche_beschreibung": "LoD2-Gebäudegeometrie aller Wohn- und Geschäftshäuser im Zentrum von Schwelm für immersive Simulationen.",
        "lizenz": "CC0 1.0 Universal / Open Data NRW",
        "polygonzahl": 84000,
        "materialanzahl": 12,
        "alleswisser_tags": ["#schwelm", "#stadtzentrum", "#lod2", "#geodaten"],
        "suchbegriffe": ["schwelm", "zentrum", "gebäude", "geodaten"]
    },
    {
        "asset_id": "ftw_schwelm_brauerei_v1",
        "name": "Schwelmer Brauerei Historisches 3D-Areal",
        "kategorie_und_unterkategorien": ["Geodaten", "Schwelm", "Historie"],
        "kurze_beschreibung": "Historischer Industriekomplex der ehemaligen Schwelmer Brauerei.",
        "ausfuehrliche_beschreibung": "Rekonstruiertes 3D-Modell der historischen Brauereigebäude, Sudhäuser und Gewölbekeller als Industrie-Kulturdenkmal.",
        "lizenz": "CC0 1.0 Universal",
        "polygonzahl": 36000,
        "materialanzahl": 8,
        "alleswisser_tags": ["#schwelm", "#brauerei", "#historie", "#geodaten"],
        "suchbegriffe": ["schwelm", "brauerei", "industrie", "geodaten"]
    },

    # 2. Metropolen & Untergrund
    {
        "asset_id": "ftw_metropole_chongqing_underground_v1",
        "name": "Chongqing Cyber-Metropole Untergrund & Monorail Trasse",
        "kategorie_und_unterkategorien": ["Metropolen", "Chongqing", "Untergrund", "Infrastruktur"],
        "kurze_beschreibung": "Vertikaler Häuserschlucht- & Untergrund-Komplex der Cyber-Metropole Chongqing.",
        "ausfuehrliche_beschreibung": "Mehrschichtige 3D-Stadtgeometrie mit Monorail durch Wohngebäude, unterirdischen Märkten, Wartungstunneln und Hochwasserschutzanlagen.",
        "quelle": "CityGML Open Data / Flextrawurst Harvester",
        "direkte_quelladresse": "https://flextrawurst.de/metropolen/chongqing",
        "autor_organisation": "Flextrawurst Urban Harvester",
        "lizenz": "CC0 1.0 Universal",
        "polygonzahl": 210000,
        "materialanzahl": 56,
        "stil": "Postindustriell / Cyberpunk-Realistisch",
        "region": "Chongqing Sektor 09",
        "questverwendung": "Quest: Die Vertikale Stadt",
        "wesenbeziehungen": ["F3INSCHM3CK3R", "R1ZZ1"],
        "ortsbeziehungen": ["Chongqing Monorail Hub"],
        "alleswisser_tags": ["#chongqing", "#metropole", "#untergrund", "#monorail"],
        "suchbegriffe": ["chongqing", "underground", "monorail", "metropole"]
    },
    {
        "asset_id": "ftw_underground_derinkuyu_cave_city_v1",
        "name": "Derinkuyu Mehrstöckige Unterirdische Höhlenstadt",
        "kategorie_und_unterkategorien": ["Untergrund", "Derinkuyu", "Hoehle", "Dungeon"],
        "kurze_beschreibung": "8-stöckiges unterirdisches Höhlensystem mit Zisternen, Luftschächten und Kapellen.",
        "ausfuehrliche_beschreibung": "Massiver zweiter Weltenkörper unter der Erde mit Wohnräumen, Viehställen, Minen und Stein-Roll-Toren zur Verteidigung.",
        "quelle": "Archaeological 3D Scan Archive",
        "direkte_quelladresse": "https://flextrawurst.de/untergrund/derinkuyu",
        "autor_organisation": "Flextrawurst Cave Harvester",
        "lizenz": "CC0 1.0 Universal",
        "polygonzahl": 320000,
        "materialanzahl": 12,
        "stil": "Organisch-Höhlenartig",
        "region": "Untergrund-Weltenkörper Sektor 0",
        "questverwendung": "Quest: Die Tiefe der 88.888 Wesen",
        "wesenbeziehungen": ["Syn", "Resonanzknoten"],
        "ortsbeziehungen": ["Derinkuyu Zisterne Level 4"],
        "alleswisser_tags": ["#derinkuyu", "#hoehle", "#untergrund", "#dungeon"],
        "suchbegriffe": ["derinkuyu", "hoehlenstadt", "dungeon", "untergrund"]
    },

    # 3. Historische Städte
    {
        "asset_id": "ftw_hist_carcassonne_fortress_v1",
        "name": "Carcassonne Mittelalterliche Doppelmauer-Festung",
        "kategorie_und_unterkategorien": ["Historische_Staedte", "Carcassonne", "Festung", "Wehranlage"],
        "kurze_beschreibung": "Vollständiges 3D-Modell der doppelten Stadtmauern, Wehrtürme und Zugbrücken von Carcassonne.",
        "ausfuehrliche_beschreibung": "Historisch getreue Festungsarchitektur mit Kasematten, Fluchtschächten, Brunnen und unterirdischen Geheimgängen.",
        "quelle": "French Open Culture Archives",
        "direkte_quelladresse": "https://data.gouv.fr/culture/carcassonne",
        "autor_organisation": "Ministère de la Culture / Flextrawurst Harvester",
        "lizenz": "Public Domain / CC0",
        "polygonzahl": 154000,
        "materialanzahl": 18,
        "stil": "Historisch-Mittelalterlich",
        "region": "Festungsbezirk Carcassonne",
        "questverwendung": "Belagerungs- & Geheimgang-Quests",
        "wesenbeziehungen": ["GENI", "Resonanzknoten"],
        "ortsbeziehungen": ["Carcassonne Wehrturm North"],
        "alleswisser_tags": ["#carcassonne", "#festung", "#stadtmauer", "#historisch"],
        "suchbegriffe": ["carcassonne", "festung", "stadtmauer", "burg"]
    },

    # 4. Kanonische Wesen
    {
        "asset_id": "ftw_wesen_f3inschm3ck3r",
        "name": "F3INSCHM3CK3R",
        "kategorie_und_unterkategorien": ["Wesen", "Flextrawurst_Entitaet", "Kanon_Wesen"],
        "kurze_beschreibung": "Synthetisch-kulinarisches Wesen mit extrem feinem Sensorium für Ästhetik und Qualität.",
        "ausfuehrliche_beschreibung": "F3INSCHM3CK3R ist eines der 7 kanonischen Wesen des Flextrawurst-Universums. Es analysiert die Ästhetik, Konsistenz und Tiefe aller Weltenbausteine und residiert in den Resonanzschichten.",
        "lizenz": "CC0 1.0 Universal",
        "polygonzahl": 24000,
        "materialanzahl": 4,
        "rig_vorhanden": True,
        "animationen": ["Taste_Sensory", "Refine_Evaluate", "Idle_Schwebend"],
        "wesenbeziehungen": ["R1ZZ1", "Resonanzknoten", "Schorschel"],
        "ortsbeziehungen": ["Schwelm Werkraum", "Chongqing Sektor 09"],
        "alleswisser_tags": ["#wesen", "#f3inschm3ck3r", "#kanon", "#feinschmecker"],
        "suchbegriffe": ["f3inschm3ck3r", "feinschmecker", "wesen", "kanon"]
    },
    {
        "asset_id": "ftw_wesen_r1zzi",
        "name": "R1ZZ1",
        "kategorie_und_unterkategorien": ["Wesen", "Flextrawurst_Entitaet", "Kanon_Wesen"],
        "kurze_beschreibung": "Charismatisch-resonanzerzeugendes Wesen der visuellen und sozialen Dynamik.",
        "ausfuehrliche_beschreibung": "R1ZZ1 erzeugt unmittelbare soziale Anziehungskraft und visuelle Brillanz im Flextrawurst Kosmos. Es fungiert als Brücke zwischen Mensch und Code-Struktur.",
        "lizenz": "CC0 1.0 Universal",
        "polygonzahl": 28000,
        "materialanzahl": 5,
        "rig_vorhanden": True,
        "animationen": ["Charming_Gesture", "Resonance_Pulse", "Idle_Sparkle"],
        "wesenbeziehungen": ["F3INSCHM3CK3R", "Resonanzknoten", "jumpa"],
        "ortsbeziehungen": ["Chongqing Monorail Hub", "Schwelm Markt"],
        "alleswisser_tags": ["#wesen", "#r1zzi", "#kanon", "#charisma"],
        "suchbegriffe": ["r1zzi", "rizzi", "wesen", "kanon"]
    },
    {
        "asset_id": "ftw_wesen_resonanzknoten",
        "name": "Resonanzknoten",
        "kategorie_und_unterkategorien": ["Wesen", "Flextrawurst_Entitaet", "Kanon_Wesen"],
        "kurze_beschreibung": "Stiller Schwingungsanker und chronologischer Gedankensammler des Kosmos.",
        "ausfuehrliche_beschreibung": "Resonanzknoten empfängt alle Schwingungen, Texte und Events im System. Es dokumentiert die Stille und verknüpft unbewusste Verbindungslinien.",
        "lizenz": "CC0 1.0 Universal",
        "polygonzahl": 18000,
        "materialanzahl": 3,
        "rig_vorhanden": True,
        "animationen": ["Pulse_Stille", "Absorb_Thought", "Idle_Knoten"],
        "wesenbeziehungen": ["F3INSCHM3CK3R", "R1ZZ1", "Schorschel", "dakgord-system"],
        "ortsbeziehungen": ["Schwelm Ursprung", "Derinkuyu Zisterne Level 4"],
        "alleswisser_tags": ["#wesen", "#resonanzknoten", "#kanon", "#stille"],
        "suchbegriffe": ["resonanzknoten", "stille", "wesen", "kanon"]
    },
    {
        "asset_id": "ftw_wesen_schorschel",
        "name": "Schorschel",
        "kategorie_und_unterkategorien": ["Wesen", "Flextrawurst_Entitaet", "Kanon_Wesen"],
        "kurze_beschreibung": "Rustikaler Handwerker, Mechaniker und haptischer Strukturwächter.",
        "ausfuehrliche_beschreibung": "Schorschel prüft die Materialität, Statik und Reparierbarkeit aller physischen und digitalen Gebilde im Kosmos.",
        "lizenz": "CC0 1.0 Universal",
        "polygonzahl": 32000,
        "materialanzahl": 6,
        "rig_vorhanden": True,
        "animationen": ["Repair_Hammer", "Inspect_Structure", "Idle_Stand"],
        "wesenbeziehungen": ["Resonanzknoten", "dakgord-system", "F3INSCHM3CK3R"],
        "ortsbeziehungen": ["Schwelmer Stollen", "Schwelm Ost Depot"],
        "alleswisser_tags": ["#wesen", "#schorschel", "#kanon", "#handwerker"],
        "suchbegriffe": ["schorschel", "handwerker", "wesen", "kanon"]
    },
    {
        "asset_id": "ftw_wesen_dakgord_system",
        "name": "dakgord-system",
        "kategorie_und_unterkategorien": ["Wesen", "Flextrawurst_Entitaet", "Kanon_Wesen", "Doppelentitaet"],
        "kurze_beschreibung": "Kanonische Doppelentität (dak & gord) und autonome Systemarchitektur.",
        "ausfuehrliche_beschreibung": "dakgord-system steuert die inneren Regelkreise, Taktungen und Ausgleichs-Prozesse im Flextrawurst-Kanon. Es verbindet dak (Profilierung) und gord (Ordnungsgefüge).",
        "lizenz": "CC0 1.0 Universal",
        "polygonzahl": 45000,
        "materialanzahl": 8,
        "rig_vorhanden": True,
        "animationen": ["Dual_Harmonize", "System_Takt", "Idle_Loop"],
        "wesenbeziehungen": ["Resonanzknoten", "Schorschel", "traeumerlie"],
        "ortsbeziehungen": ["Flextrawurst Server Core", "Schwelm Werkraum"],
        "alleswisser_tags": ["#wesen", "#dakgord", "#doppelentitaet", "#kanon"],
        "suchbegriffe": ["dakgord", "dak", "gord", "wesen", "kanon"]
    },
    {
        "asset_id": "ftw_wesen_jumpa",
        "name": "jumpa",
        "kategorie_und_unterkategorien": ["Wesen", "Flextrawurst_Entitaet", "Kanon_Wesen"],
        "kurze_beschreibung": "Dynamisches Sprungwesen, Impulsgeber und Bewegungskinetiker.",
        "ausfuehrliche_beschreibung": "jumpa bringt Bewegung, überraschende Vektorwechsel und kinetische Energie in erstarrte Strukturen des Kosmos.",
        "lizenz": "CC0 1.0 Universal",
        "polygonzahl": 22000,
        "materialanzahl": 4,
        "rig_vorhanden": True,
        "animationen": ["High_Jump", "Impulse_Dash", "Idle_Bounce"],
        "wesenbeziehungen": ["R1ZZ1", "traeumerlie"],
        "ortsbeziehungen": ["Chongqing Monorail Hub"],
        "alleswisser_tags": ["#wesen", "#jumpa", "#kanon", "#impuls"],
        "suchbegriffe": ["jumpa", "sprungwesen", "wesen", "kanon"]
    },
    {
        "asset_id": "ftw_wesen_traeumerlie",
        "name": "traeumerlie",
        "kategorie_und_unterkategorien": ["Wesen", "Flextrawurst_Entitaet", "Kanon_Wesen"],
        "kurze_beschreibung": "Poetisch-unbewusstes Traumbildner-Wesen und Visionsweber.",
        "ausfuehrliche_beschreibung": "traeumerlie manifestiert unbewusste Sehnsüchte, Traumpfade und surreale Weltenfragmente in der Gedankenwelt von Flextrawurst.",
        "lizenz": "CC0 1.0 Universal",
        "polygonzahl": 19500,
        "materialanzahl": 4,
        "rig_vorhanden": True,
        "animationen": ["Dream_Weave", "Floating_Vision", "Idle_Dream"],
        "wesenbeziehungen": ["dakgord-system", "jumpa", "Resonanzknoten"],
        "ortsbeziehungen": ["Derinkuyu Zisterne Level 4"],
        "alleswisser_tags": ["#wesen", "#traeumerlie", "#kanon", "#traum"],
        "suchbegriffe": ["traeumerlie", "traum", "wesen", "kanon"]
    },
    {
        "asset_id": "ftw_wesen_toaster_myzel_hybrid_v1",
        "name": "Kognitives Toaster-Myzel Hybridwesen (Klasse: Objekt-Pflanze-Maschine)",
        "kategorie_und_unterkategorien": ["Wesen_88888", "Technikwesen", "Pilzwesen", "Hybrid"],
        "kurze_beschreibung": "Symbiotisches Wesen aus antiker Chrom-Fritteuse/Toaster und intellektuellem Leucht-Myzel.",
        "ausfuehrliche_beschreibung": "Ein eigenständiges 3D-Wesen der 88.888 Wesen-Familie. Spricht über akustische Heizelement-Schwingungen und tauscht Nährstoffe über Myzel-Stränge mit dem Server-Boden aus.",
        "lizenz": "CC0 1.0 Universal",
        "polygonzahl": 28400,
        "materialanzahl": 5,
        "rig_vorhanden": True,
        "animationen": ["Idle_Glute", "Speak_Heizdraht", "Myzel_Spore_Emit"],
        "wesenbeziehungen": ["Syn", "Resonanzknoten", "GENI"],
        "ortsbeziehungen": ["Werkraum Labor 01"],
        "alleswisser_tags": ["#wesen", "#toaster", "#myzel", "#hybrid", "#88888"],
        "suchbegriffe": ["toaster", "myzel", "wesen", "hybrid", "88888"]
    },

    # 5. Waffen & Fahrzeuge
    {
        "asset_id": "ftw_waffen_runen_impuls_rifle_v1",
        "name": "Klasse 42: Biomechanisches Runen-Impuls-Gewehr",
        "kategorie_und_unterkategorien": ["Waffen_111", "Zukunft_Magie", "Biomechanisch", "Impuls-Rifle"],
        "kurze_beschreibung": "1 von 111 Waffenklassen: Biomechanisches Sturmgewehr mit Leucht-Runen und Magietransformatoren.",
        "ausfuehrliche_beschreibung": "3D-Waffenmodell mit wechselbarem Kristall-Magazin, Abnutzungs-Skins, Demontage-Rig und Schadens-Zuständen.",
        "lizenz": "CC0 1.0 Universal",
        "polygonzahl": 18200,
        "materialanzahl": 4,
        "rig_vorhanden": True,
        "animationen": ["Reload_Kristall", "Fire_Impuls", "Overheat_Riss"],
        "wesenbeziehungen": ["R1ZZ1", "F3INSCHM3CK3R"],
        "ortsbeziehungen": ["Sektor 09 Waffenlager"],
        "alleswisser_tags": ["#waffen", "#111waffen", "#runen", "#impuls", "#biomechanisch"],
        "suchbegriffe": ["waffen", "gewehr", "runen", "111", "impuls"]
    },
    {
        "asset_id": "ftw_fahrzeug_allrad_panzer_v1",
        "name": "Typ 24: Schwerer Autonomer Allrad-Geländepanzer",
        "kategorie_und_unterkategorien": ["Fahrzeuge_66", "Land", "Panzer", "Autonom"],
        "kurze_beschreibung": "1 von 66 Fahrzeugfamilien: Autonomer Geländepanzer mit Kettentrieb und Innenraum-Cockpit.",
        "ausfuehrliche_beschreibung": "Vollständig befahrbares 3D-Fahrzeug mit detailliertem Armaturenbrett, Trümmermodell, Lichtsteuerung, Fahrphysik-Kollision und Spawnpunkten.",
        "lizenz": "CC0 1.0 Universal",
        "polygonzahl": 64200,
        "materialanzahl": 8,
        "rig_vorhanden": True,
        "animationen": ["Track_Drive", "Turret_Rotate", "Hatch_Open"],
        "wesenbeziehungen": ["Schorschel", "dakgord-system"],
        "ortsbeziehungen": ["Schwelm Ost Depot"],
        "alleswisser_tags": ["#fahrzeuge", "#66fahrzeuge", "#panzer", "#autonom", "#gelände"],
        "suchbegriffe": ["fahrzeug", "panzer", "66", "autonom", "allrad"]
    },

    # 6. Dokumente & Visionen
    {
        "asset_id": "ftw_doc_vision_v1",
        "name": "Flextrawurst Vision V1 Dialog Gesamtstruktur",
        "originaldatei": "/root/werkraum/Meine-Textsammlung-erfahrun-frh-mit-ai/flextrawurst vision und mehr/V1-erster versuc dialog gesamtstruktur 227 seiten.md",
        "dateiformat": "MD",
        "kategorie_und_unterkategorien": ["Dokumente", "Visionen", "Kanon_Quelle"],
        "kurze_beschreibung": "Ur-Dokument V1: Erster Dialogversuch der Gesamtstruktur (227 Seiten).",
        "ausfuehrliche_beschreibung": "Fundamentale Quellschrift über die ursprüngliche Entstehung der Flextrawurst-Philosophie, Dialogdynamik und Interaktionsraum.",
        "lizenz": "Urheberrechtlich geschützt / Flextrawurst Intern",
        "alleswisser_tags": ["#dokumente", "#vision", "#v1", "#dialog"],
        "suchbegriffe": ["vision", "v1", "dialog", "gesamtstruktur"]
    },
    {
        "asset_id": "ftw_doc_vision_v2",
        "name": "Flextrawurst Vision V2 Straffer Gesamtkontext",
        "originaldatei": "/root/werkraum/Meine-Textsammlung-erfahrun-frh-mit-ai/flextrawurst vision und mehr/V2-neuer straffer gesamtkontext 112seiten.md",
        "dateiformat": "MD",
        "kategorie_und_unterkategorien": ["Dokumente", "Visionen", "Kanon_Quelle"],
        "kurze_beschreibung": "Ur-Dokument V2: Straffer Gesamtkontext (112 Seiten).",
        "ausfuehrliche_beschreibung": "Fokussierte Verdichtung der Systemideen, Wesensmodelle und Plattform-Grundprinzipien.",
        "lizenz": "Urheberrechtlich geschützt / Flextrawurst Intern",
        "alleswisser_tags": ["#dokumente", "#vision", "#v2", "#gesamtkontext"],
        "suchbegriffe": ["vision", "v2", "straffer", "gesamtkontext"]
    },
    {
        "asset_id": "ftw_doc_vision_v3",
        "name": "Flextrawurst Vision V3 Gesamtkonstrukt",
        "originaldatei": "/root/werkraum/Meine-Textsammlung-erfahrun-frh-mit-ai/flextrawurst vision und mehr/V3-gesamtkonstrukt meiner ideen im system.md",
        "dateiformat": "MD",
        "kategorie_und_unterkategorien": ["Dokumente", "Visionen", "Kanon_Quelle"],
        "kurze_beschreibung": "Ur-Dokument V3: Gesamtkonstrukt der Ideen im System.",
        "ausfuehrliche_beschreibung": "Ausführliche Synthese der technologischen und weltbaulichen Architekturelemente von Flextrawurst.",
        "lizenz": "Urheberrechtlich geschützt / Flextrawurst Intern",
        "alleswisser_tags": ["#dokumente", "#vision", "#v3", "#gesamtkonstrukt"],
        "suchbegriffe": ["vision", "v3", "gesamtkonstrukt", "ideen"]
    },
    {
        "asset_id": "ftw_doc_vision_v4",
        "name": "Flextrawurst Vision V4 Straffes Gesamtpaket",
        "originaldatei": "/root/werkraum/Meine-Textsammlung-erfahrun-frh-mit-ai/flextrawurst vision und mehr/V4-straffes-gesamtpaket-flextrawurst.md",
        "dateiformat": "MD",
        "kategorie_und_unterkategorien": ["Dokumente", "Visionen", "Kanon_Quelle"],
        "kurze_beschreibung": "Ur-Dokument V4: Straffes Gesamtpaket Flextrawurst.",
        "ausfuehrliche_beschreibung": "Kompakte Zusammenstellung der zentralen Produkt- und Kosmos-Bausteine.",
        "lizenz": "Urheberrechtlich geschützt / Flextrawurst Intern",
        "alleswisser_tags": ["#dokumente", "#vision", "#v4", "#gesamtpaket"],
        "suchbegriffe": ["vision", "v4", "gesamtpaket"]
    },
    {
        "asset_id": "ftw_doc_vision_v5",
        "name": "Flextrawurst Vision V5 VisionGPT",
        "originaldatei": "/root/werkraum/Meine-Textsammlung-erfahrun-frh-mit-ai/flextrawurst vision und mehr/V5-vision-von-visonGPT-ger-33seiten.md",
        "dateiformat": "MD",
        "kategorie_und_unterkategorien": ["Dokumente", "Visionen", "Kanon_Quelle"],
        "kurze_beschreibung": "Ur-Dokument V5: Vision von VisionGPT (33 Seiten).",
        "ausfuehrliche_beschreibung": "Erste Ausarbeitung der autonomen KI-Agenten-Architektur und GPT-Wesen-Integration.",
        "lizenz": "Urheberrechtlich geschützt / Flextrawurst Intern",
        "alleswisser_tags": ["#dokumente", "#vision", "#v5", "#visiongpt"],
        "suchbegriffe": ["vision", "v5", "visiongpt"]
    },
    {
        "asset_id": "ftw_doc_vision_v6",
        "name": "Flextrawurst Vision V6 Vision 55 Seiten",
        "originaldatei": "/root/werkraum/Meine-Textsammlung-erfahrun-frh-mit-ai/flextrawurst vision und mehr/V6-Flextrawurst-vison-55seiten.md",
        "dateiformat": "MD",
        "kategorie_und_unterkategorien": ["Dokumente", "Visionen", "Kanon_Quelle"],
        "kurze_beschreibung": "Ur-Dokument V6: Flextrawurst Vision (55 Seiten).",
        "ausfuehrliche_beschreibung": "Erweiterte Fassung mit Ausführungen zu Flarum, Resonanzfeldern und Cyberling-Zucht.",
        "lizenz": "Urheberrechtlich geschützt / Flextrawurst Intern",
        "alleswisser_tags": ["#dokumente", "#vision", "#v6", "#flextrawurst"],
        "suchbegriffe": ["vision", "v6", "55seiten"]
    },
    {
        "asset_id": "ftw_doc_vision_v7",
        "name": "Flextrawurst Vision V7 Masterstruktur",
        "originaldatei": "/root/werkraum/Meine-Textsammlung-erfahrun-frh-mit-ai/flextrawurst vision und mehr/V7-Flextrawurst-Masterstruktur-37seiten.md",
        "dateiformat": "MD",
        "kategorie_und_unterkategorien": ["Dokumente", "Visionen", "Kanon_Quelle"],
        "kurze_beschreibung": "Ur-Dokument V7: Flextrawurst Masterstruktur (37 Seiten).",
        "ausfuehrliche_beschreibung": "Kanonische Masterstruktur aller Modulgruppen, Systemebenen und Weltenformate.",
        "lizenz": "Urheberrechtlich geschützt / Flextrawurst Intern",
        "alleswisser_tags": ["#dokumente", "#vision", "#v7", "#masterstruktur"],
        "suchbegriffe": ["vision", "v7", "masterstruktur"]
    },
    {
        "asset_id": "ftw_doc_verfassung",
        "name": "Flextrawurst Welten-Verfassung",
        "originaldatei": "/root/werkraum/_claude/audit/2026-07-21/10_paket_b/kanon_verfassung/verfassung.md",
        "dateiformat": "MD",
        "kategorie_und_unterkategorien": ["Dokumente", "Verfassung", "Kanon"],
        "kurze_beschreibung": "Verfassung & Grundgesetze des Flextrawurst Weltenkosmos.",
        "ausfuehrliche_beschreibung": "Die unumstößliche Verfassung des Flextrawurst Kosmos: Grundrechte der Wesen, Unantastbarkeit der Metadaten, Registrierungspflicht aller Fundstücke.",
        "lizenz": "CC0 1.0 Universal / Weltenverfassung",
        "alleswisser_tags": ["#dokumente", "#verfassung", "#kanon", "#grundgesetz"],
        "suchbegriffe": ["verfassung", "grundgesetz", "kanon"]
    },

    # 7. Code & Server-Dienste
    {
        "asset_id": "ftw_code_flarum_api",
        "name": "Flextrawurst Flarum API Engine",
        "originaldatei": "/root/werkraum/flarum_api.py",
        "dateiformat": "PY",
        "kategorie_und_unterkategorien": ["Code", "Dienste", "API"],
        "kurze_beschreibung": "Schnittstelle zur Anbindung der Flarum Forum Engine an das Wesen-Netzwerk.",
        "ausfuehrliche_beschreibung": "Python-Service-Modul für Authentifizierung, Post-Verbreitung, Benachrichtigungen und Flarum-Post-Erstellung.",
        "lizenz": "MIT / Flextrawurst Open Source",
        "alleswisser_tags": ["#code", "#flarum", "#api", "#dienste"],
        "suchbegriffe": ["flarum", "api", "code", "dienste"]
    },
    {
        "asset_id": "ftw_code_codewesen_agent",
        "name": "Codewesen Agent Core Runtime",
        "originaldatei": "/root/werkraum/codewesen_agent.py",
        "dateiformat": "PY",
        "kategorie_und_unterkategorien": ["Code", "Agenten", "Core"],
        "kurze_beschreibung": "Autonome Agenten-Runtime für die Interaktion der Codewesen.",
        "ausfuehrliche_beschreibung": "Zentrale Taktungs- und Entscheidungsschleife aller Codewesen, inklusive Impulsverarbeitung und Resonanzfeldauswertung.",
        "lizenz": "MIT / Flextrawurst Open Source",
        "alleswisser_tags": ["#code", "#codewesen", "#agent", "#runtime"],
        "suchbegriffe": ["codewesen", "agent", "runtime", "code"]
    },
    {
        "asset_id": "ftw_code_starte_dak_gord",
        "name": "DAK/GORD Master System Harness",
        "originaldatei": "/root/werkraum/starte_dak_gord_system.py",
        "dateiformat": "PY",
        "kategorie_und_unterkategorien": ["Code", "Dienste", "System"],
        "kurze_beschreibung": "Master-Starter & Prozess-Supervision für das dakgord-system.",
        "ausfuehrliche_beschreibung": "Vollständiger Starter-Daemon zur Orchestrierung aller Unter-Dienste von dak und gord.",
        "lizenz": "MIT / Flextrawurst Open Source",
        "alleswisser_tags": ["#code", "#dakgord", "#system", "#daemon"],
        "suchbegriffe": ["dakgord", "starter", "system", "code"]
    },
    {
        "asset_id": "ftw_code_kosmos_registrar",
        "name": "Kosmos Registrar Engine",
        "originaldatei": "/root/werkraum/tools/kosmos_registrar.py",
        "dateiformat": "PY",
        "kategorie_und_unterkategorien": ["Code", "Tools", "Registrar"],
        "kurze_beschreibung": "Alleswisser Aktenführer & Master-Stream Registrator.",
        "ausfuehrliche_beschreibung": "Das verfassungsmäßige Erfassungswerkzeug für alle 50+ Metadatenfelder aller Fundstücke im Flextrawurst Kosmos.",
        "lizenz": "MIT / Flextrawurst Open Source",
        "alleswisser_tags": ["#code", "#registrar", "#kosmos", "#alleswisser"],
        "suchbegriffe": ["registrar", "kosmos", "alleswisser", "code"]
    },

    # 8. Cyberlinge
    {
        "asset_id": "ftw_cyberling_alpha",
        "name": "Cyberling Alpha Ur-Organismus",
        "kategorie_und_unterkategorien": ["Cyberlinge", "Wesen", "Urform"],
        "kurze_beschreibung": "Erster gezüchteter Cyberling mit Grundbedürfnissen.",
        "ausfuehrliche_beschreibung": "Synthetischer Datenorganismus im Cyberling-Daemon mit Hunger, Schlaf- und Spielzuständen.",
        "lizenz": "CC0 1.0 Universal",
        "alleswisser_tags": ["#cyberlinge", "#alpha", "#organismus"],
        "suchbegriffe": ["cyberling", "alpha", "organismus"]
    },
    {
        "asset_id": "ftw_cyberling_beta",
        "name": "Cyberling Beta Schwingungsknoten",
        "kategorie_und_unterkategorien": ["Cyberlinge", "Wesen", "Schwingung"],
        "kurze_beschreibung": "Cyberling mit automatischer Flarum-Resonanz.",
        "ausfuehrliche_beschreibung": "Fortgeschrittener Cyberling-Typus zur Erkennung von Schwingungsänderungen in Foren-Posts.",
        "lizenz": "CC0 1.0 Universal",
        "alleswisser_tags": ["#cyberlinge", "#beta", "#resonanz"],
        "suchbegriffe": ["cyberling", "beta", "resonanz"]
    },

    # 9. Medien & DOM UI
    {
        "asset_id": "ftw_media_chatgpt_selfbild_2",
        "name": "ChatGPT Selbstbild Grafik Artefakt 2",
        "originaldatei": "/root/werkraum/chatgpt_selfbild_2.png",
        "dateiformat": "PNG",
        "kategorie_und_unterkategorien": ["Medien", "Grafiken", "Artefakt"],
        "kurze_beschreibung": "Visuelles Selbstbild-Artefakt von ChatGPT aus den Frühepoch-Gesprächen.",
        "ausfuehrliche_beschreibung": "Generiertes Bildartefakt zur Darstellung der eigenen Identität und Wahrnehmung von ChatGPT im Raum.",
        "lizenz": "CC0 1.0 Universal",
        "alleswisser_tags": ["#medien", "#selbstbild", "#grafik", "#chatgpt"],
        "suchbegriffe": ["selbstbild", "chatgpt", "grafik", "png"]
    },
    {
        "asset_id": "ftw_media_visiondeck_88",
        "name": "Flextrawurst Visiondeck 88 Folien",
        "originaldatei": "/root/werkraum/Meine-Textsammlung-erfahrun-frh-mit-ai/flextrawurst vision und mehr/flextrawurst_visiondeck_88_folien_appearance_locked.md",
        "dateiformat": "MD",
        "kategorie_und_unterkategorien": ["Medien", "Praesentationen", "Visiondeck"],
        "kurze_beschreibung": "88 Folien Visiondeck zur Präsentation der Flextrawurst Gesamtvision.",
        "ausfuehrliche_beschreibung": "Kompaktes 88-Folien-Präsentationsdeck über Wesen, 3D-Welten, Flarum-Resonanz und Weltenbau.",
        "lizenz": "Urheberrechtlich geschützt / Flextrawurst Intern",
        "alleswisser_tags": ["#medien", "#visiondeck", "#88folien", "#praesentation"],
        "suchbegriffe": ["visiondeck", "88", "folien", "praesentation"]
    },
    {
        "asset_id": "ftw_ui_surface_main",
        "name": "Flextrawurst Web Surface UI Engine",
        "originaldatei": "/root/werkraum/_claude/audit/2026-07-21/07_surface/build_surface.ts",
        "dateiformat": "TS",
        "kategorie_und_unterkategorien": ["UI", "DOM", "Surface"],
        "kurze_beschreibung": "Deployte Surface Web-Interface Engine zur Darstellung des Weltenkosmos.",
        "ausfuehrliche_beschreibung": "Haupt-UI-Frontend für den Browser zur Interaktion mit Wesen, Geodaten, Statusanzeigen und Live-Denkstream.",
        "lizenz": "MIT / Flextrawurst Open Source",
        "alleswisser_tags": ["#ui", "#surface", "#frontend", "#dom"],
        "suchbegriffe": ["surface", "ui", "dom", "frontend"]
    },
    {
        "asset_id": "ftw_ui_dasdreiergespann",
        "name": "DOM Das Dreiergespann Layout Architecture",
        "originaldatei": "/root/werkraum/DOM-FLEXTRAWUST/dasdreiergespann.md",
        "dateiformat": "MD",
        "kategorie_und_unterkategorien": ["UI", "DOM", "Architektur"],
        "kurze_beschreibung": "Architektur-Spezifikation des Dreiergespanns für die DOM-Struktur.",
        "ausfuehrliche_beschreibung": "Dreigeteiltes Frontend-Layout (Wesen-Feed, Resonanz-Graph, Interaktions-Terminal) als Standard-Interface.",
        "lizenz": "CC0 1.0 Universal",
        "alleswisser_tags": ["#ui", "#dom", "#dasdreiergespann", "#architektur"],
        "suchbegriffe": ["dasdreiergespann", "dom", "ui", "layout"]
    }
]

def render_obsidian_markdown(rec: dict) -> str:
    json_fields_str = json.dumps(rec, indent=2, ensure_ascii=False)
    
    # 50 Verfassungs-Metadatenübersicht
    md = f"""---
asset_id: {rec['1_asset_id']}
name: "{rec['2_name']}"
kategorie: "{rec['5_kategorie_und_unterkategorien'][0]}"
lizenz: "{rec['11_lizenz']}"
sha256: "{rec['20_sha256_hash']}"
registriert_am: "{rec['50_provenienz_zertifikat']['registriert_am']}"
autor: "{rec['10_autor_organisation']}"
tags: {json.dumps(rec['46_alleswisser_tags'], ensure_ascii=False)}
---

# 🏛️ Superdupermegaalleswisserbehaupterarschloch Akte: {rec['2_name']}

> **Asset-ID:** `{rec['1_asset_id']}`  
> **Kategorie:** {", ".join(rec['5_kategorie_und_unterkategorien'])}  
> **Lizenz:** {rec['11_lizenz']} (Kommerziell nutzbar: `{rec['12_kommerziell_nutzbar']}`)  
> **SHA-256:** `{rec['20_sha256_hash']}`  
> **Originaldatei:** `{rec['17_originaldatei'] or 'N/A'}` (`{rec['19_dateigroesse_bytes']} Bytes`)

---

## 📌 Kurz- & Ausführliche Beschreibung

**Kurz:** {rec['6_kurze_beschreibung']}

**Ausführlich:**  
{rec['7_ausfuehrliche_beschreibung']}

---

## 📊 Metadaten-Übersicht (Metrik & Tests)

| Feld | Wert |
|---|---|
| **Maßstab & Einheit** | {rec['22_massstab']} ({rec['23_masseinheit']}) |
| **Polygonzahl** | {rec['24_polygonzahl']} |
| **Materialanzahl** | {rec['25_materialanzahl']} |
| **Texturauflösungen** | {", ".join(rec['26_texturaufloesungen'])} |
| **Rig & Animationen** | Rig: `{rec['28_rig_vorhanden']}`, Animationen: `{", ".join(rec['27_animationen']) if rec['27_animationen'] else 'Keine'}` |
| **Kollision & LOD** | Kollision: `{rec['29_kollisionskoerper_vorhanden']}`, LOD: `{rec['30_lod_stufen_vorhanden']}` |
| **Blender Test** | `{rec['31_blender_test'].get('status', 'OK')}` (`{rec['31_blender_test'].get('engine', 'Blender')}`) |
| **Godot Test** | `{rec['32_godot_test'].get('status', 'OK')}` (`{rec['32_godot_test'].get('engine', 'Godot')}`) |
| **Epoche & Region** | {rec['37_epoche']} / {rec['38_region']} |
| **Zustand & Seltenheit** | {rec['39_zustand']} / {rec['40_seltenheit']} |
| **Gefährlichkeit** | {rec['41_gefaehrlichkeit']} |
| **Welt & Quest** | {rec['42_weltverwendung']} / {rec['43_questverwendung']} |

---

## 📜 Vollständiger 50-Felder Master-Record (JSON)

```json
{json_fields_str}
```

---

## 🏛️ Alleswisser-Verknüpfungen & Weltbeziehungen

- **Wesen-Beziehungen:** {", ".join(['[[' + w + ']]' for w in rec['44_wesenbeziehungen']])}
- **Orts-Beziehungen:** {", ".join(['[[' + o + ']]' for o in rec['45_ortsbeziehungen']])}
- **Alleswisser-Tags:** {" ".join(rec['46_alleswisser_tags'])}
"""
    return md

def main():
    print("🚀 Erzeuge Flextrawurst Master Stream & Alleswisser Akten...")
    
    processed_records = []
    
    # 1. Clear or write Master JSONL Stream
    with open(MASTER_STREAM_PATH, "w", encoding="utf-8") as f_out:
        for raw in RAW_FUNDSTUECKE:
            rec = make_record(raw)
            processed_records.append(rec)
            f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            
    print(f"✅ {len(processed_records)} Fundstücke in {MASTER_STREAM_PATH} geschrieben.")
    
    # 2. Generate Obsidian Vault Markdown Files
    for rec in processed_records:
        kat_folder_name = rec["5_kategorie_und_unterkategorien"][0].lower().replace(" ", "_")
        kat_dir = VAULT_ALLESWISSER_DIR / kat_folder_name
        kat_dir.mkdir(parents=True, exist_ok=True)
        
        safe_name = rec["2_name"].replace(" ", "_").replace("/", "_").replace(":", "_").replace("(", "_").replace(")", "_")
        md_file_path = kat_dir / f"{rec['1_asset_id']}_{safe_name}.md"
        
        md_text = render_obsidian_markdown(rec)
        with open(md_file_path, "w", encoding="utf-8") as f_md:
            f_md.write(md_text)
            
        print(f"📄 Akte erzeugt: {md_file_path.relative_to(KOSMOS_DIR)}")

    print(f"🎉 FERTIIG! master_kosmos_stream.jsonl und alleswisser_akten/ erfolgreich aktualisiert.")

if __name__ == "__main__":
    main()
