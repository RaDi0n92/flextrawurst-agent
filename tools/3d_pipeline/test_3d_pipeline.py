#!/usr/bin/env python3
"""
test_3d_pipeline.py — End-to-End Testsuite für Blender, Godot & den Flextrawurst 3D-MCP Server.
"""
import os
import sys
import json
import urllib.request

BASE_URL = "http://127.0.0.1:8090"
TEST_DIR = "/root/werkraum/tools/3d_pipeline/test_artifacts"
os.makedirs(TEST_DIR, exist_ok=True)

def test_3d_engine():
    print("⚡ Starte Flextrawurst 3D Pipeline & MCP E2E Tests...")

    # 1. Pipeline Status Check
    req = urllib.request.urlopen(f"{BASE_URL}/api/3d/status")
    res = json.loads(req.read().decode("utf-8"))
    assert res["status"] == "ok"
    assert res["blender_installed"] == True
    assert res["godot_installed"] == True
    print(f"✅ 1. 3D Status OK: Blender='{res['blender_version']}', Godot='{res['godot_version']}'")

    # 2. OpenAPI Schema Check (ChatGPT Custom GPTs Compatibility)
    req_oa = urllib.request.urlopen(f"{BASE_URL}/openapi.json")
    res_oa = json.loads(req_oa.read().decode("utf-8"))
    assert "openapi" in res_oa
    assert "paths" in res_oa
    print("✅ 2. OpenAPI v3 Schema für ChatGPT Actions OK")

    # 3. Standard MCP Protocol Check (tools/list)
    rpc_payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }).encode("utf-8")
    req_mcp = urllib.request.Request(f"{BASE_URL}/mcp", data=rpc_payload, headers={"Content-Type": "application/json"})
    res_mcp = json.loads(urllib.request.urlopen(req_mcp).read().decode("utf-8"))
    tools = res_mcp["result"]["tools"]
    assert len(tools) >= 3
    print(f"✅ 3. MCP JSON-RPC Protocol OK ({len(tools)} MCP Tools gelistet)")

    # 4. Erzeuge Test Cube in Blender & Rendere Vorschau PNG
    preview_img = os.path.join(TEST_DIR, "test_cube_preview.png")
    # Erzeuge ein minimales OBJ File für Test
    test_obj = os.path.join(TEST_DIR, "test_cube.obj")
    with open(test_obj, "w") as f:
        f.write("""# Test Cube
v -0.5 -0.5  0.5
v  0.5 -0.5  0.5
v -0.5  0.5  0.5
v  0.5  0.5  0.5
v -0.5  0.5 -0.5
v  0.5  0.5 -0.5
v -0.5 -0.5 -0.5
v  0.5 -0.5 -0.5
f 1 2 4 3
f 3 4 6 5
f 5 6 8 7
f 7 8 2 1
f 2 8 6 4
f 7 1 3 5
""")

    # Render Vorschau via Blender Headless REST API
    render_payload = json.dumps({
        "model_path": test_obj,
        "image_output": preview_img
    }).encode("utf-8")
    req_ren = urllib.request.Request(f"{BASE_URL}/api/3d/render", data=render_payload, headers={"Content-Type": "application/json"})
    res_ren = json.loads(urllib.request.urlopen(req_ren).read().decode("utf-8"))
    assert res_ren["status"] == "ok"
    assert os.path.exists(preview_img)
    print(f"✅ 4. Blender Headless Studio-Render OK (Vorschau PNG: {preview_img}, {res_ren['file_size_kb']} KB)")

    # 5. Konvertiere OBJ -> GLB via Blender Headless REST API
    test_glb = os.path.join(TEST_DIR, "test_cube.glb")
    conv_payload = json.dumps({
        "input_path": test_obj,
        "output_path": test_glb
    }).encode("utf-8")
    req_conv = urllib.request.Request(f"{BASE_URL}/api/3d/convert", data=conv_payload, headers={"Content-Type": "application/json"})
    res_conv = json.loads(urllib.request.urlopen(req_conv).read().decode("utf-8"))
    assert res_conv["status"] == "ok"
    assert os.path.exists(test_glb)
    print(f"✅ 5. Blender Headless 3D Konvertierung (OBJ -> GLB) OK ({res_conv['file_size_kb']} KB, Vertices: {res_conv['vertices']}, Polys: {res_conv['polygons']})")

    print("\n🎉 SÄMTLICHE 5 FLESTRAWURST 3D PIPELINE & MCP TESTS ERFOLGREICH BESTANDEN!")

if __name__ == "__main__":
    test_3d_engine()
