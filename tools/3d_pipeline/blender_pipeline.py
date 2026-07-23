#!/usr/bin/env python3
"""
blender_pipeline.py — Headless Blender 3D Automation Engine für Flextrawurst.
Bietet 3D-Format-Konvertierung, Mesh-Inspektion und automatisierte Studio-Vorschau-Renders.
"""
import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path

BLENDER_BIN = "blender"

def check_blender_installed() -> bool:
    try:
        res = subprocess.run([BLENDER_BIN, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res.returncode == 0
    except Exception:
        return False

def convert_model_headless(input_path: str, output_path: str) -> dict:
    """Konvertiert ein 3D-Modell (FBX, OBJ, STL, PLY, GLTF/GLB) in ein Zielformat via Headless Blender."""
    input_p = Path(input_path).resolve()
    output_p = Path(output_path).resolve()
    output_p.parent.mkdir(parents=True, exist_ok=True)
    
    if not input_p.exists():
        return {"status": "error", "error": f"Eingabedatei nicht gefunden: {input_path}"}
        
    ext_in = input_p.suffix.lower()
    ext_out = output_p.suffix.lower()
    
    # Inline Python Skript für Blender CLI Execution
    blender_script = f"""
import bpy
import sys

# Leere Szene initialisieren
bpy.ops.wm.read_factory_settings(use_empty=True)

input_file = r"{str(input_p)}"
output_file = r"{str(output_p)}"
ext_in = "{ext_in}"
ext_out = "{ext_out}"

try:
    # Import
    if ext_in in ['.gltf', '.glb']:
        bpy.ops.import_scene.gltf(filepath=input_file)
    elif ext_in == '.obj':
        try:
            bpy.ops.wm.obj_import(filepath=input_file)
        except Exception:
            bpy.ops.import_scene.obj(filepath=input_file)
    elif ext_in == '.fbx':
        bpy.ops.import_scene.fbx(filepath=input_file)
    elif ext_in == '.stl':
        bpy.ops.import_mesh.stl(filepath=input_file)
    elif ext_in == '.ply':
        bpy.ops.import_mesh.ply(filepath=input_file)
    else:
        print(f"UNSUPPORTED_IMPORT: {{ext_in}}")
        sys.exit(1)

    # Mesh Metadaten erfassen
    vertices = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')
    faces = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH')
    materials = len(bpy.data.materials)

    # Export
    if ext_out in ['.gltf', '.glb']:
        bpy.ops.export_scene.gltf(filepath=output_file, export_format='GLB' if ext_out == '.glb' else 'GLTF_EMBEDDED')
    elif ext_out == '.obj':
        try:
            bpy.ops.wm.obj_export(filepath=output_file)
        except Exception:
            bpy.ops.export_scene.obj(filepath=output_file)
    elif ext_out == '.fbx':
        bpy.ops.export_scene.fbx(filepath=output_file)
    elif ext_out == '.stl':
        bpy.ops.export_mesh.stl(filepath=output_file)
    else:
        print(f"UNSUPPORTED_EXPORT: {{ext_out}}")
        sys.exit(1)

    print(f"SUCCESS_STATS: {{vertices}}|{{faces}}|{{materials}}")

except Exception as e:
    print(f"BLENDER_ERROR: {{str(e)}}")
    sys.exit(1)
"""

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(blender_script)
        script_path = tf.name
        
    try:
        cmd = [BLENDER_BIN, "-b", "--python", script_path]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120)
        
        stdout = res.stdout
        if "SUCCESS_STATS:" in stdout:
            stats_line = [l for l in stdout.splitlines() if "SUCCESS_STATS:" in l][0]
            v, f, m = stats_line.split("SUCCESS_STATS:")[1].strip().split("|")
            return {
                "status": "ok",
                "input_file": str(input_p),
                "output_file": str(output_p),
                "vertices": int(v),
                "polygons": int(f),
                "materials": int(m),
                "file_size_kb": round(output_p.stat().st_size / 1024, 1)
            }
        else:
            return {"status": "error", "error": res.stderr or stdout}
    except Exception as e:
        return {"status": "error", "error": str(e)}
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)


def render_preview_headless(model_path: str, image_output_path: str) -> dict:
    """Erzeugt ein automatisiertes Studio-Renderbild (PNG) eines 3D-Modells via Headless Blender."""
    model_p = Path(model_path).resolve()
    image_p = Path(image_output_path).resolve()
    image_p.parent.mkdir(parents=True, exist_ok=True)
    
    if not model_p.exists():
        return {"status": "error", "error": f"Modell nicht gefunden: {model_path}"}
        
    ext_in = model_p.suffix.lower()
    
    render_script = f"""
import bpy
import mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)

model_file = r"{str(model_p)}"
image_file = r"{str(image_p)}"
ext_in = "{ext_in}"

# Import Model
if ext_in in ['.gltf', '.glb']:
    bpy.ops.import_scene.gltf(filepath=model_file)
elif ext_in == '.obj':
    try:
        bpy.ops.wm.obj_import(filepath=model_file)
    except Exception:
        bpy.ops.import_scene.obj(filepath=model_file)
elif ext_in == '.fbx':
    bpy.ops.import_scene.fbx(filepath=model_file)
elif ext_in == '.stl':
    bpy.ops.import_mesh.stl(filepath=model_file)

# Berechne Bounding Box aller Meshes
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
if not meshes:
    bpy.ops.mesh.primitive_cube_add()
    meshes = [bpy.context.active_object]

# Studio Beleuchtung & Kamera aufbauen
bpy.ops.object.camera_add(location=(3, -3, 2.5), rotation=(1.1, 0, 0.8))
camera = bpy.context.active_object
bpy.context.scene.camera = camera

# Licht 1: Key Light
bpy.ops.object.light_add(type='SUN', location=(4, -4, 5))
key_light = bpy.context.active_object
key_light.data.energy = 3.5

# Licht 2: Fill Light
bpy.ops.object.light_add(type='AREA', location=(-3, -3, 3))
fill_light = bpy.context.active_object
fill_light.data.energy = 50.0

# Render Einstellungen (Robustes CPU Studio Rendering)
bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
bpy.context.scene.render.resolution_x = 800
bpy.context.scene.render.resolution_y = 600
bpy.context.scene.render.filepath = image_file
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Render-Ausführung
bpy.ops.render.render(write_still=True)
print("RENDER_SUCCESS")
"""

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(render_script)
        script_path = tf.name

    try:
        cmd = [BLENDER_BIN, "-b", "--python", script_path]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120)
        
        if image_p.exists() or "RENDER_SUCCESS" in res.stdout:
            return {
                "status": "ok",
                "model_file": str(model_p),
                "image_output": str(image_p),
                "file_size_kb": round(image_p.stat().st_size / 1024, 1) if image_p.exists() else 0
            }
        else:
            return {"status": "error", "error": res.stderr or res.stdout}
    except Exception as e:
        return {"status": "error", "error": str(e)}
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)


if __name__ == "__main__":
    print(f"Blender Install-Check: {check_blender_installed()}")
