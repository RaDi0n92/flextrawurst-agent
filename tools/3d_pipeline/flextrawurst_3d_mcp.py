#!/usr/bin/env python3
"""
flextrawurst_3d_mcp.py — 3D-MCP Server (Model Context Protocol & OpenAPI REST) für Flextrawurst.
Ermöglicht ChatGPT & Antigravity CLI die Ausführung von Blender- & Godot-Headless-Aktionen.
Port: 8090
"""
import base64
import hashlib
import html
import os
import secrets
import sys
import json
import time
import datetime
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Importiere 3D Automation Engines
sys.path.insert(0, str(Path(__file__).parent))
import blender_pipeline
import godot_pipeline

PORT = int(os.environ.get("FLEXTRAWURST_3D_MCP_PORT", "8090"))
BASE_DIR = Path("/root/werkraum/tools/3d_pipeline")

# 2026-07-23 (Daniels Auftrag: oeffentlich ueber flextrawurst.de/3d-mcp/ erreichbar machen,
# fuer ChatGPT Custom-GPT-Actions + nativen MCP-Connector): der Server nahm bislang
# input_path/output_path/project_dir ungeprueft entgegen, komplett ohne Authentifizierung --
# oeffentlich erreichbar waere das beliebiges Datei-Lesen/Schreiben fuer jeden im Internet.
# API_KEY greift nur, wenn gesetzt (lokale/Antigravity-CLI-Nutzung ohne Env-Var bleibt
# unveraendert unauthentifiziert, wie bisher).
API_KEY = os.environ.get("FLEXTRAWURST_3D_MCP_KEY", "")
# 2026-07-23: oeffentliche Basis-URL fuer das OpenAPI-Schema (Custom GPT Actions lesen
# "servers"/"url" daraus, um zu wissen wohin sie ihre Requests schicken sollen) --
# ohne diese Variable wuerde das Schema weiterhin faelschlich 127.0.0.1 nennen.
PUBLIC_BASE_URL = os.environ.get("FLEXTRAWURST_3D_MCP_PUBLIC_URL", f"http://127.0.0.1:{PORT}")

# 2026-07-23 (Daniel: "need an OAuth" -- ChatGPTs nativer MCP-Connector verlangt einen
# echten OAuth-2.1-Authorization-Code+PKCE-Flow, ein blosser Bearer-Header reicht dafuer
# nicht, siehe /oauth/authorize + /oauth/token unten). Einzel-Nutzer-Server -- kein echtes
# Login noetig, aber die /oauth/authorize-Seite fragt den bestehenden API_KEY als
# Zustimmungs-Passwort ab, damit nicht irgendwer im Internet, der die URL kennt, sich
# selbst einen Zugriff freischalten kann. CLIENT_ID/CLIENT_SECRET sind statisch (ein
# einziger vertrauenswuerdiger Client: Daniels ChatGPT-Connector-Instanz).
OAUTH_CLIENT_ID = os.environ.get("FLEXTRAWURST_3D_MCP_CLIENT_ID", "flextrawurst-3d-mcp")
OAUTH_CLIENT_SECRET = os.environ.get("FLEXTRAWURST_3D_MCP_CLIENT_SECRET", "")
_AUTH_CODES: dict[str, dict] = {}   # code -> {redirect_uri, code_challenge, code_challenge_method, expires}
_ACCESS_TOKENS: dict[str, float] = {}  # token -> expires (unix ts)
_CODE_TTL_S = 300
_TOKEN_TTL_S = 3600 * 24 * 30  # 30 Tage -- Einzel-Nutzer-Tool, kein Refresh-Flow noetig


def _pkce_gueltig(code_verifier: str, code_challenge: str, method: str) -> bool:
    if method == "S256":
        digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        berechnet = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
        return berechnet == code_challenge
    if method == "plain":
        return code_verifier == code_challenge
    return False

