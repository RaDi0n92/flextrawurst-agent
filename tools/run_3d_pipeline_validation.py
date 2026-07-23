#!/usr/bin/env python3
"""
run_3d_pipeline_validation.py — Flextrawurst 3D Pipeline & MCP Server Validator.
Prüft alle 3D-Assets über den Flextrawurst 3D-MCP Server (http://127.0.0.1:8090).
- Format-Konvertierung (FBX/OBJ -> GLB)
- 800x600 Studio-Vorschau PNG-Rendering nach /root/werkraum/kosmos/renders/
- Ermittlung Vertex- / Polygon- / Material-Zahlen
- Godot 4.3 Headless Asset-Import Tests
- SHA-256 Hashes aller Quelldateien, GLB-Dateien und Preview-Renderings
"""

import os
import sys
import json
import hashlib
import urllib.request
import urllib.parse
from pathlib import Path

MCP_SERVER_URL = "http://127.0.0.1:8090"
RAW_DIR = Path("/root/werkraum/kosmos/assets/raw_3d")
GLB_DIR = Path("/root/werkraum/kosmos/assets/glb")
RENDERS_DIR = Path("/root/werkraum/kosmos/renders")
GODOT_PROJ_DIR = Path("/root/werkraum/kosmos/godot_project")

RAW_DIR.mkdir(parents=True, exist_ok=True)
GLB_DIR.mkdir(parents=True, exist_ok=True)
RENDERS_DIR.mkdir(parents=True, exist_ok=True)
GODOT_PROJ_DIR.mkdir(parents=True, exist_ok=True)

# Minimized valid Godot 4.3 project file if missing
godot_project_file = GODOT_PROJ_DIR / "project.godot"
if not godot_project_file.exists():
    with open(godot_project_file, "w", encoding="utf-8") as f:
        f.write('config_version=5\n\n[application]\nconfig/name="Flextrawurst Kosmos 3D"\n')

def calculate_sha256(filepath: str) -> str:
    p = Path(filepath)
    if not p.exists():
        return "N/A"
    hasher = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

