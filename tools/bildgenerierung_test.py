#!/usr/bin/env python3
"""
flextrawurst Bildgenerator
Port: 8042

GET  /bildgenerator       → HTML-UI
POST /api/generate        → startet Job, gibt job_id zurück (JSON)
GET  /api/status/<job_id> → Status, Fortschritt, ETA, image_url wenn fertig
GET  /api/image/<job_id>  → PNG-Datei wenn fertig
GET  /api/health          → {"status": "ok"}
GET  /api/models          → Liste aller Modelle (ohne path)
"""

import os
import subprocess
import tempfile
import time
import threading
import queue
import uuid
import json
import urllib.request
import io
from pathlib import Path
from flask import Flask, request, send_file, jsonify, Response
from PIL import Image

# LD_LIBRARY_PATH damit sd-cli libstable-diffusion.so findet
SD_LIB_DIR = "/root/werkraum/tools/sd_cpp"
os.environ["LD_LIBRARY_PATH"] = SD_LIB_DIR + ":" + os.environ.get("LD_LIBRARY_PATH", "")

app = Flask(__name__)

SD_CLI     = Path("/root/werkraum/tools/sd_cpp/sd-cli")
OUTPUT_DIR = Path("/root/werkraum/bilder/generiert")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODELS_DIR    = Path("/root/werkraum/tools/models")
SDXL_SHARED   = MODELS_DIR / "sdxl_shared"
FLUX_SHARED   = MODELS_DIR / "flux_shared"

# ---------------------------------------------------------------------------
# Modell-Konfiguration
# ---------------------------------------------------------------------------
# typ: "SDXL_FULL"  → --model <path>
#      "SDXL_SPLIT" → --diffusion-model <path> + --clip_l + --clip_g + --vae
#      "FLUX"       → --diffusion-model <path> + --clip_l + --t5xxl + --vae
# ---------------------------------------------------------------------------
MODELS = {
    # steps_res: [(max_dim, steps), ...] — max(w,h) wird mit den Schwellwerten verglichen
    # sampler: sd.cpp --sampling-method Wert
    # guidance: FLUX distilled-guidance-scale (nur dev + kontext)
    # clip_skip: --clip-skip N (nur Pony benötigt 2)
    "sdxl_lightning": {
        "label":    "SDXL-Lightning (4-Step)",
        "path":     MODELS_DIR / "sdxl_lightning_4step_q5_0.gguf",
        "typ":      "SDXL_FULL",
        "steps":    4,
        "steps_res": [(512, 4), (1024, 4), (9999, 6)],
        "cfg":      1.0,
        "sampler":  "euler",
        "zeit_512": "~20-25 Min",
        "staerke":  "schnell, gute Qualität, vielseitig",
        "groesse":  "2.8 GB",
        "quant":    "Q5_0",
        "zensur":   "◑ kein Filter",
    },
    "juggernaut_xl": {
        "label":    "Juggernaut XL v9",
        "path":     MODELS_DIR / "juggernaut_xl_v9_q5_0.gguf",
        "typ":      "SDXL_FULL",
        "steps":    8,
        "steps_res": [(256, 4), (512, 8), (768, 10), (1024, 12), (9999, 14)],
        "cfg":      6.0,
        "sampler":  "dpm++2m",
        "zeit_512": "~45-50 Min",
        "staerke":  "fotorealistisch, Portraits, Szenen",
        "groesse":  "3.1 GB",
        "quant":    "Q5_K",
        "zensur":   "◑ kein Filter",
    },
    "pony": {
        "label":    "Pony Diffusion V6 XL",
        "path":     MODELS_DIR / "pony_diffusion_v6_q5_0.gguf",
        "typ":      "SDXL_FULL",
        "steps":    8,
        "steps_res": [(256, 4), (512, 8), (768, 12), (1024, 15), (9999, 18)],
        "cfg":      7.0,
        "sampler":  "euler_a",
        "clip_skip": 2,
        "zeit_512": "~45-50 Min",
        "staerke":  "NSFW-trainiert, Illustration, Anime — für explizite Inhalte",
        "groesse":  "2.9 GB",
        "quant":    "Q5_K",
        "zensur":   "✓ explizit uncensored",
    },
    "realvis_xl": {
        "label":    "RealVisXL V5",
        "path":     MODELS_DIR / "realvisxl_v5_q5_0.gguf",
        "typ":      "SDXL_FULL",
        "steps":    8,
        "steps_res": [(256, 4), (512, 8), (768, 10), (1024, 12), (9999, 14)],
        "cfg":      5.0,
        "sampler":  "dpm++2m",
        "zeit_512": "~45-50 Min",
        "staerke":  "realistisch, Fotos, Menschen, Details",
        "groesse":  "2.9 GB",
        "quant":    "Q5_K",
        "zensur":   "◑ kein Filter",
    },
    "flux_schnell": {
        "label":    "FLUX.1-schnell",
        "path":     MODELS_DIR / "flux1-schnell-q4_k.gguf",
        "typ":      "FLUX",
        "steps":    4,
        "steps_res": [(9999, 4)],
        "cfg":      1.0,
        "sampler":  "euler",
        "zeit_512": "~5-6 Min",
        "staerke":  "deutlich besser als SDXL, schnellstes FLUX",
        "groesse":  "6.5 GB",
        "quant":    "Q4_K",
        "zensur":   "✓ lokal frei",
    },
    "flux_dev": {
        "label":    "FLUX.1-dev",
        "path":     MODELS_DIR / "flux1-dev-q4_k.gguf",
        "typ":      "FLUX",
        "steps":    15,
        "steps_res": [(256, 10), (512, 15), (768, 18), (1024, 20), (9999, 25)],
        "cfg":      1.0,
        "guidance": 3.5,
        "sampler":  "euler",
        "zeit_512": "~18-20 Min",
        "staerke":  "bestes open-source Modell, komplexe Prompts",
        "groesse":  "6.5 GB",
        "quant":    "Q4_K",
        "zensur":   "✓ lokal frei",
    },
    "flux_kontext": {
        "label":    "FLUX.1-Kontext",
        "path":     MODELS_DIR / "flux1-kontext-dev-q4_k.gguf",
        "typ":      "FLUX_KONTEXT",
        "steps":    15,
        "steps_res": [(256, 10), (512, 15), (768, 20), (1024, 25), (9999, 28)],
        "cfg":      1.0,
        "guidance": 2.5,
        "sampler":  "euler",
        "zeit_512": "~18-20 Min",
        "staerke":  "Bild bearbeiten / Person in neue Szene setzen (benötigt Referenzbild)",
        "groesse":  "6.5 GB",
        "quant":    "Q4_K",
        "zensur":   "✓ lokal frei",
    },
}

# ---------------------------------------------------------------------------
# Auto-Suggest: Keywords + Ollama
# ---------------------------------------------------------------------------
_KEYWORD_MODEL = [
    (["anime", "manga", "cartoon", "illustration", "drawing", "zeichnung", "comic", "cel shad"], "pony"),
    (["portrait", "photo", "realistic", "realist", "person", "face", "fotorealist", "fotografie",
      "gesicht", "mensch", "haut", "körper", "body", "skin"], "juggernaut_xl"),
    (["schnell", "quick", "fast", "simple", "einfach", "skizze", "rough"], "sdxl_lightning"),
    (["complex", "komplexer", "intricate", "detailed", "detaill", "architektur", "landschaft",
      "szene", "scene", "fantasy", "surreal", "cinematic", "cinéma"], "flux_dev"),
]
_KEYWORD_MIX = {
    "collage": ["nebeneinander", "side by side", "collage", "compare", "vergleich", "neben", "gegenüber"],
    "blend":   ["mix", "blend", "merge", "verschmelzen", "vereinen", "kombinier", "zusammen", "überblende"],
}

def _keywords_suggest(prompt: str, multi: bool) -> dict:
    p = prompt.lower()
    model = "flux_schnell"
    for kws, m in _KEYWORD_MODEL:
        if any(k in p for k in kws):
            model = m
            break
    mix = "blend"
    for mtype, kws in _KEYWORD_MIX.items():
        if any(k in p for k in kws):
            mix = mtype
            break
    return {"model": model, "mix_type": mix, "source": "keywords"}

def _ollama_suggest(prompt: str, multi: bool, timeout: int = 5) -> dict | None:
    system = (
        "You select the best image generation model. Reply ONLY with compact JSON, no markdown.\n"
        "Models: sdxl_lightning(fast,4steps), juggernaut_xl(photorealistic,8steps), "
        "pony(anime/art,8steps), realvis_xl(realistic photos,8steps), "
        "flux_schnell(better quality,4steps), flux_dev(best quality,20steps).\n"
        "Mix types if multiple reference images: blend=pixel average, collage=side by side."
    )
    user = (
        f'Prompt: "{prompt}"\n'
        f'Multiple reference images: {"yes" if multi else "no"}\n'
        'Reply JSON: {"model":"...","mix_type":"blend","reason":"one sentence"}'
    )
    payload = json.dumps({
        "model": "gemma4:e2b-it-q4_K_M",
        "prompt": f"{system}\n\n{user}",
        "stream": False,
        "options": {"num_ctx": 512, "temperature": 0.1, "think": False},
    }).encode()
    try:
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload, headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = json.loads(resp.read())["response"].strip()
            start = raw.find("{")
            end   = raw.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(raw[start:end])
                result["source"] = "ollama"
                if result.get("model") not in MODELS:
                    result["model"] = "flux_schnell"
                return result
    except Exception:
        pass
    return None

def auto_suggest(prompt: str, multi: bool = False) -> dict:
    kw = _keywords_suggest(prompt, multi)
    ol = _ollama_suggest(prompt, multi, timeout=5)
    if ol and ol.get("model") in MODELS:
        ol.setdefault("mix_type", kw["mix_type"])
        return ol
    return kw

# ---------------------------------------------------------------------------
# Image Mixing (Pillow)
# ---------------------------------------------------------------------------
def mix_images(paths: list[Path], mode: str = "blend", target_size: tuple = (512, 512)) -> Path:
    imgs = [Image.open(p).convert("RGBA").resize(target_size, Image.LANCZOS) for p in paths]
    if mode == "collage":
        total_w = target_size[0] * len(imgs)
        canvas  = Image.new("RGBA", (total_w, target_size[1]), (0, 0, 0, 255))
        for i, img in enumerate(imgs):
            canvas.paste(img, (i * target_size[0], 0))
        result = canvas.resize(target_size, Image.LANCZOS)
    else:
        # blend: equal-weight pixel average
        import numpy as np
        arrays = [np.array(img).astype(float) for img in imgs]
        avg    = np.mean(arrays, axis=0).astype("uint8")
        result = Image.fromarray(avg, "RGBA")
    out = Image.new("RGB", target_size, (0, 0, 0))
    out.paste(result.convert("RGB"))
    tmp_path = Path(f"/tmp/bilder_mix_{uuid.uuid4()}.png")
    out.save(str(tmp_path))
    return tmp_path

# Shared encoder/vae paths
SDXL_CLIP_L = SDXL_SHARED / "clip" / "clip_l.safetensors"
SDXL_CLIP_G = SDXL_SHARED / "clip" / "clip_g.safetensors"
SDXL_VAE    = SDXL_SHARED / "vae" / "xlVAEC_c91.safetensors"

FLUX_CLIP_L = FLUX_SHARED / "clip_l.safetensors"
FLUX_T5XXL  = FLUX_SHARED / "t5xxl_fp8_e4m3fn.safetensors"
FLUX_VAE    = FLUX_SHARED / "ae.safetensors"

# ---------------------------------------------------------------------------
# Auflösungen
# ---------------------------------------------------------------------------
RESOLUTIONS = [
    ("128x128",    128,   128),
    ("256x256",    256,   256),
    ("512x512",    512,   512),
    ("640x480",    640,   480),
    ("666x666",    666,   666),
    ("768x576",    768,   576),
    ("768x768",    768,   768),
    ("768x1024",   768,  1024),
    ("960x540",    960,   540),
    ("1024x768",  1024,   768),
    ("1024x1024", 1024,  1024),
    ("1280x720",  1280,   720),
    ("1280x960",  1280,   960),
    ("1336x768",  1336,   768),
    ("1440x900",  1440,   900),
    ("1920x1080", 1920,  1080),
]

