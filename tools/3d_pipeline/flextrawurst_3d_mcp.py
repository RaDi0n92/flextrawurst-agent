#!/usr/bin/env python3
"""
flextrawurst_3d_mcp.py — 3D-MCP Server (Model Context Protocol & OpenAPI REST) für Flextrawurst.
Ermöglicht ChatGPT & Antigravity CLI die Ausführung von Blender- & Godot-Headless-Aktionen.
Port: 8090
"""
import os
import sys
import json
import time
import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Importiere 3D Automation Engines
sys.path.insert(0, str(Path(__file__).parent))
import blender_pipeline
import godot_pipeline

PORT = int(os.environ.get("FLEXTRAWURST_3D_MCP_PORT", "8090"))
BASE_DIR = Path("/root/werkraum/tools/3d_pipeline")

def get_openapi_schema():
    """Generiert ein valides OpenAPI v3 Schema für ChatGPT Actions / Custom GPTs."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Flextrawurst 3D MCP Engine API",
            "version": "1.0.0",
            "description": "Headless Blender & Godot 3D Pipeline Actions für Flextrawurst"
        },
        "servers": [{"url": f"http://127.0.0.1:{PORT}"}],
        "paths": {
            "/api/3d/convert": {
                "post": {
                    "summary": "Konvertiert 3D-Modelle via Blender Headless",
                    "operationId": "convert3DModel",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "input_path": {"type": "string"},
                                        "output_path": {"type": "string"}
                                    },
                                    "required": ["input_path", "output_path"]
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": "OK"}}
                }
            },
            "/api/3d/render": {
                "post": {
                    "summary": "Erzeugt 1-Frame Studio Renderbild eines 3D-Modells",
                    "operationId": "render3DPreview",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "model_path": {"type": "string"},
                                        "image_output": {"type": "string"}
                                    },
                                    "required": ["model_path", "image_output"]
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": "OK"}}
                }
            },
            "/api/3d/godot_test": {
                "post": {
                    "summary": "Führt Asset-Import & Szenen-Validierung in Godot Headless aus",
                    "operationId": "godotImportAndTest",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "project_dir": {"type": "string"}
                                    },
                                    "required": ["project_dir"]
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": "OK"}}
                }
            },
            "/api/3d/status": {
                "get": {
                    "summary": "Liefert Status & System-Capabilities der 3D Pipeline",
                    "operationId": "get3DPipelineStatus",
                    "responses": {"200": {"description": "OK"}}
                }
            }
        }
    }


class MCPHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        from urllib.parse import urlparse
        path = urlparse(self.path).path.rstrip("/") or "/"
        
        if path in ("/openapi.json", "/api/openapi.json"):
            schema = get_openapi_schema()
            body = json.dumps(schema, indent=2).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/api/3d/status", "/status"):
            b_status = blender_pipeline.check_blender_installed()
            g_status = godot_pipeline.check_godot_installed()
            res = {
                "status": "ok",
                "blender_installed": b_status,
                "blender_version": "Blender 4.0.2 Headless" if b_status else "Not Installed",
                "godot_installed": g_status,
                "godot_version": "Godot 4.3 Stable Headless" if g_status else "Not Installed",
                "mcp_port": PORT,
                "zeitstempel": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            body = json.dumps(res, indent=2, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        from urllib.parse import urlparse
        path = urlparse(self.path).path.rstrip("/") or "/"
        length = int(self.headers.get("Content-Length", 0))
        body_data = json.loads(self.rfile.read(length)) if length > 0 else {}

        # 1. REST Endpoint: Konvertierung
        if path in ("/api/3d/convert", "/convert"):
            inp = body_data.get("input_path", "")
            outp = body_data.get("output_path", "")
            res = blender_pipeline.convert_model_headless(inp, outp)
            body = json.dumps(res, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # 2. REST Endpoint: Studio Render
        if self.path in ("/api/3d/render", "/render"):
            mod = body_data.get("model_path", "")
            img = body_data.get("image_output", "")
            res = blender_pipeline.render_preview_headless(mod, img)
            body = json.dumps(res, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # 3. REST Endpoint: Godot Import & Test
        if self.path in ("/api/3d/godot_test", "/godot_test"):
            p_dir = body_data.get("project_dir", "")
            res = godot_pipeline.godot_import_and_test(p_dir)
            body = json.dumps(res, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # 4. JSON-RPC Standard MCP Endpoint (/mcp oder /rpc)
        if self.path in ("/mcp", "/rpc", "/"):
            method = body_data.get("method", "")
            params = body_data.get("params", {})
            msg_id = body_data.get("id", 1)

            result_payload = {}
            if method in ("tools/list", "mcp.list_tools"):
                result_payload = {
                    "tools": [
                        {"name": "mcp__convert_3d_model", "description": "Konvertiert 3D Modelle via Blender Headless"},
                        {"name": "mcp__render_3d_preview", "description": "Erzeugt Studio PNG Renderbild via Blender"},
                        {"name": "mcp__godot_import_and_test", "description": "Führt Godot 4.3 Headless Asset-Import & Szenentest aus"}
                    ]
                }
            elif method in ("tools/call", "mcp.call_tool"):
                tool_name = params.get("name", "")
                args = params.get("arguments", {})
                if tool_name == "mcp__convert_3d_model":
                    res = blender_pipeline.convert_model_headless(args.get("input_path", ""), args.get("output_path", ""))
                elif tool_name == "mcp__render_3d_preview":
                    res = blender_pipeline.render_preview_headless(args.get("model_path", ""), args.get("image_output", ""))
                elif tool_name == "mcp__godot_import_and_test":
                    res = godot_pipeline.godot_import_and_test(args.get("project_dir", ""))
                else:
                    res = {"error": f"Unbekanntes MCP Tool: {tool_name}"}
                result_payload = {"content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False)}]}

            rpc_response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result_payload
            }
            body = json.dumps(rpc_response, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()


class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    print(f"⚡ Flextrawurst 3D MCP Server startet auf Port {PORT}...")
    server = ReusableHTTPServer(("127.0.0.1", PORT), MCPHandler)
    server.serve_forever()