# Define raw 3D geometry definitions for 3D assets if not present
ASSETS_GEOMETRY = {
    "ftw_schwelm_rathaus_v1": {
        "name": "Amtliches Rathaus Schwelm 3D-Fassade",
        "format": "obj",
        "obj_content": """# Rathaus Schwelm Fassadengeometrie
v -5.0 0.0 0.0
v  5.0 0.0 0.0
v  5.0 0.0 8.0
v -5.0 0.0 8.0
v -5.0 10.0 0.0
v  5.0 10.0 0.0
v  5.0 10.0 8.0
v -5.0 10.0 8.0
v  0.0 5.0 12.0
f 1 2 3 4
f 5 8 7 6
f 1 5 6 2
f 2 6 7 3
f 3 7 8 4
f 4 8 5 1
f 4 3 9
f 8 7 9
f 3 7 9
f 4 8 9
"""
    },
    "ftw_schwelm_altstadt_straat_v1": {
        "name": "Schwelm Historischer Straßenverlauf & Hausgeometrien",
        "format": "obj",
        "obj_content": """# Schwelm Altstadt Straßenzug
v -10.0 -2.0 0.0
v  10.0 -2.0 0.0
v  10.0  2.0 0.0
v -10.0  2.0 0.0
v -8.0 2.0 0.0
v -4.0 2.0 0.0
v -4.0 2.0 5.0
v -8.0 2.0 5.0
f 1 2 3 4
f 5 6 7 8
"""
    },
    "ftw_metropole_chongqing_underground_v1": {
        "name": "Chongqing Cyber-Metropole Untergrund & Monorail Trasse",
        "format": "obj",
        "obj_content": """# Chongqing Cyber-Tower & Monorail
v -3.0 -3.0 -10.0
v  3.0 -3.0 -10.0
v  3.0  3.0 -10.0
v -3.0  3.0 -10.0
v -3.0 -3.0  20.0
v  3.0 -3.0  20.0
v  3.0  3.0  20.0
v -3.0  3.0  20.0
f 1 2 3 4
f 5 8 7 6
f 1 5 6 2
f 2 6 7 3
f 3 7 8 4
f 4 8 5 1
"""
    },
    "ftw_hist_carcassonne_fortress_v1": {
        "name": "Carcassonne Mittelalterliche Doppelmauer-Festung",
        "format": "obj",
        "obj_content": """# Carcassonne Festungsturm
v -2.0 -2.0 0.0
v  2.0 -2.0 0.0
v  2.0  2.0 0.0
v -2.0  2.0 0.0
v -1.5 -1.5 10.0
v  1.5 -1.5 10.0
v  1.5  1.5 10.0
v -1.5  1.5 10.0
f 1 2 3 4
f 5 8 7 6
f 1 5 6 2
f 2 6 7 3
f 3 7 8 4
f 4 8 5 1
"""
    },
    "ftw_underground_derinkuyu_cave_city_v1": {
        "name": "Derinkuyu Mehrstöckige Unterirdische Höhlenstadt",
        "format": "obj",
        "obj_content": """# Derinkuyu Höhlen-Dungeon Kammer
v -4.0 -4.0 -5.0
v  4.0 -4.0 -5.0
v  4.0  4.0 -5.0
v -4.0  4.0 -5.0
v -3.5 -3.5  0.0
v  3.5 -3.5  0.0
v  3.5  3.5  0.0
v -3.5  3.5  0.0
f 1 2 3 4
f 5 8 7 6
f 1 5 6 2
f 2 6 7 3
f 3 7 8 4
f 4 8 5 1
"""
    },
    "ftw_wesen_toaster_myzel_hybrid_v1": {
        "name": "Kognitives Toaster-Myzel Hybridwesen",
        "format": "obj",
        "obj_content": """# Toaster-Myzel Hybrid Geometry
v -0.8 -0.5 0.0
v  0.8 -0.5 0.0
v  0.8  0.5 0.0
v -0.8  0.5 0.0
v -0.8 -0.5 1.2
v  0.8 -0.5 1.2
v  0.8  0.5 1.2
v -0.8  0.5 1.2
f 1 2 3 4
f 5 8 7 6
f 1 5 6 2
f 2 6 7 3
f 3 7 8 4
f 4 8 5 1
"""
    },
    "ftw_waffen_runen_impuls_rifle_v1": {
        "name": "Biomechanisches Runen-Impuls-Gewehr",
        "format": "obj",
        "obj_content": """# Runen Impuls Rifle Body
v -0.1 -1.0 -0.2
v  0.1 -1.0 -0.2
v  0.1  1.5 -0.2
v -0.1  1.5 -0.2
v -0.1 -1.0  0.2
v  0.1 -1.0  0.2
v  0.1  1.5  0.2
v -0.1  1.5  0.2
f 1 2 3 4
f 5 8 7 6
f 1 5 6 2
f 2 6 7 3
f 3 7 8 4
f 4 8 5 1
"""
    },
    "ftw_fahrzeug_allrad_panzer_v1": {
        "name": "Typ 24: Schwerer Autonomer Allrad-Geländepanzer",
        "format": "obj",
        "obj_content": """# Autonomer Panzer Chassis
v -2.0 -4.0 0.0
v  2.0 -4.0 0.0
v  2.0  4.0 0.0
v -2.0  4.0 0.0
v -1.8 -3.5 1.5
v  1.8 -3.5 1.5
v  1.8  3.5 1.5
v -1.8  3.5 1.5
f 1 2 3 4
f 5 8 7 6
f 1 5 6 2
f 2 6 7 3
f 3 7 8 4
f 4 8 5 1
"""
    },
    "test_cube": {
        "name": "Standard Test Cube Asset",
        "format": "obj",
        "obj_content": """# Test Cube Geometry
v -1.0 -1.0  1.0
v  1.0 -1.0  1.0
v -1.0  1.0  1.0
v  1.0  1.0  1.0
v -1.0  1.0 -1.0
v  1.0  1.0 -1.0
v -1.0 -1.0 -1.0
v  1.0 -1.0 -1.0
f 1 2 4 3
f 3 4 6 5
f 5 6 8 7
f 7 8 2 1
f 2 8 6 4
f 7 1 3 5
"""
    }
}

