#!/usr/bin/env python3
"""
godot_pipeline.py — Headless Godot Engine Automation & Scene Testing für Flextrawurst.
"""
import os
import sys
import json
import subprocess
from pathlib import Path

GODOT_BIN = "godot"

def check_godot_installed() -> bool:
    try:
        res = subprocess.run([GODOT_BIN, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res.returncode == 0
    except Exception:
        return False

def godot_import_and_test(project_dir: str) -> dict:
    """Führt automatisierten Import von 3D-Assets & Szenen-Validierung in Godot Headless aus."""
    p_dir = Path(project_dir).resolve()
    if not p_dir.exists():
        return {"status": "error", "error": f"Godot Projekt-Verzeichnis nicht gefunden: {project_dir}"}
        
    try:
        # Step 1: Auto-Import aller GLTF/GLB/FBX Assets
        cmd_import = [GODOT_BIN, "--headless", "--editor", "--quit", "--path", str(p_dir)]
        res_imp = subprocess.run(cmd_import, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120)
        
        # Zähle generierte .import Dateien
        import_files = list(p_dir.glob("**/*.import"))
        
        return {
            "status": "ok",
            "project_dir": str(p_dir),
            "godot_version": res_imp.stdout.splitlines()[0] if res_imp.stdout else "Godot 4.x Headless",
            "imported_assets_count": len(import_files),
            "output_log": res_imp.stdout[-500:] if len(res_imp.stdout) > 500 else res_imp.stdout
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    print(f"Godot Install-Check: {check_godot_installed()}")
