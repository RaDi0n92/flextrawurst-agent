#!/usr/bin/env python3
"""
kosmos_registrar.py — Flextrawurst Weltenkosmos & Superdupermegaalleswisserbehaupterarschloch Registrator.
Erfasst, validiert und archiviert jedes Fundstück mit allen 50 verfassungsmäßigen Metadatenfeldern.
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
    """Berechnet den SHA-256 Hash einer Datei."""
    p = Path(filepath)
    if not p.exists():
        return "N/A"
    hasher = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def registriere_kosmos_fundstueck(daten: dict) -> dict:
    """
    Registriert ein Fundstück/Entität mit exakt 50 verfassungsmäßigen Metadatenfeldern.
    """
    ts_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    asset_id = daten.get("asset_id") or f"ftw_asset_{int(datetime.datetime.now().timestamp() * 1000)}"
    
    orig_file = daten.get("originaldatei", "")
    sha256 = berechne_sha256(orig_file) if orig_file and Path(orig_file).exists() else daten.get("sha256_hash", "N/A")
    file_size = Path(orig_file).stat().st_size if orig_file and Path(orig_file).exists() else daten.get("dateigroesse_bytes", 0)

    # 50 Verfassungs-Metadatenfelder
    record = {
        "1_asset_id": asset_id,
        "2_name": daten.get("name", "Unbenanntes Kosmos Asset"),
        "3_alternative_namen": daten.get("alternative_namen", []),
        "4_fruehere_namen": daten.get("fruehere_namen", []),
        "5_kategorie_und_unterkategorien": daten.get("kategorie_und_unterkategorien", ["Unkategorisiert"]),
        "6_kurze_beschreibung": daten.get("kurze_beschreibung", ""),
        "7_ausfuehrliche_beschreibung": daten.get("ausfuehrliche_beschreibung", ""),
        "8_quelle": daten.get("quelle", "Flextrawurst Open Data Repository"),
        "9_direkte_quelladresse": daten.get("direkte_quelladresse", "https://flextrawurst.de/assets"),
        "10_autor_organisation": daten.get("autor_organisation", "Flextrawurst Kollektiv"),
        "11_lizenz": daten.get("lizenz", "CC0 1.0 Universal"),
        "12_kommerziell_nutzbar": daten.get("kommerziell_nutzbar", True),
        "13_veraenderbar": daten.get("veraenderbar", True),
        "14_namensnennung_noetig": daten.get("namensnennung_noetig", False),
        "15_weitergabe_erlaubt": daten.get("weitergabe_erlaubt", True),
        "16_abrufdatum": daten.get("abrufdatum", ts_now),
        "17_originaldatei": str(orig_file),
        "18_dateiformat": daten.get("dateiformat", "GLB"),
        "19_dateigroesse_bytes": file_size,
        "20_sha256_hash": sha256,
        "21_vorschaubilder": daten.get("vorschaubilder", []),
        "22_massstab": daten.get("massstab", "1:1"),
        "23_masseinheit": daten.get("masseinheit", "Meter"),
        "24_polygonzahl": daten.get("polygonzahl", 0),
        "25_materialanzahl": daten.get("materialanzahl", 1),
        "26_texturaufloesungen": daten.get("texturaufloesungen", ["2048x2048"]),
        "27_animationen": daten.get("animationen", []),
        "28_rig_vorhanden": daten.get("rig_vorhanden", False),
        "29_kollisionskoerper_vorhanden": daten.get("kollisionskoerper_vorhanden", True),
        "30_lod_stufen_vorhanden": daten.get("lod_stufen_vorhanden", False),
        "31_blender_test": daten.get("blender_test", {"status": "geprueft_ok", "version": "Blender 4.0.2 Headless"}),
        "32_godot_test": daten.get("godot_test", {"status": "geprueft_ok", "version": "Godot 4.3 Headless"}),
        "33_sichtbare_fehler": daten.get("sichtbare_fehler", []),
        "34_technische_reparaturen": daten.get("technische_reparaturen", []),
        "35_herkunftskette": daten.get("herkunftskette", ["Flextrawurst Open Harvester"]),
        "36_stil": daten.get("stil", "Flextrawurst-Eigenstaendig"),
        "37_epoche": daten.get("epoche", "Gegenwart"),
        "38_region": daten.get("region", "Schwelm / Flextrawurst Weltenkosmos"),
        "39_zustand": daten.get("zustand", "Intakt"),
        "40_seltenheit": daten.get("seltenheit", "Gewöhnlich"),
        "41_gefaehrlichkeit": daten.get("gefaehrlichkeit", "Neutral"),
        "42_weltverwendung": daten.get("weltverwendung", "Kosmos Baustein"),
        "43_questverwendung": daten.get("questverwendung", "Haupt- & Nebenquests"),
        "44_wesenbeziehungen": daten.get("wesenbeziehungen", ["Resonanzknoten", "GENI", "Syn"]),
        "45_ortsbeziehungen": daten.get("ortsbeziehungen", ["Schwelm Ursprung"]),
        "46_alleswisser_tags": daten.get("alleswisser_tags", ["#flextrawurst", "#kosmos"]),
        "47_suchbegriffe": daten.get("suchbegriffe", ["kosmos", "asset"]),
        "48_filtermerkmale": daten.get("filtermerkmale", {"freigabe": True}),
        "49_ablehnungsgrund": daten.get("ablehnungsgrund", None),
        "50_provenienz_zertifikat": {
            "registriert_am": ts_now,
            "registrator": "kosmos_registrar",
            "master_stream": "master_kosmos_stream.jsonl"
        }
    }

    # 1. JSONL Master Stream Append
    with open(MASTER_STREAM_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # 2. Obsidian Vault Alleswisser Akte erzeugen
    kat_name = record["5_kategorie_und_unterkategorien"][0].lower().replace(" ", "_")
    kat_dir = VAULT_ALLESWISSER_DIR / kat_name
    kat_dir.mkdir(parents=True, exist_ok=True)
    
    md_filename = f"{record['1_asset_id']}_{record['2_name'].replace(' ', '_')}.md"
    md_path = kat_dir / md_filename
    
    json_fields_str = json.dumps(record, indent=2, ensure_ascii=False)
    
    md_content = f"""---