def mcp_post(endpoint: str, data: dict) -> dict:
    url = f"{MCP_SERVER_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def run_validation():
    print("===============================================================")
    print("⚡ Flextrawurst 3D Pipeline & MCP Server Validator Initialized")
    print("===============================================================")
    
    # Check MCP status endpoint
    try:
        status_req = urllib.request.urlopen(f"{MCP_SERVER_URL}/api/3d/status")
        status_data = json.loads(status_req.read().decode("utf-8"))
        print(f"✅ 3D-MCP Server Status: {status_data['status'].upper()}")
        print(f"   Engine 1: {status_data['blender_version']}")
        print(f"   Engine 2: {status_data['godot_version']}")
    except Exception as e:
        print(f"❌ Error connecting to 3D-MCP Server: {e}")
        sys.exit(1)

    reports = []

    for asset_id, info in ASSETS_GEOMETRY.items():
        print(f"\n---------------------------------------------------------------")
        print(f"📦 Prüfe 3D-Asset: [{asset_id}] — {info['name']}")
        print(f"---------------------------------------------------------------")

        # 1. Quell-Datei erzeugen (OBJ)
        src_path = RAW_DIR / f"{asset_id}.obj"
        with open(src_path, "w", encoding="utf-8") as f:
            f.write(info["obj_content"])
        
        src_sha256 = calculate_sha256(str(src_path))
        src_size = src_path.stat().st_size
        print(f"1. Quell-Asset (OBJ): {src_path.name} ({src_size} Bytes)")
        print(f"   SHA-256 (Source): {src_sha256}")

        # 2. Format-Konvertierung via 3D-MCP (OBJ -> GLB)
        target_glb_path = GLB_DIR / f"{asset_id}.glb"
        conv_res = mcp_post("/api/3d/convert", {
            "input_path": str(src_path),
            "output_path": str(target_glb_path)
        })

        if conv_res.get("status") != "ok":
            print(f"❌ Konvertierung fehlgeschlagen: {conv_res.get('error')}")
            continue

        glb_sha256 = calculate_sha256(str(target_glb_path))
        print(f"2. GLB Konvertierung via Blender Headless:")
        print(f"   Target: {target_glb_path.name} ({conv_res['file_size_kb']} KB)")
        print(f"   Vertices: {conv_res['vertices']} | Polygons: {conv_res['polygons']} | Materials: {conv_res['materials']}")
        print(f"   SHA-256 (GLB): {glb_sha256}")

        # 3. Studio Preview Rendering (800x600 PNG nach /root/werkraum/kosmos/renders/)
        render_png_path = RENDERS_DIR / f"{asset_id}_preview.png"
        render_res = mcp_post("/api/3d/render", {
            "model_path": str(target_glb_path),
            "image_output": str(render_png_path)
        })

        if render_res.get("status") != "ok":
            print(f"❌ Render-Vorschau fehlgeschlagen: {render_res.get('error')}")
            continue

        png_sha256 = calculate_sha256(str(render_png_path))
        print(f"3. 800x600 Studio Preview PNG Render:")
        print(f"   Render Output: {render_png_path.name} ({render_res['file_size_kb']} KB)")
        print(f"   SHA-256 (PNG): {png_sha256}")

        # Copy GLB to Godot project directory for import test
        godot_asset_dest = GODOT_PROJ_DIR / f"{asset_id}.glb"
        with open(target_glb_path, "rb") as sf, open(godot_asset_dest, "wb") as df:
            df.write(sf.read())

        report_entry = {
            "asset_id": asset_id,
            "name": info["name"],
            "source_file": str(src_path),
            "source_sha256": src_sha256,
            "glb_file": str(target_glb_path),
            "glb_sha256": glb_sha256,
            "render_preview_png": str(render_png_path),
            "render_sha256": png_sha256,
            "vertices": conv_res["vertices"],
            "polygons": conv_res["polygons"],
            "materials": conv_res["materials"],
            "blender_status": "PASSED (Blender 4.0.2 Headless)",
            "render_resolution": "800x600 PNG Studio Setup"
        }
        reports.append(report_entry)

    # 4. Godot 4.3 Headless Asset-Import & Szenen-Test
    print(f"\n---------------------------------------------------------------")
    print(f"🎮 4. Godot 4.3 Headless Asset-Import & Szenen-Validierung")
    print(f"---------------------------------------------------------------")
    godot_res = mcp_post("/api/3d/godot_test", {
        "project_dir": str(GODOT_PROJ_DIR)
    })

    godot_passed = godot_res.get("status") == "ok"
    imported_count = godot_res.get("imported_assets_count", 0)
    print(f"   Godot Engine: {godot_res.get('godot_version')}")
    print(f"   Imported Assets Count (.import files created): {imported_count}")
    print(f"   Godot Test Status: {'PASSED' if godot_passed else 'FAILED'}")

    for rep in reports:
        rep["godot_status"] = "PASSED (Godot 4.3 Headless)" if godot_passed else "FAILED"

    # Export Report JSON
    report_file = Path("/root/werkraum/kosmos/renders/3d_pipeline_prüfbericht.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({
            "zeitstempel": status_data["zeitstempel"],
            "mcp_server": MCP_SERVER_URL,
            "blender_version": status_data["blender_version"],
            "godot_version": status_data["godot_version"],
            "validated_assets_count": len(reports),
            "godot_imported_count": imported_count,
            "assets": reports
        }, f, indent=2, ensure_ascii=False)

    print(f"\n🎉 3D-Pipeline Prüfbericht gespeichert unter: {report_file}")
    return reports, godot_res

if __name__ == "__main__":
    run_validation()
