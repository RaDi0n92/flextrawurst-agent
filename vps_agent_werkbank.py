#!/usr/bin/env python3
import argparse, json, urllib.request, urllib.error
from urllib.parse import urlencode

def req(base, method, endpoint, api_key, body=None):
    url = base.rstrip("/") + endpoint
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    if method == "GET":
        if body:
            url += "?" + urlencode(body)
        r = urllib.request.Request(url=url, method="GET", headers=headers)
    else:
        data = json.dumps(body or {}).encode("utf-8")
        r = urllib.request.Request(url=url, data=data, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            txt = resp.read().decode("utf-8", errors="replace")
            print(f"HTTP {resp.status}\n{txt}")
            return 0
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}\n{txt}")
        return 1
    except Exception as e:
        print(f"ERROR: {e}")
        return 2

def main():
    p = argparse.ArgumentParser()
    p.add_argument("anweisung", nargs="?", default="status")
    p.add_argument("--vps-url", default="http://127.0.0.1:8001")
    p.add_argument("--api-key", required=True)
    p.add_argument("--api-style", choices=["workspace","bridge"], default="workspace")
    args = p.parse_args()

    style = {
        "workspace": {
            "status": ("GET","/health",None),
            "list": ("GET","/files",{"path":"."}),
            "read": ("GET","/read",{"path":"README.md"}),
            "exec": ("POST","/run",{"command":"pwd","timeout":30}),
            "write": ("POST","/write",{"path":"test.txt","content":"hello"})
        },
        "bridge": {
            "status": ("GET","/api/status",None),
            "list": ("POST","/api/files/list",{"path":".","recursive":True,"max_depth":3}),
            "read": ("POST","/api/files/read",{"path":"README.md"}),
            "exec": ("POST","/api/exec",{"command":"pwd","timeout":30}),
            "write": ("POST","/api/files/write",{"path":"test.txt","content":"hello"})
        }
    }[args.api_style]

    cmd = args.anweisung.strip().lower()
    action = "status" if "status" in cmd or "health" in cmd else \
             "list" if "list" in cmd or "struktur" in cmd else \
             "read" if cmd.startswith("read") else \
             "exec" if cmd.startswith("exec") or "run" in cmd else \
             "write" if cmd.startswith("write") or "schreib" in cmd else "status"

    method, endpoint, body = style[action]
    if action == "read" and cmd.startswith("read "):
        body = {"path": cmd.split(" ",1)[1]}
    if action == "exec" and cmd.startswith("exec "):
        body = {"command": cmd.split(" ",1)[1], "timeout": 30}
    return req(args.vps_url, method, endpoint, args.api_key, body)

if __name__ == "__main__":
    raise SystemExit(main())