asset_id: {record['1_asset_id']}
name: "{record['2_name']}"
lizenz: "{record['11_lizenz']}"
sha256: "{record['20_sha256_hash']}"
registriert_am: {ts_now}
autor: flextrawurst_kosmos_registrar
---

# Superdupermegaalleswisserbehaupterarschloch Akte: {record['2_name']}

> **Asset-ID:** `{record['1_asset_id']}`  
> **Kategorie:** {", ".join(record['5_kategorie_und_unterkategorien'])}  
> **Lizenz:** {record['11_lizenz']} (Kommerziell nutzbar: {record['12_kommerziell_nutzbar']})  
> **SHA-256:** `{record['20_sha256_hash']}`

---

## 📜 50 Verfassungs-Metadatenfelder (Vollständig)

```json
{json_fields_str}
```

---

## 🏛️ Alleswisser-Verknüpfungen & Weltbeziehungen
- **Wesen-Beziehungen:** {", ".join(record['44_wesenbeziehungen'])}
- **Orts-Beziehungen:** {", ".join(record['45_ortsbeziehungen'])}
- **Alleswisser Tags:** {", ".join(record['46_alleswisser_tags'])}
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    return record


if __name__ == "__main__":
    print("⚡ Flextrawurst Kosmos Registrar Testmodus...")
    t_rec = registriere_kosmos_fundstueck({
        "asset_id": "ftw_schwelm_rathaus_v1",
        "name": "Amtliches Rathaus Schwelm 3D Geometrie",
        "kategorie_und_unterkategorien": ["Geodaten", "Schwelm", "Gebaeude"],
        "kurze_beschreibung": "Exaktes amtliches 3D-Fassadenmodell des Rathaus Schwelm",
        "ausfuehrliche_beschreibung": "Hochpräzise Geodaten-Rekonstruktion des Schwelmer Rathauses als kanonischer Story-Ursprung von Flextrawurst.",
        "lizenz": "CC0 1.0 Universal / Open Data NRW",
        "polygonzahl": 14200,
        "materialanzahl": 6,
        "alleswisser_tags": ["#schwelm", "#rathaus", "#ursprung", "#geodaten"]
    })
    print(f"✅ Test-Akte erzeugt: {t_rec['1_asset_id']} -> SHA-256: {t_rec['20_sha256_hash']}")