RES_MAP = {r[0]: (r[1], r[2]) for r in RESOLUTIONS}

# ---------------------------------------------------------------------------
# Stile
# ---------------------------------------------------------------------------
STYLES = [
    ("default",         "Standard",              ""),
    ("skizze",          "Skizzenhaft",            ", pencil sketch, rough lines, monochrome"),
    ("bilderbuch",      "Bilderbuch",             ", children's book illustration, colorful, soft"),
    ("realistisch",     "Realistisch",            ", photorealistic, detailed, sharp"),
    ("impressionismus", "Impressionismus",         ", impressionist painting, visible brushstrokes, soft light, Monet style"),
    ("surrealismus",    "Surrealismus",            ", surrealist, dreamlike, paradoxical, Salvador Dali style"),
    ("aquarell",        "Aquarell",               ", watercolor, soft edges, flowing colors, organic"),
    ("anime",           "Anime / Manga",           ", anime style, expressive eyes, clean lines, vibrant"),
    ("cyberpunk",       "Cyberpunk",              ", cyberpunk, neon lights, dark dystopian, futuristic"),
    ("pixel",           "Pixel Art",              ", 8-bit pixel art, retro game style, limited palette"),
    ("pixar",           "3D Animationsfilm",       ", Pixar style, 3D animation, warm lighting, expressive"),
    ("popad",           "Pop Art",                ", pop art, bold primary colors, Ben-Day dots, Andy Warhol style"),
    ("ghibli",          "Studio Ghibli",           ", Studio Ghibli style, painterly, lush nature, dreamy"),
    ("flat",            "Flat Design",             ", minimalist flat design, clean shapes, no gradients, geometric"),
    ("papercraft",      "Papercraft",              ", papercraft, layered paper, 3D cut paper illusion"),
]

STYLE_MAP = {s[0]: s[2] for s in STYLES}

# ---------------------------------------------------------------------------
# Steps per Auflösung
# ---------------------------------------------------------------------------
def _get_steps(model_cfg: dict, w: int, h: int) -> int:
    steps_res = model_cfg.get("steps_res")
    if not steps_res:
        return model_cfg["steps"]
    max_dim = max(w, h)
    for max_d, s in steps_res:
        if max_dim <= max_d:
            return s
    return steps_res[-1][1]


# ---------------------------------------------------------------------------
# Zeitschätzung (Sekunden) für verschiedene Auflösungen pro Modell-Typ
# ---------------------------------------------------------------------------
def _estimate_secs(model_cfg: dict, w: int, h: int) -> int:
    pixels   = w * h
    base_pix = 512 * 512
    steps    = _get_steps(model_cfg, w, h)
    typ      = model_cfg["typ"]

    if typ in ("FLUX", "FLUX_KONTEXT"):
        secs_per_512x512_step = 73
    else:
        secs_per_512x512_step = 335

    ratio = pixels / base_pix
    return int(secs_per_512x512_step * ratio * steps)


# ---------------------------------------------------------------------------
# Job-State (in-memory)
# ---------------------------------------------------------------------------
JOBS: dict = {}
JOB_QUEUE = queue.Queue()
JOBS_LOCK = threading.Lock()


# ---------------------------------------------------------------------------
# sd-cli Command Builder
# ---------------------------------------------------------------------------
def _build_cmd(model_key: str, full_prompt: str, w: int, h: int, output_path: Path,
               init_img_path: Path | None = None, strength: float = 0.75,
               negative_prompt: str = "") -> list[str]:
    cfg    = MODELS[model_key]
    typ    = cfg["typ"]
    steps  = _get_steps(cfg, w, h)
    sampler = cfg.get("sampler", "euler")

    base = [str(SD_CLI)]

    if typ == "SDXL_FULL":
        base += [
            "--model",            str(cfg["path"]),
            "--cfg-scale",        str(cfg.get("cfg", 7.0)),
            "--sampling-method",  sampler,
            "--force-sdxl-vae-conv-scale",
        ]
        if cfg.get("clip_skip"):
            base += ["--clip-skip", str(cfg["clip_skip"])]
    elif typ == "SDXL_SPLIT":
        base += [
            "--diffusion-model",  str(cfg["path"]),
            "--clip_l",           str(SDXL_CLIP_L),
            "--clip_g",           str(SDXL_CLIP_G),
            "--vae",              str(SDXL_VAE),
            "--sampling-method",  sampler,
        ]
    elif typ in ("FLUX", "FLUX_KONTEXT"):
        base += [
            "--diffusion-model", str(cfg["path"]),
            "--clip_l",          str(FLUX_CLIP_L),
            "--t5xxl",           str(FLUX_T5XXL),
            "--vae",             str(FLUX_VAE),
            "--cfg-scale",       str(cfg["cfg"]),
            "--sampling-method", "euler",
        ]
        if cfg.get("guidance"):
            base += ["--guidance", str(cfg["guidance"])]

    base += [
        "--prompt", full_prompt,
        "--width",  str(w),
        "--height", str(h),
        "--steps",  str(steps),
        "--output", str(output_path),
    ]

    if negative_prompt:
        base += ["--negative-prompt", negative_prompt]

    if init_img_path:
        base += ["--init-img", str(init_img_path), "--strength", str(round(strength, 2))]

    if typ in ("FLUX", "FLUX_KONTEXT"):
        base += ["--clip-on-cpu"]

    return base


# ---------------------------------------------------------------------------
# Background Worker
# ---------------------------------------------------------------------------
def worker():
    while True:
        job_id, model_key, full_prompt, w, h, estimated_secs, output_path, init_img_path, strength, negative_prompt = JOB_QUEUE.get()
        with JOBS_LOCK:
            JOBS[job_id]["status"]     = "running"
            JOBS[job_id]["started_at"] = time.time()

        cmd = _build_cmd(model_key, full_prompt, w, h, output_path, init_img_path, strength, negative_prompt)

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            step_total     = MODELS[model_key]["steps"]
            step_done      = 0
            sampling_start = None
            step_times: list[float] = []

            for line in proc.stdout:
                line = line.strip()

                # Echte Diffusions-Steps erkennen: Zeilen mit "s/it" oder "it/s"
                is_sampling_line = "s/it" in line or "it/s" in line
                if is_sampling_line:
                    if sampling_start is None:
                        sampling_start = time.time()
                    for token in line.split():
                        if "/" in token:
                            parts = token.split("/")
                            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                                new_step = int(parts[0])
                                if new_step > step_done:
                                    step_times.append(time.time())
                                step_done  = new_step
                                step_total = int(parts[1])

                elapsed = time.time() - JOBS[job_id]["started_at"]

                if not is_sampling_line and sampling_start is None:
                    # Modell lädt noch — Fortschritt auf 0 lassen, ETA unverändert
                    pct = 0
                    eta = max(0, int(estimated_secs - elapsed))
                    phase = "loading"
                else:
                    pct   = min(95, int(step_done / max(step_total, 1) * 95))
                    phase = "sampling"
                    # ETA aus echten Step-Zeiten berechnen
                    if len(step_times) >= 2:
                        avg_step = (step_times[-1] - step_times[0]) / (len(step_times) - 1)
                        remaining = max(0, step_total - step_done) * avg_step
                        eta = int(remaining)
                    else:
                        eta = max(0, int(estimated_secs - elapsed))

                with JOBS_LOCK:
                    JOBS[job_id]["progress_pct"] = pct
                    JOBS[job_id]["eta_seconds"]  = eta
                    JOBS[job_id]["phase"]        = phase

            proc.wait(timeout=14400)  # 4h max

            if proc.returncode != 0:
                with JOBS_LOCK:
                    JOBS[job_id]["status"] = "error"
                    JOBS[job_id]["error"]  = f"sd-cli exit code {proc.returncode}"
            elif not Path(output_path).exists():
                with JOBS_LOCK:
                    JOBS[job_id]["status"] = "error"
                    JOBS[job_id]["error"]  = "Kein Ausgabe-PNG erzeugt"
            else:
                with JOBS_LOCK:
                    JOBS[job_id]["status"]       = "done"
                    JOBS[job_id]["progress_pct"] = 100
                    JOBS[job_id]["eta_seconds"]  = 0
                    JOBS[job_id]["image_url"]    = f"/api/image/{job_id}"

        except subprocess.TimeoutExpired:
            proc.kill()
            with JOBS_LOCK:
                JOBS[job_id]["status"] = "error"
                JOBS[job_id]["error"]  = "Timeout (4h)"
        except Exception as ex:
            with JOBS_LOCK:
                JOBS[job_id]["status"] = "error"
                JOBS[job_id]["error"]  = str(ex)
        finally:
            if init_img_path:
                p = Path(init_img_path)
                if p.exists() and str(p).startswith("/tmp/"):
                    try:
                        p.unlink()
                    except Exception:
                        pass

        JOB_QUEUE.task_done()


_worker_thread = threading.Thread(target=worker, daemon=True)
_worker_thread.start()


# ---------------------------------------------------------------------------
# HTML-UI Builder helpers
# ---------------------------------------------------------------------------
def _build_resolution_options():
    opts = []
    for name, _, _ in RESOLUTIONS:
        opts.append(f'<option value="{name}">{name}</option>')
    return "\n".join(opts)


def _build_style_options():
    opts = []
    for key, label, _ in STYLES:
        opts.append(f'<option value="{key}">{label}</option>')
    return "\n".join(opts)


def _is_available(cfg: dict) -> bool:
    return cfg["path"].exists() and not cfg.get("broken", False)

def _is_pending(cfg: dict) -> bool:
    return not cfg["path"].exists() and "pending_reason" in cfg and not cfg.get("broken", False)


def _build_model_options():
    opts = ['<option value="auto" selected>🤖 Auto (KI wählt)</option>']
    for key, cfg in MODELS.items():
        if cfg.get("broken"):
            opts.append(f'<option value="{key}" disabled style="color:#555">⚠ {cfg["label"]} (inkompatibel)</option>')
        elif _is_pending(cfg):
            opts.append(f'<option value="{key}" disabled style="color:#888">⏳ {cfg["label"]} ({cfg["pending_reason"]})</option>')
        else:
            opts.append(f'<option value="{key}">{cfg["label"]}</option>')
    return "\n".join(opts)


def _build_model_table_rows():
    rows = []
    for key, cfg in MODELS.items():
        zensur = cfg.get("zensur", "")
        if zensur.startswith("✓"):
            zensur_class = "zensur-frei"
        elif zensur.startswith("◑"):
            zensur_class = "zensur-neutral"
        else:
            zensur_class = ""
        broken = cfg.get("broken", False)
        pending = _is_pending(cfg)
        row_class = "broken-row" if (broken or pending) else ""
        if broken:
            name_cell = f'{cfg["label"]}<br><small style="color:#e07070">⚠ {cfg.get("broken_reason", "")}</small>'
        elif pending:
            name_cell = f'{cfg["label"]}<br><small style="color:#8888ff">⏳ {cfg["pending_reason"]}</small>'
        else:
            name_cell = cfg["label"]
        dimmed = broken or pending
        zeit_cell = f'<span style="color:#555">—</span>' if dimmed else cfg["zeit_512"]
        rows.append(
            f'<tr data-model="{key}" class="{row_class}">'
            f'<td>{name_cell}</td>'
            f'<td style="{"color:#555" if dimmed else ""}">{"SDXL" if "SDXL" in cfg["typ"] else cfg["typ"]}</td>'
            f'<td class="zeit">{zeit_cell}</td>'
            f'<td style="{"color:#555" if dimmed else ""}">{cfg["staerke"]}</td>'
            f'<td style="{"color:#555" if dimmed else ""}">{cfg["groesse"]}</td>'
            f'<td class="{zensur_class}" style="{"color:#555" if dimmed else ""}">{zensur}</td>'
            f'</tr>'
        )
    return "\n".join(rows)


