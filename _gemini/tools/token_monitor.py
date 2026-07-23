#!/usr/bin/env python3
"""
token_monitor.py — Live-Monitor für Antigravity CLI Kontextfenster & Token-Verbrauch.
Liest das aktuelle transcript.jsonl und zeigt Kontextgröße, Token-Schätzung & Prozent an.
"""
import os
import sys
import glob
import json
import time
from pathlib import Path

BRAIN_DIR = Path("/root/.gemini/antigravity-cli/brain")

def find_latest_transcript():
    transcripts = glob.glob(str(BRAIN_DIR / "*" / ".system_generated" / "logs" / "transcript.jsonl"))
    if not transcripts:
        return None
    return max(transcripts, key=os.path.getmtime)

def analyze_transcript(filepath):
    total_bytes = os.path.getsize(filepath)
    steps_count = 0
    estimated_tokens = 0
    last_step_type = ""
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            steps_count += 1
            try:
                data = json.loads(line)
                last_step_type = data.get("type", "")
            except Exception:
                pass

    # Ungefähre Token-Schätzung: ~4 Zeichen pro Token
    estimated_tokens = int(total_bytes / 4)
    # Gemini 3.6 / Pro Kontextfenster (1.000.000 Tokens)
    max_context = 1000000
    usage_pct = round((estimated_tokens / max_context) * 100, 2)
    
    return {
        "filepath": filepath,
        "conv_id": Path(filepath).parts[-5],
        "file_size_kb": round(total_bytes / 1024, 1),
        "steps_count": steps_count,
        "estimated_tokens": estimated_tokens,
        "max_context": max_context,
        "usage_pct": usage_pct,
        "last_step": last_step_type
    }

def print_hud():
    tf = find_latest_transcript()
    if not tf:
        print("⚠️  Keine aktive Antigravity CLI Chat-Session gefunden.")
        return
    
    info = analyze_transcript(tf)
    print("\033[H\033[J", end="") # Terminal screen clear
    print("=" * 65)
    print(" 🚀 ANTIGRAVITY CLI — KONTEXTFENSTER & TOKEN LIVE-MONITOR")
    print("=" * 65)
    print(f" 📂 Conversation ID : {info['conv_id']}")
    print(f" 📊 Verlauf Schritte: {info['steps_count']} Interaction Steps")
    print(f" 💾 Transcript Größe: {info['file_size_kb']} KB")
    print("-" * 65)
    
    # Visual Progress Bar
    bar_len = 30
    filled = int((info['usage_pct'] / 100) * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    
    print(f" 🧠 Kontext-Auslastung: [{bar}] {info['usage_pct']}%")
    print(f" 🔢 Geschätzte Tokens: ~{info['estimated_tokens']:,} / {info['max_context']:,} Tokens")
    print("=" * 65)
    print(" (Drücke Strg+C zum Beenden | Aktualisiert automatisch alle 2s)")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        print_hud()
    else:
        try:
            while True:
                print_hud()
                time.sleep(2)
        except KeyboardInterrupt:
            print("\nMonitor beendet.")