def get_openapi_schema():
    """Generiert ein valides OpenAPI v3 Schema für ChatGPT Actions / Custom GPTs."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Flextrawurst 3D MCP Engine API",
            "version": "1.0.0",
            "description": "Headless Blender & Godot 3D Pipeline Actions für Flextrawurst"
        },
        "servers": [{"url": PUBLIC_BASE_URL}],
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

    def _autorisiert(self) -> bool:
        """2026-07-23: nur relevant sobald FLEXTRAWURST_3D_MCP_KEY gesetzt ist (oeffentliche
        Freischaltung) -- erwartet 'Authorization: Bearer <key>' ODER einen gueltigen,
        per OAuth-Flow ausgestellten Access-Token (siehe /oauth/token)."""
        if not API_KEY:
            return True
        auth = self.headers.get("Authorization", "")
        if auth == f"Bearer {API_KEY}":
            return True
        if auth.startswith("Bearer "):
            token = auth[len("Bearer "):]
            ablauf = _ACCESS_TOKENS.get(token)
            if ablauf and ablauf > time.time():
                return True
        return False

    def _unauthorized(self):
        body = json.dumps({"error": "unauthorized"}).encode("utf-8")
        self.send_response(401)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, obj: dict):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        # 2026-07-23 (OAuth-Discovery, RFC 8414 / RFC 9728): ChatGPT sucht diese Metadaten-
        # Datei automatisch, um Authorization-/Token-/Registration-Endpunkt zu finden --
        # ohne sie muesste Daniel jede URL einzeln von Hand eintragen.
        if path in ("/.well-known/oauth-authorization-server", "/.well-known/oauth-protected-resource"):
            self._json(200, {
                "issuer": PUBLIC_BASE_URL,
                "authorization_endpoint": f"{PUBLIC_BASE_URL}/oauth/authorize",
                "token_endpoint": f"{PUBLIC_BASE_URL}/oauth/token",
                "registration_endpoint": f"{PUBLIC_BASE_URL}/oauth/register",
                "response_types_supported": ["code"],
                "grant_types_supported": ["authorization_code"],
                "code_challenge_methods_supported": ["S256", "plain"],
                "token_endpoint_auth_methods_supported": ["client_secret_post", "none"],
            })
            return

        if path == "/oauth/authorize":
            qs = parse_qs(parsed.query)
            redirect_uri = (qs.get("redirect_uri") or [""])[0]
            state = (qs.get("state") or [""])[0]
            code_challenge = (qs.get("code_challenge") or [""])[0]
            code_challenge_method = (qs.get("code_challenge_method") or ["plain"])[0]
            eingereichter_key = (qs.get("key") or [""])[0]

            if not redirect_uri:
                self._json(400, {"error": "invalid_request", "error_description": "redirect_uri fehlt"})
                return

            if eingereichter_key != API_KEY or not API_KEY:
                # 2026-07-23: einfache Zustimmungs-Seite -- Einzel-Nutzer-Server, kein echtes
                # Login noetig, aber ohne den bestehenden API_KEY kann niemand sich selbst
                # freischalten, der nur die URL kennt.
                formular_url = f"{PUBLIC_BASE_URL}/oauth/authorize?{parsed.query}"
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"""<!doctype html><html><body style="font-family:monospace;background:#0a0e14;color:#cdd6f4;padding:40px">
<h3>Flextrawurst 3D-MCP — Zugriff erlauben?</h3>
<form method="GET" action="{html.escape(PUBLIC_BASE_URL)}/oauth/authorize">
<input type="hidden" name="redirect_uri" value="{html.escape(redirect_uri)}">
<input type="hidden" name="state" value="{html.escape(state)}">
<input type="hidden" name="code_challenge" value="{html.escape(code_challenge)}">
<input type="hidden" name="code_challenge_method" value="{html.escape(code_challenge_method)}">
<label>Schluessel: <input type="password" name="key"></label>
<button type="submit">Erlauben</button>
</form></body></html>""".encode("utf-8"))
                return

            code = secrets.token_urlsafe(32)
            _AUTH_CODES[code] = {
                "redirect_uri": redirect_uri,
                "code_challenge": code_challenge,
                "code_challenge_method": code_challenge_method,
                "expires": time.time() + _CODE_TTL_S,
            }
            trenner = "&" if "?" in redirect_uri else "?"
            ziel = f"{redirect_uri}{trenner}code={urllib.parse.quote(code)}&state={urllib.parse.quote(state)}"
            self.send_response(302)
            self.send_header("Location", ziel)
            self.end_headers()
            return

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
        roh = self.rfile.read(length) if length > 0 else b""
        content_type = self.headers.get("Content-Type", "")
        if "application/x-www-form-urlencoded" in content_type:
            # 2026-07-23: /oauth/token wird per Spezifikation (RFC 6749) form-encoded
            # gesendet, nicht als JSON -- anders als der Rest dieses Servers.
            body_data = {k: v[0] for k, v in urllib.parse.parse_qs(roh.decode("utf-8")).items()}
        else:
            body_data = json.loads(roh) if roh else {}

        # 2026-07-23 (OAuth): /oauth/register (DCR) und /oauth/token sind absichtlich VOR
        # dem Autorisierungs-Check -- man braucht ja erst einen Token, bevor man einen
        # Bearer-Header mitschicken kann.
        if path == "/oauth/register":
            self._json(201, {
                "client_id": OAUTH_CLIENT_ID,
                "client_secret": OAUTH_CLIENT_SECRET,
                "redirect_uris": body_data.get("redirect_uris", []),
                "token_endpoint_auth_method": "client_secret_post" if OAUTH_CLIENT_SECRET else "none",
            })
            return

        if path == "/oauth/token":
            grant_type = body_data.get("grant_type", "")
            if grant_type != "authorization_code":
                self._json(400, {"error": "unsupported_grant_type"})
                return
            code = body_data.get("code", "")
            eintrag = _AUTH_CODES.pop(code, None)
            if not eintrag or eintrag["expires"] < time.time():
                self._json(400, {"error": "invalid_grant", "error_description": "Code ungueltig oder abgelaufen"})
                return
            code_verifier = body_data.get("code_verifier", "")
            if eintrag["code_challenge"] and not _pkce_gueltig(
                code_verifier, eintrag["code_challenge"], eintrag["code_challenge_method"]
            ):
                self._json(400, {"error": "invalid_grant", "error_description": "PKCE-Verifikation fehlgeschlagen"})
                return
            token = secrets.token_urlsafe(32)
            _ACCESS_TOKENS[token] = time.time() + _TOKEN_TTL_S
            self._json(200, {
                "access_token": token,
                "token_type": "Bearer",
                "expires_in": _TOKEN_TTL_S,
            })
            return

        if not self._autorisiert():
            self._unauthorized()
            return

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
            if method == "initialize":
                # 2026-07-23: fehlte bisher -- das offizielle MCP-Protokoll (Streamable HTTP)
                # erwartet diesen Handshake vor tools/list/tools/call, sonst brechen konforme
                # Clients (z.B. ChatGPTs nativer MCP-Connector) die Verbindung ab.
                result_payload = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "flextrawurst-3d-mcp", "version": "1.0.0"},
                }
            elif method in ("tools/list", "mcp.list_tools"):
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