def _models_js_data():
    data = {}
    for key, cfg in MODELS.items():
        data[key] = {
            "label":     cfg["label"],
            "typ":       cfg["typ"].replace("_SPLIT","").replace("_FULL",""),
            "steps":     cfg["steps"],
            "steps_res": cfg.get("steps_res", []),
            "zeit_512":  cfg["zeit_512"],
            "staerke":   cfg["staerke"],
            "groesse":   cfg["groesse"],
            "zensur":    cfg.get("zensur", ""),
            "broken":    cfg.get("broken", False) or _is_pending(cfg),
        }
    return json.dumps(data)


# ---------------------------------------------------------------------------
# HTML-UI
# ---------------------------------------------------------------------------
HTML_UI = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bildgenerator — flextrawurst</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:      #0d0d0d;
    --surface: #161616;
    --surface2:#1e1e1e;
    --border:  #2a2a2a;
    --accent:  #7ecf8f;
    --accent2: #3a7d50;
    --text:    #e0e0e0;
    --muted:   #777;
    --error:   #e07070;
    --info:    #6ab0d4;
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 32px 16px 64px;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    width: 100%;
    max-width: 780px;
    overflow: hidden;
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 24px;
    border-bottom: 1px solid var(--border);
  }

  .card-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .status-badge {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 12px;
    color: var(--muted);
  }

  .status-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #555;
    flex-shrink: 0;
  }

  .status-dot.online {
    background: var(--accent);
    box-shadow: 0 0 6px var(--accent);
    animation: pulse 2s infinite;
  }

  .status-dot.offline {
    background: var(--error);
    box-shadow: 0 0 6px var(--error);
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
  }

  .card-body {
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 18px;
  }

  textarea {
    width: 100%;
    min-height: 90px;
    background: #111;
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-size: 14px;
    padding: 12px 14px;
    resize: vertical;
    font-family: inherit;
    line-height: 1.5;
    outline: none;
    transition: border-color 0.2s;
  }

  textarea:focus { border-color: var(--accent2); }

  .row-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
  }

  .row-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 14px;
  }

  label {
    display: block;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
    margin-bottom: 6px;
  }

  select {
    width: 100%;
    background: #111;
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-size: 13px;
    padding: 10px 12px;
    outline: none;
    cursor: pointer;
    transition: border-color 0.2s;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%23777' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 12px center;
    background-color: #111;
    padding-right: 34px;
  }

  select:focus { border-color: var(--accent2); }

  /* Modell-Tabelle */
  .modell-tabelle-wrap {
    overflow-x: auto;
    border-radius: 8px;
    border: 1px solid var(--border);
  }

  .modell-tabelle {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }

  .modell-tabelle th {
    background: #1a1a1a;
    color: var(--muted);
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
  }

  .modell-tabelle td {
    padding: 8px 12px;
    border-bottom: 1px solid #1e1e1e;
    color: #bbb;
    vertical-align: top;
  }

  .modell-tabelle tr:last-child td {
    border-bottom: none;
  }

  .modell-tabelle tr {
    transition: background 0.15s;
  }

  .modell-tabelle tr.aktiv {
    background: #1e2e22;
  }

  .modell-tabelle tr.aktiv td {
    color: var(--text);
  }

  .modell-tabelle tr.aktiv td:first-child {
    color: var(--accent);
    font-weight: 600;
  }

  .zensur-frei {
    color: #7ecf8f;
    white-space: nowrap;
  }

  .zensur-neutral {
    color: #c8b84a;
    white-space: nowrap;
  }

  .broken-row td { opacity: 0.4; }
  .broken-row:hover td { opacity: 0.5; }

  .zensur-hint {
    font-size: 11px;
    color: var(--muted);
    padding: 6px 4px 0;
    line-height: 1.5;
  }

  .zeit-display {
    font-size: 11px;
    color: var(--info);
    padding: 6px 0 2px;
  }

  /* Ziel-Auswahl */
  .ziel-section { margin-bottom: 18px; }
  .ziel-label { font-size: 0.75rem; color: #555; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 8px; }
  .ziel-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
  @media (max-width: 480px) { .ziel-grid { grid-template-columns: repeat(2, 1fr); } }
  .ziel-btn { background: #111; border: 1px solid #2a2a2a; border-radius: 6px; padding: 8px 6px; cursor: pointer; text-align: left; display: flex; flex-direction: column; gap: 2px; transition: all 0.15s; }
  .ziel-btn:hover { border-color: #444; }
  .ziel-btn.active { border-color: var(--accent); background: #0d150d; }
  .ziel-icon { font-size: 1rem; color: #555; }
  .ziel-btn.active .ziel-icon { color: var(--accent); }
  .ziel-name { font-size: 0.8rem; color: var(--fg); font-weight: 500; }
  .ziel-desc { font-size: 0.7rem; color: #666; }
  .ziel-btn.active .ziel-desc { color: #7a9; }
  .ziel-info { margin-top: 8px; padding: 10px 12px; background: #0a0f0a; border-left: 2px solid var(--accent); border-radius: 0 4px 4px 0; font-size: 0.8rem; color: #999; line-height: 1.55; display: none; }
  .ziel-info.visible { display: block; }
  .ziel-info strong { color: var(--fg); }
  .ziel-info .step { color: #7a9; margin-right: 4px; }
  /* Help-Tooltips */
  .help-toggle { display: inline-block; margin-left: 6px; color: #444; cursor: pointer; font-size: 0.75rem; border: 1px solid #333; border-radius: 50%; width: 16px; height: 16px; text-align: center; line-height: 14px; vertical-align: middle; }
  .help-toggle:hover { color: #888; border-color: #555; }
  .help-text { display: none; font-size: 0.78rem; color: #666; margin-top: 5px; padding: 7px 10px; background: #0c0c0c; border-radius: 4px; line-height: 1.5; }
  .help-text.open { display: block; }
  .section-label { display: flex; align-items: center; font-size: 0.82rem; color: #aaa; margin-bottom: 6px; }

  .img2img-wrap { margin: 12px 0; border: 1px solid #333; border-radius: 6px; overflow: hidden; }
  .img2img-toggle { padding: 8px 12px; cursor: pointer; color: #888; font-size: 0.85rem; user-select: none; }
  .img2img-toggle:hover { color: var(--fg); }
  .img2img-body { display: none; padding: 12px; border-top: 1px solid #333; }
  .img2img-body.open { display: block; }
  .img2img-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 8px; }
  .upload-label { cursor: pointer; padding: 5px 10px; border: 1px solid #555; border-radius: 4px; font-size:0.82rem; }
  .upload-label:hover { border-color: var(--accent); }
  #initImgInput { display: none; }
  #initImgPreview { max-width: 180px; max-height: 180px; border-radius: 4px; border: 1px solid #444; margin-bottom: 8px; display: none; }
  .btn-clear-img { background: none; border: 1px solid #555; color: #888; border-radius: 4px; padding: 4px 8px; cursor: pointer; font-size:0.8rem; }
  .btn-clear-img:hover { border-color: #e55; color: #e55; }
  .strength-row { display: flex; flex-direction: column; gap: 4px; }
  .strength-row label { font-size: 0.82rem; color: #aaa; }
  .strength-row input[type=range] { width: 100%; accent-color: var(--accent); }
  .strength-labels { display: flex; justify-content: space-between; font-size: 0.75rem; color: #666; margin-top: 2px; }
  .strength-presets { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 6px; }
  .preset-btn { background: #1a1a1a; border: 1px solid #3a3a3a; color: #999; border-radius: 4px; padding: 4px 10px; cursor: pointer; font-size: 0.78rem; transition: all 0.15s; }
  .preset-btn:hover { border-color: #666; color: var(--fg); }
  .preset-btn.active { border-color: var(--accent); color: var(--accent); background: #1a1f1a; }
  #imgThumbGrid { display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0; }
  .thumb-wrap { position: relative; display: inline-block; }
  .thumb-wrap img { width: 80px; height: 80px; object-fit: cover; border-radius: 4px; border: 1px solid #444; }
  .thumb-rm { position: absolute; top: -4px; right: -4px; background: #333; border: none; color: #e55; cursor: pointer; border-radius: 50%; width: 18px; height: 18px; font-size: 10px; line-height: 18px; text-align: center; padding: 0; }
  .url-row { display: flex; gap: 6px; margin: 6px 0 4px; }
  .url-input { flex: 1; background: #111; border: 1px solid #333; color: var(--fg); border-radius: 4px; padding: 5px 8px; font-size: 0.8rem; font-family: inherit; }
  .url-input:focus { outline: none; border-color: #555; }
  .btn-url-add { background: #1a1a1a; border: 1px solid #444; color: #aaa; border-radius: 4px; padding: 5px 12px; cursor: pointer; font-size: 0.8rem; white-space: nowrap; }
  .btn-url-add:hover { border-color: var(--accent); color: var(--accent); }
  .url-error { font-size: 0.78rem; color: #c55; min-height: 1em; margin-bottom: 4px; }
  .mix-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 0.82rem; }
  .mix-row select { background: #1a1a1a; border: 1px solid #444; color: var(--fg); border-radius: 4px; padding: 3px 6px; }
  .mix-method-btn { background: #111; border: 1px solid #2a2a2a; color: #888; border-radius: 5px; padding: 7px 14px; cursor: pointer; font-size: 0.82rem; transition: all 0.15s; }
  .mix-method-btn:hover { border-color: #555; color: var(--fg); }
  .mix-method-btn.active { border-color: var(--accent); color: var(--accent); background: #0d150d; }
  .auto-info { font-size: 0.8rem; color: #888; min-height: 1.2em; margin-bottom: 6px; transition: color 0.3s; }
  .auto-info.chosen { color: var(--accent); }
  .refine-wrap { width: 100%; margin-top: 14px; border-top: 1px solid #2a2a2a; padding-top: 12px; }
  .refine-label { font-size: 0.78rem; color: #666; margin-bottom: 6px; letter-spacing: 0.05em; text-transform: uppercase; }
  .refine-textarea { width: 100%; background: #111; border: 1px solid #333; color: var(--fg); border-radius: 5px; padding: 8px 10px; font-size: 0.85rem; resize: vertical; min-height: 60px; box-sizing: border-box; font-family: inherit; }
  .refine-textarea:focus { outline: none; border-color: #555; }
  .refine-controls { display: flex; flex-wrap: wrap; align-items: flex-end; gap: 12px; margin-top: 8px; }
  .refine-strength-row { display: flex; flex-direction: column; gap: 3px; flex: 1; min-width: 160px; }
  .refine-strength-row label { font-size: 0.8rem; color: #aaa; }
  .refine-strength-row input[type=range] { accent-color: var(--accent); }
  .refine-check { font-size: 0.8rem; color: #888; display: flex; align-items: center; gap: 5px; cursor: pointer; }
  .btn-refine { background: #1a1a1a; border: 1px solid #555; color: var(--fg); padding: 7px 16px; border-radius: 5px; cursor: pointer; font-size: 0.85rem; white-space: nowrap; }
  .btn-refine:hover { border-color: var(--accent); color: var(--accent); }

  .btn-generate {
    width: 100%;
    padding: 14px;
    background: var(--accent2);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    cursor: pointer;
    transition: background 0.2s, opacity 0.2s;
  }

  .btn-generate:hover:not(:disabled) { background: var(--accent); color: #000; }
  .btn-generate:disabled { opacity: 0.45; cursor: not-allowed; }

  .progress-wrap {
    display: none;
    flex-direction: column;
    gap: 8px;
  }

  .progress-wrap.visible { display: flex; }

  .progress-bar-bg {
    width: 100%;
    height: 6px;
    background: #222;
    border-radius: 3px;
    overflow: hidden;
  }

  .progress-bar-fill {
    height: 100%;
    background: var(--accent);
    border-radius: 3px;
    transition: width 0.5s ease;
    width: 0%;
  }

  .progress-label {
    font-size: 12px;
    color: var(--muted);
    text-align: right;
  }

  .result-wrap {
    display: none;
    flex-direction: column;
    gap: 14px;
    align-items: center;
  }

  .result-wrap.visible { display: flex; }

  .result-img {
    width: 100%;
    border-radius: 8px;
    border: 1px solid var(--border);
    cursor: zoom-in;
  }

  .btn-download {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    background: #222;
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--accent);
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    transition: background 0.2s, border-color 0.2s;
  }

  .btn-download:hover { background: #2a2a2a; border-color: var(--accent2); }

  .error-box {
    display: none;
    padding: 12px 16px;
    background: #200;
    border: 1px solid #500;
    border-radius: 8px;
    color: var(--error);
    font-size: 13px;
  }

  .error-box.visible { display: block; }

  .queue-hint {
    display: none;
    font-size: 12px;
    color: var(--muted);
    text-align: center;
    padding: 6px 0;
  }

  .queue-hint.visible { display: block; }

  footer {
    margin-top: 32px;
    font-size: 11px;
    color: #444;
    text-align: center;
  }
</style>
</head>
<body>

<div class="card">
  <div class="card-header">
    <span class="card-title">&#9670; Bildgenerator</span>
    <div class="status-badge" id="statusBadge">
      <div class="status-dot" id="statusDot"></div>
      <span id="statusText">Verbinde...</span>
    </div>
  </div>

  <div class="card-body">

    <!-- ═══ ZIEL-AUSWAHL ═══ -->
    <div class="ziel-section">
      <div class="ziel-label">Was möchtest du tun?</div>
      <div class="ziel-grid">
        <button class="ziel-btn active" data-ziel="neu" onclick="setZiel('neu', this)">
          <span class="ziel-icon">✦</span>
          <span class="ziel-name">Neues Bild</span>
          <span class="ziel-desc">Prompt → Bild</span>
        </button>
        <button class="ziel-btn" data-ziel="anpassen" onclick="setZiel('anpassen', this)">
          <span class="ziel-icon">⟳</span>
          <span class="ziel-name">Bild anpassen</span>
          <span class="ziel-desc">1 Referenz + Änderung</span>
        </button>
        <button class="ziel-btn" data-ziel="mixen" onclick="setZiel('mixen', this)">
          <span class="ziel-icon">⊕</span>
          <span class="ziel-name">Bilder mixen</span>
          <span class="ziel-desc">2–6 Bilder kombinieren</span>
        </button>
        <button class="ziel-btn" data-ziel="weiter" onclick="setZiel('weiter', this)">
          <span class="ziel-icon">↗</span>
          <span class="ziel-name">Weiterentwickeln</span>
          <span class="ziel-desc">Ergebnis als Basis</span>
        </button>
        <button class="ziel-btn" data-ziel="person" onclick="setZiel('person', this)">
          <span class="ziel-icon">◎</span>
          <span class="ziel-name">Person übernehmen</span>
          <span class="ziel-desc">Fotos → neue Szene</span>
        </button>
        <button class="ziel-btn" data-ziel="kombi" onclick="setZiel('kombi', this)">
          <span class="ziel-icon">⧉</span>
          <span class="ziel-name">Semantisch kombinieren</span>
          <span class="ziel-desc">Bild 1 + Bild 2 verstehen</span>
        </button>
      </div>
      <div class="ziel-info" id="zielInfo"></div>
    </div>

    <!-- ═══ MIX-METHODE (nur bei "Bilder mixen") ═══ -->
    <div id="mixMethodPanel" style="display:none; margin-bottom:14px; padding:12px 14px; background:#0e150e; border:1px solid #2a3a2a; border-radius:6px;">
      <div style="font-size:0.75rem; color:#555; text-transform:uppercase; letter-spacing:0.07em; margin-bottom:10px;">Wie sollen die Bilder kombiniert werden?</div>
      <div id="mixMethodBtns" style="display:flex; flex-wrap:wrap; gap:8px;">
        <button class="mix-method-btn active" data-mix="auto"    onclick="setMixMethod('auto',    this)">🤖 Auto (KI entscheidet)</button>
        <button class="mix-method-btn"        data-mix="blend"   onclick="setMixMethod('blend',   this)">Blend — Stile verschmelzen</button>
        <button class="mix-method-btn"        data-mix="collage" onclick="setMixMethod('collage', this)">Collage — alle Teile sichtbar</button>
      </div>
      <div id="mixMethodDesc" style="margin-top:8px; font-size:0.78rem; color:#666; line-height:1.5;"></div>
    </div>

    <div>
      <label for="imageName">Name der Datei <span style="color:#555; font-size:10px; text-transform:none; letter-spacing:0">(optional — leer = automatisch)</span></label>
      <input type="text" id="imageName" placeholder="z.B. portrait-nacht oder drache-blau" autocomplete="off"
             style="width:100%; background:#111; border:1px solid #2a2a2a; border-radius:8px; color:#e0e0e0; font-size:14px; padding:10px 14px; outline:none; font-family:inherit; transition:border-color 0.2s;"
             onfocus="this.style.borderColor='#3a7d50'" onblur="this.style.borderColor='#2a2a2a'">
    </div>

    <div>
      <label for="prompt">Beschreibe dein Bild</label>
      <textarea id="prompt" placeholder="z.B. ein roter Apfel auf einem Holztisch, abendliches Licht..."></textarea>
    </div>

    <div id="modelHint" style="display:none; padding:12px 16px; border-radius:8px; font-size:12px; line-height:1.8;"></div>

    <div>
      <label for="negativePrompt">Negativer Prompt <span style="color:#555; font-size:10px; text-transform:none; letter-spacing:0">(was NICHT im Bild sein soll)</span></label>
      <textarea id="negativePrompt" placeholder="z.B. blurry, distorted, ugly, deformed, watermark..." style="min-height:54px;"></textarea>
    </div>

    <div class="row-2">
      <div>
        <label for="modelSel">Modell</label>
        <select id="modelSel" onchange="onModelChange()">
          MODEL_OPTIONS
        </select>
      </div>
      <div>
        <label for="style">Stil</label>
        <select id="style">
          STYLE_OPTIONS
        </select>
      </div>
    </div>

    <!-- Modell-Info-Tabelle -->
    <div class="modell-tabelle-wrap">
      <table class="modell-tabelle">
        <thead>
          <tr>
            <th>Modell</th>
            <th>Typ</th>
            <th>Zeit 512×512</th>
            <th>Stärke</th>
            <th>Größe</th>
            <th>Zensur</th>
          </tr>
        </thead>
        <tbody id="modellTableBody">
          MODEL_TABLE_ROWS
        </tbody>
      </table>
    </div>
    <p class="zensur-hint">◑ kein Filter = kein Safety-Checker, aber Training kann explizite Inhalte trotzdem einschränken. ✓ explizit uncensored = für NSFW-Inhalte trainiert (Pony Diffusion).</p>

    <div>
      <label for="resolution">Auflösung</label>
      <select id="resolution" onchange="onResolutionChange()">
        RESOLUTION_OPTIONS
      </select>
      <div class="zeit-display" id="zeitDisplay">Geschätzte Zeit: —</div>
    </div>

    <div class="img2img-wrap" id="img2imgWrap">
      <div class="img2img-toggle" onclick="toggleImg2Img()">
        <span id="img2imgToggleLabel">&#43; Referenzbilder (img2img)</span>
        <span class="help-toggle" onclick="event.stopPropagation(); toggleHelp('helpImg2Img')" title="Was ist das?">?</span>
      </div>
      <div class="help-text" id="helpImg2Img">
        <strong>Referenzbilder</strong> = Bilder die als Ausgangsbasis dienen. Das neue Bild entsteht ausgehend von diesen Bildern.<br><br>
        <strong>1 Bild hochladen →</strong> Bild anpassen. Die Änderungsstärke bestimmt wie stark sich das Ergebnis vom Original unterscheidet.<br>
        &nbsp;&nbsp;• <em>subtil (0.25):</em> kleine Änderungen, Bild bleibt sehr ähnlich<br>
        &nbsp;&nbsp;• <em>mittel (0.5):</em> merkliche Änderungen, Grundstruktur bleibt<br>
        &nbsp;&nbsp;• <em>stark (0.75):</em> starke Änderungen, nur grobe Struktur bleibt<br>
        &nbsp;&nbsp;• <em>neu (1.0):</em> ignoriert das Original fast komplett<br><br>
        <strong>2–6 Bilder hochladen →</strong> Bilder werden gemischt (Pixel-Blend oder Collage), das Ergebnis ist die Basis.<br>
        &nbsp;&nbsp;• <em>Blend:</em> alle Bilder übereinander gelegt (Stile verschmelzen)<br>
        &nbsp;&nbsp;• <em>Collage:</em> Bilder nebeneinander, das Modell sieht alle gleichzeitig<br><br>
        <strong>Limitation:</strong> Das Modell "weiß" nicht dass Bild 1 eine Person und Bild 2 eine Katze ist — es sieht nur Pixel. Für semantisches Verstehen → FLUX Kontext (bald verfügbar).
      </div>
      <div class="img2img-body" id="img2imgBody">
        <div class="img2img-row">
          <label class="upload-label" for="initImgInput">Bilder wählen (bis 6 · PNG/JPG/WebP)</label>
          <input type="file" id="initImgInput" accept="image/png,image/jpeg,image/webp" multiple onchange="onInitImgChange()">
          <button class="btn-clear-img" id="clearInitImgBtn" onclick="clearAllImgs()" style="display:none">✕ alle entfernen</button>
        </div>
        <div class="url-row">
          <input type="url" id="imgUrlInput" class="url-input" placeholder="oder Bild-URL einfügen (https://... oder /pfad/zum/bild.png)" autocomplete="off">
          <button class="btn-url-add" onclick="addImgFromUrl()">+ laden</button>
        </div>
        <div id="urlError" class="url-error"></div>
        <div id="imgThumbGrid"></div>
        <div class="mix-row" id="mixRow" style="display:none">
          <label>Mix-Methode:</label>
          <select id="mixType">
            <option value="auto">🤖 Auto (KI entscheidet)</option>
            <option value="blend">Blend (Pixel-Durchschnitt)</option>
            <option value="collage">Collage (nebeneinander)</option>
          </select>
        </div>
        <div class="strength-row">
          <label>Änderungsstärke
            <span class="help-toggle" onclick="toggleHelp('helpStrength')" title="Was bedeutet die Stärke?">?</span>
          </label>
          <div class="help-text" id="helpStrength">
            Wie stark das Ergebnis vom Referenzbild abweichen darf.<br>
            <strong>🤖 Auto</strong> = erkennt aus deinem Prompt ob du subtile oder starke Änderungen willst.<br>
            Tipp: für "andere Kleidung" → 0.25–0.4 | für "anderer Stil" → 0.6–0.8 | für "nur grob als Basis" → 1.0
          </div>
          <div class="strength-presets" id="strengthPresets">
            <button class="preset-btn" data-val="auto"  onclick="setStrengthPreset('auto',  this)">🤖 Auto</button>
            <button class="preset-btn" data-val="0.25"  onclick="setStrengthPreset('0.25',  this)">subtil · 0.25</button>
            <button class="preset-btn active" data-val="0.5" onclick="setStrengthPreset('0.5', this)">mittel · 0.5</button>
            <button class="preset-btn" data-val="0.75"  onclick="setStrengthPreset('0.75',  this)">stark · 0.75</button>
            <button class="preset-btn" data-val="1.0"   onclick="setStrengthPreset('1.0',   this)">neu · 1.0</button>
          </div>
          <input type="range" id="strengthSlider" min="0.1" max="1.0" step="0.05" value="0.5"
                 oninput="onStrengthSlide(this.value)">
          <div class="strength-labels"><span>kaum verändern</span><span id="strengthVal">0.5</span><span>komplett neu</span></div>
        </div>
      </div>
    </div>
    <div class="auto-info" id="autoInfo"></div>

    <button class="btn-generate" id="btnGenerate" onclick="startGeneration()">
      Bild generieren
    </button>

    <div class="queue-hint" id="queueHint">
      Ein anderes Bild wird gerade generiert — dein Auftrag wartet in der Warteschlange.
    </div>

    <div class="progress-wrap" id="progressWrap">
      <div class="progress-bar-bg">
        <div class="progress-bar-fill" id="progressFill"></div>
      </div>
      <div class="progress-label" id="progressLabel">Starte...</div>
    </div>

    <div class="error-box" id="errorBox"></div>

    <div class="result-wrap" id="resultWrap">
      <img class="result-img" id="resultImg" src="" alt="Generiertes Bild" onclick="openFull(this.src)">
      <a class="btn-download" id="btnDownload" href="#" download="bild.png">
        &#8595; Herunterladen
      </a>
      <div class="refine-wrap" id="refineWrap">
        <div class="refine-label">Weiterentwickeln</div>
        <textarea id="refinePrompt" class="refine-textarea" placeholder="Was soll sich ändern? z.B. 'mach den Himmel dramatischer' · 'füge einen Hut hinzu' · 'andere Farbe, blau'"></textarea>
        <div class="refine-controls">
          <div class="refine-strength-row">
            <label>Änderungsstärke</label>
            <div class="strength-presets" id="refineStrengthPresets">
              <button class="preset-btn" data-val="auto"  onclick="setRefineStrengthPreset('auto', this)">🤖 Auto</button>
              <button class="preset-btn active" data-val="0.25" onclick="setRefineStrengthPreset('0.25', this)">subtil · 0.25</button>
              <button class="preset-btn" data-val="0.5"   onclick="setRefineStrengthPreset('0.5',  this)">mittel · 0.5</button>
              <button class="preset-btn" data-val="0.75"  onclick="setRefineStrengthPreset('0.75', this)">stark · 0.75</button>
            </div>
            <input type="range" id="refineStrength" min="0.1" max="1.0" step="0.05" value="0.25"
                   oninput="onRefineStrengthSlide(this.value)">
            <div class="strength-labels"><span>subtil</span><span id="refineStrengthVal">0.25</span><span>stark</span></div>
          </div>
          <label class="refine-check"><input type="checkbox" id="keepOrigPrompt" checked> Original-Prompt beibehalten</label>
          <button class="btn-refine" onclick="startRefinement()">&#8635; Verfeinern</button>
        </div>
      </div>
    </div>
  </div>
</div>

<footer>flextrawurst.de &mdash; sd.cpp &middot; CPU-only</footer>

<script>
const BASE_URL = '';
const MODELLE = MODELS_JS_DATA;

const RES_PIXEL = {
  "128x128":   128*128,
  "256x256":   256*256,
  "512x512":   512*512,
  "640x480":   640*480,
  "666x666":   666*666,
  "768x576":   768*576,
  "768x768":   768*768,
  "768x1024":  768*1024,
  "960x540":   960*540,
  "1024x768":  1024*768,
  "1024x1024": 1024*1024,
  "1280x720":  1280*720,
  "1280x960":  1280*960,
  "1336x768":  1336*768,
  "1440x900":  1440*900,
  "1920x1080": 1920*1080,
};

let currentJobId = null;
let pollTimer = null;

// --- Zeitschätzung ---
function getStepsForRes(m, resKey) {
  if (!m.steps_res || !m.steps_res.length) return m.steps;
  const [rw, rh] = (resKey || '512x512').split('x').map(Number);
  const maxDim = Math.max(rw || 512, rh || 512);
  for (const [maxD, s] of m.steps_res) {
    if (maxDim <= maxD) return s;
  }
  return m.steps_res[m.steps_res.length - 1][1];
}

function calcZeit(modelKey, resKey) {
  const m = MODELLE[modelKey];
  if (!m) return "—";
  const [rw, rh] = (resKey || '512x512').split('x').map(Number);
  const pixels  = (rw || 512) * (rh || 512);
  const base    = 512 * 512;
  const ratio   = pixels / base;
  const isFlux  = m.typ === "FLUX" || m.typ === "FLUX_KONTEXT";
  const secsPerStep = isFlux ? 73 : 335;
  const steps   = getStepsForRes(m, resKey);
  const total   = Math.round(secsPerStep * ratio * steps);
  return formatDauer(total);
}

function formatDauer(secs) {
  if (secs >= 3600) {
    const h = Math.floor(secs/3600);
    const m = Math.floor((secs%3600)/60);
    return m > 0 ? `~${h}h ${m}min` : `~${h}h`;
  }
  if (secs >= 60) {
    const m = Math.floor(secs/60);
    const s = secs % 60;
    return s > 0 ? `~${m} Min ${s} Sek` : `~${m} Min`;
  }
  return `~${secs} Sek`;
}

function updateZeitDisplay() {
  const mKey = document.getElementById('modelSel').value;
  const rKey = document.getElementById('resolution').value;
  document.getElementById('zeitDisplay').textContent = 'Geschätzte Zeit: ' + calcZeit(mKey, rKey);
}

const C = (t) => `<code style="background:#111;padding:2px 6px;border-radius:3px;color:#eee;font-size:11px;">${t}</code>`;
const CB = (t) => `<code style="background:#111;padding:3px 9px;border-radius:3px;color:#eee;display:inline-block;margin:3px 0;">${t}</code>`;

const MODEL_HINTS = {
  sdxl_lightning: {
    bg: '#0e0e1a', border: '#2a2a55', color: '#8888cc',
    html: `<strong style="font-size:13px;">SDXL-Lightning — nur 4 Schritte, dafür anders</strong><br><br>
Lightning ist ein destilliertes Modell: es wurde darauf trainiert in 4 Schritten das gleiche zu erreichen was normale Modelle in 20–30 brauchen.
Das klingt toll — hat aber einen Haken: der CFG-Scale muss niedrig bleiben (hier 2.0). Höher drehen = schlechtere Qualität, nicht besser.<br><br>
<strong>Prompt-Stil:</strong> kommagetrennte englische Tags, ähnlich wie Stable Diffusion 1.5.<br>
${CB('a woman sitting in a park, golden hour, cinematic lighting, detailed, sharp')}<br><br>
<strong>Gut für:</strong> schnelle Entwürfe, Stil-Tests, einfache Szenen.<br>
<strong>Schwächer bei:</strong> sehr detaillierten Gesichtern, komplexer Komposition, Text im Bild.`
  },
  juggernaut_xl: {
    bg: '#0f0d0d', border: '#3a2020', color: '#cc8888',
    html: `<strong style="font-size:13px;">Juggernaut XL v9 — fotorealistisch, stark bei Menschen</strong><br><br>
Juggernaut wurde auf einer kuratierten Sammlung hochwertiger Fotos trainiert — besonders stark bei Porträts, Haut, Licht und realistischen Texturen.
Der CFG-Scale 7.0 ist bewusst höher als bei FLUX — das Modell braucht das um Details zu schärfen.<br><br>
<strong>Prompt-Qualitäts-Booster (vorne rein):</strong><br>
${CB('RAW photo, 8k uhd, dslr, sharp focus, high quality, film grain')}<br><br>
<strong>Negativer Prompt hilft hier besonders:</strong><br>
${CB('bad anatomy, blurry, low quality, ugly, deformed, watermark, extra limbs')}<br><br>
<strong>Gut für:</strong> Menschen, Gesichter, Porträts, realistische Szenen.<br>
<strong>Hinweis zur Zensur:</strong> kein Safety-Checker, aber das Modell wurde nicht explizit auf NSFW-Inhalte trainiert — Ergebnisse variieren.`
  },
  pony: {
    bg: '#1a1200', border: '#4a3800', color: '#c8a030',
    html: `<strong style="font-size:13px;">Pony Diffusion V6 XL — das einzige wirklich uncensored Modell hier</strong><br><br>
Pony wurde auf Danbooru trainiert — einer riesigen Datenbank mit Anime- und Illustrations-Bildern, die alle mit Tags bewertet sind.
${C('score_9')} = bestes 1% der Bilder. ${C('score_4')} = unterste 10%. Das Modell hat gelernt: hohe Score = gutes Bild.
Ohne diese Tags generiert es im Mittelmaß. Mit ihnen zieht es das Beste aus seinem Training.<br><br>
<strong>Prompt immer starten mit:</strong><br>
${CB('score_9, score_8_up, score_7_up')}<br><br>
<strong>Für explizite Inhalte zusätzlich:</strong><br>
${CB('explicit, nude, nsfw')}<br><br>
<strong>Negativer Prompt empfohlen:</strong><br>
${CB('score_6, score_5, score_4, low quality, bad anatomy, clothes')}<br><br>
<strong>Stil:</strong> eher Illustration/Anime als Foto. Für fotorealistisch → Juggernaut oder RealVisXL.<br><br>
<strong>⏱ Geschwindigkeit:</strong> SDXL-Modelle sind auf dieser CPU langsamer als FLUX — das liegt an der Architektur, nicht den Steps.
Pony läuft mit 8 Steps (wie alle SDXL-Modelle hier). 128×128 dauert ~3 Min, 512×512 ~45 Min.
Für schnelle Tests: kleine Auflösung wählen, Ergebnis prüfen, dann größer generieren.`
  },
  realvis_xl: {
    bg: '#0d0f0d', border: '#1e3020', color: '#78bb88',
    html: `<strong style="font-size:13px;">RealVisXL V5 — realistisch, stark bei Texturen und Licht</strong><br><br>
RealVisXL ist auf Fotorealismus spezialisiert — ähnlich wie Juggernaut, aber mit anderem Schwerpunkt.
Besonders stark bei Materialien (Stoff, Haut, Metall), natürlichem Licht und Umgebungsdetails.
Weniger auf Porträts ausgerichtet als Juggernaut, dafür besser bei Szenen und Objekten.<br><br>
<strong>Prompt-Tipp:</strong><br>
${CB('photorealistic, ultra detailed, natural lighting, sharp focus')}<br><br>
<strong>Negativer Prompt:</strong><br>
${CB('cartoon, anime, painting, illustration, low quality, blurry, noise')}<br><br>
<strong>Gut für:</strong> Landschaften, Objekte, Räume, Nahaufnahmen mit Textur.<br>
<strong>Hinweis zur Zensur:</strong> kein Safety-Checker, aber Training enthält keine NSFW-Daten — für explizite Inhalte → Pony Diffusion.`
  },
  flux_schnell: {
    bg: '#0a0f14', border: '#1a3050', color: '#6aaacc',
    html: `<strong style="font-size:13px;">FLUX.1-schnell — natürliche Sprache statt Tags</strong><br><br>
FLUX versteht echte Sätze — keine kommagetrennte Tag-Listen nötig.
Schreib einfach was du sehen willst, wie du es einem Menschen erklären würdest.<br><br>
<strong>So promten:</strong><br>
${CB('a woman sitting by a window at night, rain outside, soft lamp light, photorealistic')}<br><br>
<strong>Statt:</strong><br>
${CB('woman, window, night, rain, lamp, photo, realistic, detailed')} ← unnötig bei FLUX<br><br>
<strong>Wichtig:</strong> Englisch funktioniert deutlich besser als Deutsch — FLUX wurde fast ausschließlich auf englischen Texten trainiert.<br><br>
<strong>4 Steps reichen.</strong> Mehr Steps bei "schnell" bringt keinen Vorteil — das Modell ist dafür nicht ausgelegt.<br><br>
<strong>Inhalte:</strong> kein Safety-Checker, aber das Training hat implizite Einschränkungen — explizite Inhalte entstehen selten. Für NSFW → Pony Diffusion.<br><br>
<strong>⚠ RAM:</strong> ~17 GB beim Laden. Erster Start dauert mehrere Minuten — danach schnell.`
  },
  flux_dev: {
    bg: '#0a0f14', border: '#1a3050', color: '#6aaacc',
    html: `<strong style="font-size:13px;">FLUX.1-dev — bestes Qualitäts-Modell hier, aber langsamer</strong><br><br>
FLUX.1-dev ist die vollwertige Version — 20 Steps statt 4, deutlich bessere Komposition, mehr Details, schärfere Ergebnisse.
Gleiche Regeln wie FLUX.1-schnell: natürliche Sätze auf Englisch, keine Tag-Listen.<br><br>
<strong>Prompt-Stil:</strong><br>
${CB('a detailed portrait of an old fisherman, weathered face, harbor at dusk, cinematic, sharp')}<br><br>
<strong>Wann dev statt schnell:</strong> immer wenn das Ergebnis wirklich gut sein muss — Portraits, komplexe Szenen, viele Details im Bild.<br><br>
<strong>Inhalte:</strong> Gleiche Einschränkung wie schnell — explizite Inhalte entstehen kaum, auch ohne Safety-Checker.
Das ist Training, kein Filter. Für NSFW → Pony Diffusion.<br><br>
<strong>⚠ RAM:</strong> ~17 GB beim Laden. Bei wenig freiem RAM langsam wegen Swap — nicht wirklich eingefroren, nur wartend.`
  },
  flux_kontext: {
    bg: '#0f0a14', border: '#301a50', color: '#aa88cc',
    html: `<strong style="font-size:13px;">FLUX.1-Kontext — Bild bearbeiten, keine Neuerstellung</strong><br><br>
Kontext ist ein anderes Modell als die anderen: es erstellt kein Bild aus dem Nichts.
Es nimmt ein <strong>Referenzbild</strong> und verändert es anhand deines Prompts — die Grundstruktur bleibt, die Szene/Details ändern sich.<br><br>
<strong>Ohne Referenzbild:</strong> läuft als normales FLUX txt2img — keine Identitätserkennung, kein Unterschied zu FLUX.1-dev.<br><br>
<strong>Mit Referenzbild(ern):</strong> Mehrere Fotos werden zusammengeblended und dem Modell als Ausgangsbasis gegeben.
Das Modell "liest" Pose, Lichtstimmung und grobe Strukturen — aber es erkennt keine Identität wie ein Mensch es täte.<br><br>
<strong>Prompt beschreibt die Änderung, nicht das Bild:</strong><br>
${CB('the person from the reference image in a dark forest at night, cinematic lighting')}<br>
${CB('same pose, but change background to a snowy mountain, sunset')}<br><br>
<strong>Gut für:</strong> Szenen tauschen, Licht ändern, Stil übertragen.<br>
<strong>Nicht für:</strong> Gesichtsidentität präzise übernehmen (dafür bräuchte es PhotoMaker oder IP-Adapter — noch nicht integriert).<br><br>
<strong>⚠ RAM-Hinweis:</strong> Dieses Modell belegt ~17 GB RAM beim Laden (Modell + Encoder). Bei wenig freiem RAM wirkt die Generation wie eingefroren — sie läuft aber noch, nur sehr langsam über Swap. Geduld oder zuerst andere Prozesse schließen.`
  },
};

function onModelChange() {
  const mKey = document.getElementById('modelSel').value;
  document.querySelectorAll('#modellTableBody tr').forEach(tr => {
    tr.classList.toggle('aktiv', tr.dataset.model === mKey);
  });
  updateZeitDisplay();
  const hintEl = document.getElementById('modelHint');
  const hint = MODEL_HINTS[mKey];
  if (hint) {
    hintEl.style.display = 'block';
    hintEl.style.background = hint.bg;
    hintEl.style.border = '1px solid ' + hint.border;
    hintEl.style.color = hint.color;
    hintEl.innerHTML = hint.html;
  } else {
    hintEl.style.display = 'none';
  }
}

function onResolutionChange() {
  updateZeitDisplay();
}

// Init
onModelChange();

// --- Health Check ---
function checkHealth() {
  fetch(BASE_URL + '/api/health')
    .then(r => r.ok ? r.json() : Promise.reject())
    .then(() => {
      document.getElementById('statusDot').className  = 'status-dot online';
      document.getElementById('statusText').textContent = 'Generator aktiv';
    })
    .catch(() => {
      document.getElementById('statusDot').className  = 'status-dot offline';
      document.getElementById('statusText').textContent = 'Generator nicht erreichbar';
    });
}

checkHealth();
setInterval(checkHealth, 10000);

// --- Ziel-Auswahl ---
const ZIEL_INFO = {
  neu: `<span class="step">1.</span> <strong>Prompt schreiben</strong> — beschreibe was du sehen willst.<br>
        <span class="step">2.</span> <strong>Modell wählen</strong> — oder 🤖 Auto lassen.<br>
        <span class="step">3.</span> <strong>Auflösung & Stil</strong> wählen, dann generieren.<br>
        <em>Keine Referenzbilder nötig.</em>`,

  anpassen: `<span class="step">1.</span> <strong>Referenzbilder öffnen</strong> (Abschnitt unten aufklappen).<br>
             <span class="step">2.</span> <strong>1 Bild hochladen</strong> das du verändern willst.<br>
             <span class="step">3.</span> <strong>Prompt schreiben</strong>: beschreibe was sich ändern soll (z.B. "andere Kleidung, blau").<br>
             <span class="step">4.</span> <strong>Änderungsstärke</strong>: subtil = kleine Änderung, stark = große Änderung.<br>
             <em>Gut für: Farbe ändern, Stil übertragen, Details tauschen.</em>`,

  mixen: `<span class="step">1.</span> <strong>Referenzbilder öffnen</strong> (Abschnitt unten aufklappen).<br>
          <span class="step">2.</span> <strong>2–6 Bilder hochladen</strong> die kombiniert werden sollen.<br>
          <span class="step">3.</span> <strong>Mix-Methode wählen</strong>: Blend = Stile verschmelzen | Collage = alle sichtbar<br>
          <span class="step">4.</span> <strong>Prompt</strong>: beschreibe was das Ergebnis zeigen soll.<br>
          <em>Limitation: kein semantisches Verstehen — das Modell sieht nur gemischte Pixel, nicht "Person aus Bild 1".</em>`,

  weiter: `Generiere zuerst ein Bild. Danach erscheint unter dem Ergebnis der <strong>Weiterentwickeln-Bereich</strong>.<br>
           <span class="step">1.</span> <strong>Beschreibe was sich ändern soll</strong> (z.B. "mehr Kontrast", "Hut hinzufügen").<br>
           <span class="step">2.</span> <strong>Stärke wählen</strong>: subtil = kleine Anpassung, stark = große Änderung.<br>
           <span class="step">3.</span> Option: Original-Prompt beibehalten = beide Texte werden kombiniert.<br>
           <em>Ideal für schrittweise Verbesserungen.</em>`,

  person: `Mehrere Fotos einer Person hochladen → FLUX Kontext extrahiert Identität → generiert neue Szenen.<br>
           <span class="step">1.</span> <strong>Referenzbilder öffnen</strong> (Abschnitt unten aufklappen).<br>
           <span class="step">2.</span> <strong>2–6 Fotos der Person hochladen</strong> (verschiedene Winkel/Beleuchtung = besser).<br>
           <span class="step">3.</span> <strong>Beschreibe die neue Szene</strong>: "the person from the reference images in a forest at night".<br>
           <em>Verwendet FLUX.1-Kontext — bestes verfügbares Verfahren ohne GPU.</em>`,

  kombi: `FLUX.1-Kontext versteht semantisch: "Person aus Bild 1 mit Katze aus Bild 2".<br>
          <span class="step">1.</span> <strong>Referenzbilder öffnen</strong> (Abschnitt unten aufklappen).<br>
          <span class="step">2.</span> <strong>2–6 Bilder hochladen</strong> (Bilder werden direkt als Kontext übergeben, kein Pixel-Mix).<br>
          <span class="step">3.</span> <strong>Prompt auf Englisch</strong>: "the person from the first image with the cat from the second image in a sunny garden".<br>
          <em>Modell: FLUX.1-Kontext — einziges Verfahren für echte semantische Kombination.</em>`,
};

const ZIEL_SETUP = {
  neu:      { openImg2Img: false, promptPlaceholder: 'z.B. ein roter Apfel auf einem Holztisch, abendliches Licht, fotorealistisch...', forceModel: null },
  anpassen: { openImg2Img: true,  promptPlaceholder: 'Was soll sich ändern? z.B. "andere Kleidung, blau" · "Sommerstil" · "mehr Details im Hintergrund"', forceModel: null },
  mixen:    { openImg2Img: true,  promptPlaceholder: 'Was soll das Ergebnis zeigen? z.B. "vereint die Stile beider Bilder" · "surreal, traumhaft"', forceModel: null },
  weiter:   { openImg2Img: false, promptPlaceholder: 'Erstelle zuerst ein Bild — dann erscheint unten der Weiterentwickeln-Bereich.', forceModel: null },
  person:   { openImg2Img: true,  promptPlaceholder: 'Beschreibe die neue Szene auf Englisch: "the person from the reference images in a forest at night, cinematic lighting"', forceModel: 'flux_kontext' },
  kombi:    { openImg2Img: true,  promptPlaceholder: '"the person from the first image with the cat from the second image in a sunny garden, photorealistic"', forceModel: 'flux_kontext' },
};

let currentZiel = 'neu';

function setZiel(ziel, btn) {
  currentZiel = ziel;
  document.querySelectorAll('.ziel-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  const info = document.getElementById('zielInfo');
  info.innerHTML = ZIEL_INFO[ziel] || '';
  info.classList.toggle('visible', !!ZIEL_INFO[ziel]);

  const setup = ZIEL_SETUP[ziel] || {};
  if (setup.promptPlaceholder)
    document.getElementById('prompt').placeholder = setup.promptPlaceholder;

  const body = document.getElementById('img2imgBody');
  const label = document.getElementById('img2imgToggleLabel');
  if (setup.openImg2Img && !body.classList.contains('open')) {
    body.classList.add('open');
    label.textContent = '− Referenzbilder (img2img)';
  }

  // forceModel: Modell-Select auf flux_kontext setzen wenn nötig
  if (setup.forceModel) {
    const sel = document.getElementById('modelSel');
    if (sel) { sel.value = setup.forceModel; onModelChange(); }
  }

  // Mix-Panel ein-/ausblenden
  const mixPanel = document.getElementById('mixMethodPanel');
  if (mixPanel) mixPanel.style.display = (ziel === 'mixen') ? 'block' : 'none';

  // Alter mixRow (im img2img-Body) synchron halten
  const mixRow = document.getElementById('mixRow');
  if (mixRow) mixRow.style.display = (ziel === 'mixen') ? 'flex' : (uploadedFiles.length > 1 ? 'flex' : 'none');
}

const MIX_DESCS = {
  auto:    'KI analysiert deinen Prompt und wählt automatisch die beste Methode.',
  blend:   'Alle Bilder werden Pixel für Pixel übereinandergelegt — Farben und Stile fließen zusammen.',
  collage: 'Alle Bilder werden nebeneinander gestellt — das Modell sieht alle Teile gleichzeitig.',
};

function setMixMethod(val, btn) {
  document.querySelectorAll('.mix-method-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('mixMethodDesc').textContent = MIX_DESCS[val] || '';
  // alten select synchron halten
  const sel = document.getElementById('mixType');
  if (sel) sel.value = val;
}

function toggleHelp(id) {
  document.getElementById(id).classList.toggle('open');
}

// Beim Start: Ziel-Info für "neu" anzeigen
document.addEventListener('DOMContentLoaded', () => {
  const info = document.getElementById('zielInfo');
  info.innerHTML = ZIEL_INFO['neu'];
  info.classList.add('visible');
});

// --- img2img multi ---
let uploadedFiles = []; // [{file, objectUrl, serverId, serverPath}]

function toggleImg2Img() {
  const body  = document.getElementById('img2imgBody');
  const label = document.getElementById('img2imgToggleLabel');
  const open  = body.classList.toggle('open');
  label.textContent = (open ? '− ' : '+ ') + 'Referenzbilder (img2img)';
}

function onInitImgChange() {
  const input = document.getElementById('initImgInput');
  const newFiles = Array.from(input.files).slice(0, 6 - uploadedFiles.length);
  newFiles.forEach(f => {
    if (uploadedFiles.length >= 6) return;
    uploadedFiles.push({ file: f, objectUrl: URL.createObjectURL(f), serverId: null });
  });
  input.value = '';
  renderThumbs();
}

function renderThumbs() {
  const grid = document.getElementById('imgThumbGrid');
  grid.innerHTML = '';
  uploadedFiles.forEach((entry, i) => {
    const wrap = document.createElement('div');
    wrap.className = 'thumb-wrap';
    const img = document.createElement('img');
    img.src = entry.objectUrl;
    const btn = document.createElement('button');
    btn.className = 'thumb-rm';
    btn.textContent = '✕';
    btn.onclick = () => removeImg(i);
    wrap.appendChild(img);
    wrap.appendChild(btn);
    grid.appendChild(wrap);
  });
  document.getElementById('clearInitImgBtn').style.display = uploadedFiles.length ? 'inline-block' : 'none';
  document.getElementById('mixRow').style.display = (currentZiel === 'mixen' || uploadedFiles.length > 1) ? 'flex' : 'none';
}

function removeImg(i) {
  URL.revokeObjectURL(uploadedFiles[i].objectUrl);
  uploadedFiles.splice(i, 1);
  renderThumbs();
}

function clearAllImgs() {
  uploadedFiles.forEach(e => URL.revokeObjectURL(e.objectUrl));
  uploadedFiles = [];
  renderThumbs();
}

function addImgFromUrl() {
  const input = document.getElementById('imgUrlInput');
  const errEl = document.getElementById('urlError');
  const url   = input.value.trim();
  errEl.textContent = '';
  if (!url) return;
  if (uploadedFiles.length >= 6) { errEl.textContent = 'Maximal 6 Bilder möglich.'; return; }

  const btn = document.querySelector('.btn-url-add');
  btn.textContent = '⏳';
  btn.disabled = true;

  fetch('/api/fetch_url', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  })
  .then(r => r.json())
  .then(data => {
    if (data.error) { errEl.textContent = data.error; return; }
    data.uploads.forEach(u => {
      uploadedFiles.push({ file: null, objectUrl: url, serverId: u.id, serverPath: u.path });
    });
    input.value = '';
    renderThumbs();
  })
  .catch(e => { errEl.textContent = 'Fehler: ' + e.message; })
  .finally(() => { btn.textContent = '+ laden'; btn.disabled = false; });
}

// Enter-Taste im URL-Feld
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('imgUrlInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') { e.preventDefault(); addImgFromUrl(); }
  });
});

// --- Generation ---
// --- Stärke-Presets ---
let strengthIsAuto   = false;
let refStrengthIsAuto = false;

function _autoStrengthFromPrompt(prompt) {
  const p = prompt.toLowerCase();
  if (/subtil|leicht|wenig|kaum|slightly|barely|minimal|sanft/.test(p)) return 0.25;
  if (/stark|sehr|viel|komplett|completely|totally|drastisch|radikal/.test(p)) return 0.8;
  if (/mittel|etwas|somewhat|moderate/.test(p)) return 0.5;
  return 0.45; // neutral default
}

function setStrengthPreset(val, btn) {
  document.querySelectorAll('#strengthPresets .preset-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  strengthIsAuto = val === 'auto';
  if (!strengthIsAuto) {
    const v = parseFloat(val);
    document.getElementById('strengthSlider').value = v;
    document.getElementById('strengthVal').textContent = v.toFixed(2);
  } else {
    document.getElementById('strengthVal').textContent = '🤖';
  }
}

function onStrengthSlide(v) {
  strengthIsAuto = false;
  document.querySelectorAll('#strengthPresets .preset-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('strengthVal').textContent = parseFloat(v).toFixed(2);
}

function getStrength(prompt) {
  if (strengthIsAuto) return _autoStrengthFromPrompt(prompt);
  return parseFloat(document.getElementById('strengthSlider').value);
}

function setRefineStrengthPreset(val, btn) {
  document.querySelectorAll('#refineStrengthPresets .preset-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  refStrengthIsAuto = val === 'auto';
  if (!refStrengthIsAuto) {
    const v = parseFloat(val);
    document.getElementById('refineStrength').value = v;
    document.getElementById('refineStrengthVal').textContent = v.toFixed(2);
  } else {
    document.getElementById('refineStrengthVal').textContent = '🤖';
  }
}

function onRefineStrengthSlide(v) {
  refStrengthIsAuto = false;
  document.querySelectorAll('#refineStrengthPresets .preset-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('refineStrengthVal').textContent = parseFloat(v).toFixed(2);
}

function getRefineStrength(prompt) {
  if (refStrengthIsAuto) return _autoStrengthFromPrompt(prompt);
  return parseFloat(document.getElementById('refineStrength').value);
}

function setAutoInfo(msg, chosen) {
  const el = document.getElementById('autoInfo');
  el.textContent = msg;
  el.className = 'auto-info' + (chosen ? ' chosen' : '');
}

function startGeneration() {
  const prompt = document.getElementById('prompt').value.trim();
  if (!prompt) { showError('Bitte gib einen Prompt ein.'); return; }

  const model      = document.getElementById('modelSel').value;
  const resolution = document.getElementById('resolution').value;
  const style      = document.getElementById('style').value;
  const strength   = getStrength(prompt);
  const mixType    = document.getElementById('mixType').value;

  hideError();
  hideResult();
  setProgress(0, 'Startet...');
  showProgress(true);
  setButton(true);
  setAutoInfo('', false);

  const doGenerate = (uploads) => {
    const negativePrompt = document.getElementById('negativePrompt').value.trim();
    const imageName = document.getElementById('imageName').value.trim();
    const body = { prompt, negative_prompt: negativePrompt, image_name: imageName, model, resolution, style, strength, mix_type: mixType, uploads };
    fetch(BASE_URL + '/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    .then(r => r.json())
    .then(data => {
      if (data.error) throw new Error(data.error);
      currentJobId = data.job_id;
      lastGeneratedPrompt = prompt;
      if (data.model_label) setAutoInfo('→ Modell: ' + data.model_label, true);
      if (data.queued) document.getElementById('queueHint').classList.add('visible');
      startPolling();
    })
    .catch(err => {
      showError('Fehler: ' + err.message);
      showProgress(false);
      setButton(false);
    });
  };

  // Upload files that haven't been uploaded yet
  const toUpload = uploadedFiles.filter(e => !e.serverId);
  if (toUpload.length) {
    setProgress(1, 'Bilder werden hochgeladen...');
    const fd = new FormData();
    toUpload.forEach(e => fd.append('file', e.file));
    fetch(BASE_URL + '/api/upload_init', { method: 'POST', body: fd })
      .then(r => r.json())
      .then(data => {
        if (data.error) throw new Error(data.error);
        if (!data.uploads || !Array.isArray(data.uploads))
          throw new Error('Server-Antwort ungültig: ' + JSON.stringify(data));
        data.uploads.forEach((u, i) => {
          if (toUpload[i]) { toUpload[i].serverId = u.id; toUpload[i].serverPath = u.path; }
        });
        const uploads = uploadedFiles.map(e => ({ id: e.serverId, path: e.serverPath }));
        doGenerate(uploads);
      })
      .catch(err => {
        showError('Upload-Fehler: ' + err.message);
        showProgress(false);
        setButton(false);
      });
  } else if (uploadedFiles.length) {
    const uploads = uploadedFiles.map(e => ({ id: e.serverId, path: e.serverPath }));
    doGenerate(uploads);
  } else {
    doGenerate([]);
  }
}

function startPolling() {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(pollStatus, 2000);
}

function pollStatus() {
  if (!currentJobId) return;
  fetch(BASE_URL + '/api/status/' + currentJobId)
    .then(r => {
      if (r.status === 404) {
        stopPolling();
        showProgress(false);
        setButton(false);
        document.getElementById('queueHint').classList.remove('visible');
        showError('Job nicht mehr gefunden — Server wurde neu gestartet. Bitte neu generieren.');
        return null;
      }
      return r.json();
    })
    .then(data => {
      if (!data) return;
      const pct   = data.progress_pct || 0;
      const eta   = data.eta_seconds  || 0;
      const phase = data.phase || 'loading';
      let label;
      if (phase === 'loading') {
        label = eta > 0 ? `Modell lädt... (~${formatEta(eta)} gesamt)` : 'Modell lädt...';
      } else {
        label = eta > 0 ? `Step ${pct}% · ~${formatEta(eta)} verbl.` : `Step ${pct}%`;
      }
      setProgress(phase === 'loading' ? 2 : pct, label);

      if (data.status === 'done') {
        stopPolling();
        showProgress(false);
        setButton(false);
        document.getElementById('queueHint').classList.remove('visible');
        playDoneSound();
        showResult('/api/image/' + currentJobId);
      } else if (data.status === 'error') {
        stopPolling();
        showProgress(false);
        setButton(false);
        document.getElementById('queueHint').classList.remove('visible');
        showError('Fehler: ' + (data.error || 'Unbekannter Fehler'));
      }
    })
    .catch(() => {});
}

function stopPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
}

function formatEta(secs) {
  if (secs >= 3600) return Math.floor(secs/3600) + 'h ' + Math.floor((secs%3600)/60) + 'min';
  if (secs >= 60) { const m=Math.floor(secs/60); const s=secs%60; return s>0?`${m}min ${s}s`:`${m}min`; }
  return secs + ' Sek';
}

function setButton(disabled) {
  document.getElementById('btnGenerate').disabled = disabled;
  document.getElementById('btnGenerate').textContent = disabled ? 'Generiere...' : 'Bild generieren';
}

function setProgress(pct, label) {
  document.getElementById('progressFill').style.width  = pct + '%';
  document.getElementById('progressLabel').textContent = label;
}

function showProgress(show) {
  document.getElementById('progressWrap').classList.toggle('visible', show);
}

function showResult(url) {
  const img = document.getElementById('resultImg');
  img.src = url;
  const dl  = document.getElementById('btnDownload');
  dl.href   = url;
  const name = document.getElementById('imageName').value.trim();
  dl.download = (name ? name.replace(/[^a-zA-Z0-9_\-äöüÄÖÜß]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '') : 'bild-' + Date.now()) + '.png';
  document.getElementById('resultWrap').classList.add('visible');
}

function hideResult() {
  document.getElementById('resultWrap').classList.remove('visible');
  document.getElementById('resultImg').src = '';
}

let lastGeneratedJobId = null;
let lastGeneratedPrompt = '';

function startRefinement() {
  const changeText  = document.getElementById('refinePrompt').value.trim();
  const keepOrig    = document.getElementById('keepOrigPrompt').checked;
  const strength    = getRefineStrength(changeText);
  const imgUrl      = document.getElementById('resultImg').src;

  if (!changeText) { showError('Bitte beschreibe was sich ändern soll.'); return; }
  if (!imgUrl)     { showError('Kein Bild vorhanden zum Verfeinern.'); return; }

  const finalPrompt = keepOrig && lastGeneratedPrompt
    ? lastGeneratedPrompt + ', ' + changeText
    : changeText;

  hideError();
  hideResult();
  setProgress(1, 'Bild wird geladen...');
  showProgress(true);
  setButton(true);

  fetch(imgUrl)
    .then(r => r.blob())
    .then(blob => {
      const file = new File([blob], 'refine_base.png', { type: 'image/png' });
      uploadedFiles = [{ file, objectUrl: URL.createObjectURL(blob), serverId: null }];
      renderThumbs();

      // Öffne img2img-Sektion damit man sieht was passiert
      const body = document.getElementById('img2imgBody');
      if (!body.classList.contains('open')) toggleImg2Img();

      // Prompt übernehmen
      document.getElementById('prompt').value = finalPrompt;
      document.getElementById('strengthSlider').value = strength;
      document.getElementById('strengthVal').textContent = strength.toFixed(2);

      // Upload + Generate starten
      const fd = new FormData();
      fd.append('file', file);
      return fetch(BASE_URL + '/api/upload_init', { method: 'POST', body: fd });
    })
    .then(r => r.json())
    .then(data => {
      if (data.error) throw new Error(data.error);
      if (!data.uploads || !Array.isArray(data.uploads))
        throw new Error('Upload-Antwort ungültig: ' + JSON.stringify(data));
      data.uploads.forEach((u, i) => {
        if (uploadedFiles[i]) { uploadedFiles[i].serverId = u.id; uploadedFiles[i].serverPath = u.path; }
      });
      renderThumbs();

      const model    = document.getElementById('modelSel').value;
      const resolution = document.getElementById('resolution').value;
      const style    = document.getElementById('style').value;
      const negPr    = document.getElementById('negativePrompt').value.trim();
      const uploads  = uploadedFiles.map(e => ({ id: e.serverId, path: e.serverPath }));
      const body2    = { prompt: finalPrompt, negative_prompt: negPr, model, resolution, style, strength, mix_type: 'blend', uploads };

      return fetch(BASE_URL + '/api/generate', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body2)
      });
    })
    .then(r => r.json())
    .then(data => {
      if (data.error) throw new Error(data.error);
      currentJobId = data.job_id;
      if (data.model_label) setAutoInfo('→ Modell: ' + data.model_label, true);
      if (data.queued) document.getElementById('queueHint').classList.add('visible');
      startPolling();
    })
    .catch(err => {
      showError('Fehler: ' + err.message);
      showProgress(false);
      setButton(false);
    });
}

function playDoneSound() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    [[0, 880, 0.12], [0.13, 1108, 0.18], [0.31, 1318, 0.28]].forEach(([when, freq, dur]) => {
      const osc  = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.type = 'sine';
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0, ctx.currentTime + when);
      gain.gain.linearRampToValueAtTime(0.35, ctx.currentTime + when + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + when + dur);
      osc.start(ctx.currentTime + when);
      osc.stop(ctx.currentTime + when + dur + 0.05);
    });
  } catch(e) {}
}

function showError(msg) {
  const box = document.getElementById('errorBox');
  box.textContent = msg;
  box.classList.add('visible');
}

function hideError() {
  document.getElementById('errorBox').classList.remove('visible');
}

function openFull(src) { window.open(src, '_blank'); }
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/bildgenerator", methods=["GET"])
def ui():
    html = HTML_UI
    html = html.replace("MODEL_OPTIONS",    _build_model_options())
    html = html.replace("STYLE_OPTIONS",    _build_style_options())
    html = html.replace("RESOLUTION_OPTIONS", _build_resolution_options())
    html = html.replace("MODEL_TABLE_ROWS", _build_model_table_rows())
    html = html.replace("MODELS_JS_DATA",   _models_js_data())
    return Response(html, mimetype="text/html", headers={
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Pragma": "no-cache",
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/models", methods=["GET"])
def api_models():
    result = {}
    for key, cfg in MODELS.items():
        result[key] = {
            "label":    cfg["label"],
            "typ":      cfg["typ"],
            "steps":    cfg["steps"],
            "zeit_512": cfg["zeit_512"],
            "staerke":  cfg["staerke"],
            "groesse":  cfg["groesse"],
            "quant":    cfg["quant"],
            "zensur":   cfg.get("zensur", ""),
            "broken":   cfg.get("broken", False),
            "broken_reason": cfg.get("broken_reason", ""),
            "exists":   cfg["path"].exists(),
        }
    return jsonify(result)


@app.route("/api/auto_suggest", methods=["POST"])
def api_auto_suggest():
    data  = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    multi  = bool(data.get("multi", False))
    if not prompt:
        return jsonify({"error": "prompt fehlt"}), 400
    result = auto_suggest(prompt, multi)
    result["zeit_512"] = MODELS.get(result["model"], {}).get("zeit_512", "?")
    result["label"]    = MODELS.get(result["model"], {}).get("label", result["model"])
    return jsonify(result)


@app.route("/api/upload_init", methods=["POST"])
def upload_init():
    files = request.files.getlist("file")
    if not files or all(not f.filename for f in files):
        return jsonify({"error": "Keine Datei"}), 400
    saved = []
    for f in files[:6]:
        if not f.filename:
            continue
        suffix = Path(f.filename).suffix.lower()
        if suffix not in (".png", ".jpg", ".jpeg", ".webp"):
            continue
        tmp_id   = str(uuid.uuid4())
        tmp_path = Path(f"/tmp/bilder_init_{tmp_id}{suffix}")
        f.save(str(tmp_path))
        saved.append({"id": tmp_id, "path": str(tmp_path)})
    if not saved:
        return jsonify({"error": "Keine gültigen Bilddateien"}), 400
    return jsonify({"uploads": saved, "count": len(saved)})


@app.route("/api/fetch_url", methods=["POST"])
def fetch_url():
    import urllib.request, urllib.parse
    data = request.get_json(silent=True) or {}
    url  = (data.get("url") or "").strip()
    if not url:
        return jsonify({"error": "Keine URL"}), 400
    # Nur http/https und lokale Pfade
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https", ""):
        return jsonify({"error": "Nur http/https URLs erlaubt"}), 400
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data_bytes = resp.read(20 * 1024 * 1024)  # max 20MB
    except Exception as e:
        return jsonify({"error": f"Download fehlgeschlagen: {e}"}), 400
    # Suffix aus Content-Type oder URL ableiten
    ct_map = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
    suffix = None
    for ct, s in ct_map.items():
        if ct in content_type:
            suffix = s
            break
    if not suffix:
        ext = Path(parsed.path).suffix.lower()
        if ext in (".png", ".jpg", ".jpeg", ".webp"):
            suffix = ext
    if not suffix:
        return jsonify({"error": "URL führt zu keinem erkannten Bildformat (png/jpg/webp)"}), 400
    tmp_id   = str(uuid.uuid4())
    tmp_path = Path(f"/tmp/bilder_init_{tmp_id}{suffix}")
    tmp_path.write_bytes(data_bytes)
    return jsonify({"uploads": [{"id": tmp_id, "path": str(tmp_path)}], "count": 1})


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}

    prompt           = (data.get("prompt") or "").strip()
    negative_prompt  = (data.get("negative_prompt") or "").strip()
    image_name       = (data.get("image_name") or "").strip()
    resolution       = data.get("resolution", "512x512")
    style_key        = data.get("style", "default")
    model_key        = data.get("model", "flux_schnell")
    strength         = float(data.get("strength", 0.75))
    mix_type         = data.get("mix_type", "auto")
    uploads          = data.get("uploads", [])
    if data.get("init_img_id"):
        uploads = [{"id": data["init_img_id"]}]

    if not prompt:
        return jsonify({"error": "prompt fehlt"}), 400

    # Auto-Modell
    if model_key == "auto":
        suggestion = auto_suggest(prompt, multi=len(uploads) > 1)
        model_key  = suggestion["model"]
        if mix_type == "auto":
            mix_type = suggestion.get("mix_type", "blend")
    elif mix_type == "auto":
        mix_type = _keywords_suggest(prompt, len(uploads) > 1)["mix_type"]

    if model_key not in MODELS:
        return jsonify({"error": f"Unbekanntes Modell: {model_key}"}), 400
    if MODELS[model_key].get("broken"):
        return jsonify({"error": f"Modell nicht verwendbar: {MODELS[model_key].get('broken_reason')}"}), 400
    if _is_pending(MODELS[model_key]):
        return jsonify({"error": f"Modell noch nicht bereit: {MODELS[model_key].get('pending_reason')}"}), 400

    res_entry = RES_MAP.get(resolution)
    if not res_entry:
        return jsonify({"error": f"Unbekannte Auflösung: {resolution}"}), 400
    w, h = res_entry

    model_cfg = MODELS[model_key]
    if not model_cfg["path"].exists():
        return jsonify({"error": f"Modell-Datei nicht gefunden: {model_cfg['path'].name}"}), 500

    # Referenzbilder auflösen
    init_img_path = None
    if uploads:
        found_paths = []
        for up in uploads[:6]:
            uid = up.get("id") or up.get("path", "").split("_")[-1].split(".")[0]
            for ext in (".png", ".jpg", ".jpeg", ".webp"):
                c = Path(f"/tmp/bilder_init_{uid}{ext}")
                if c.exists():
                    found_paths.append(c)
                    break
            else:
                p = Path(up.get("path", ""))
                if p.exists():
                    found_paths.append(p)
        if not found_paths:
            return jsonify({"error": "Referenzbilder nicht gefunden — bitte erneut hochladen"}), 400
        if len(found_paths) == 1:
            init_img_path = found_paths[0]
        else:
            # Bei FLUX_KONTEXT und mehreren Bildern: blend → single init_img
            # (sd.cpp kennt keinen -r Multi-Referenz-Flag; blend ist die korrekte Methode)
            target = (w, h)
            init_img_path = mix_images(found_paths, mode=mix_type, target_size=target)

    # FLUX_KONTEXT ohne init_img ist reines txt2img — strength irrelevant
    if MODELS[model_key].get("typ") == "FLUX_KONTEXT" and init_img_path:
        strength = max(strength, 0.85)  # mindestens 0.85 damit das Bild sich tatsächlich verändert

    style_suffix   = STYLE_MAP.get(style_key, "")
    full_prompt    = prompt + style_suffix
    estimated_secs = _estimate_secs(model_cfg, w, h)

    job_id      = str(uuid.uuid4())
    if image_name:
        import re
        safe = re.sub(r'[^\w\-]', '-', image_name, flags=re.UNICODE).strip('-')
        safe = re.sub(r'-+', '-', safe)[:60]
        output_path = OUTPUT_DIR / f"{safe}_{job_id[:8]}.png"
    else:
        output_path = OUTPUT_DIR / f"{job_id}.png"

    with JOBS_LOCK:
        JOBS[job_id] = {
            "status":         "pending",
            "progress_pct":   0,
            "eta_seconds":    estimated_secs,
            "image_url":      None,
            "error":          None,
            "started_at":     None,
            "estimated_secs": estimated_secs,
            "img2img":        init_img_path is not None,
            "model_used":     model_key,
            "output_path":    str(output_path),
        }

    queued = not JOB_QUEUE.empty()
    JOB_QUEUE.put((job_id, model_key, full_prompt, w, h, estimated_secs, output_path, init_img_path, strength, negative_prompt))

    return jsonify({"job_id": job_id, "queued": queued, "model_used": model_key,
                    "model_label": model_cfg["label"], "mix_type": mix_type})


@app.route("/api/status/<job_id>", methods=["GET"])
def status(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job nicht gefunden"}), 404
    return jsonify({
        "status":       job["status"],
        "progress_pct": job["progress_pct"],
        "eta_seconds":  job["eta_seconds"],
        "image_url":    job["image_url"],
        "error":        job["error"],
        "phase":        job.get("phase", "loading"),
    })


@app.route("/api/image/<job_id>", methods=["GET"])
def image(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job nicht gefunden"}), 404
    if job["status"] != "done":
        return jsonify({"error": "Bild noch nicht fertig"}), 202

    output_path = Path(job.get("output_path") or OUTPUT_DIR / f"{job_id}.png")
    if not output_path.exists():
        return jsonify({"error": "PNG nicht gefunden"}), 404

    return send_file(str(output_path), mimetype="image/png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== flextrawurst Bildgenerator ===")
    print(f"Port:    8042")
    print(f"URL:     http://localhost:8042/bildgenerator")
    print(f"Health:  http://localhost:8042/api/health")
    print(f"Models:  http://localhost:8042/api/models")
    print(f"sd-cli:  {SD_CLI}")
    print(f"Output:  {OUTPUT_DIR}")
    print()
    print("Modelle:")
    for key, cfg in MODELS.items():
        exists = "OK" if cfg["path"].exists() else "FEHLT"
        print(f"  [{exists}] {key}: {cfg['path'].name} ({cfg['groesse']})")
    print()
    print("Shared Dateien:")
    for p in [SDXL_CLIP_L, SDXL_CLIP_G, SDXL_VAE, FLUX_CLIP_L, FLUX_T5XXL, FLUX_VAE]:
        exists = "OK" if p.exists() else "FEHLT"
        print(f"  [{exists}] {p}")
    print()

    if not SD_CLI.exists():
        print(f"WARNUNG: sd-cli nicht gefunden: {SD_CLI}")

    app.run(host="0.0.0.0", port=8042, debug=False)
