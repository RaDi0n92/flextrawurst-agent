#!/bin/bash
# Wartet auf fertige Safetensors-Downloads und konvertiert zu Q5_K GGUF
# Läuft als background-Prozess

SD_CLI="/root/werkraum/tools/sd_cpp/sd-cli"
MODELS_DIR="/root/werkraum/tools/models"

convert_when_ready() {
    local src="$1"
    local dst="$2"
    local expected_size="$3"  # in bytes, ungefähr
    local name="$4"

    echo "[$(date)] Warte auf $name ($src)..."
    while true; do
        if [ -f "$src" ]; then
            actual=$(stat -c%s "$src" 2>/dev/null || echo 0)
            if [ "$actual" -ge "$expected_size" ]; then
                echo "[$(date)] $name fertig ($actual bytes). Starte Konvertierung..."
                break
            fi
        fi
        sleep 30
    done

    echo "[$(date)] Konvertiere $src -> $dst"
    "$SD_CLI" --mode convert \
        --model "$src" \
        --type q5_0 \
        --output "$dst" \
        2>&1 | tee "/tmp/convert_${name}.log"

    if [ -f "$dst" ]; then
        echo "[$(date)] Konvertierung erfolgreich: $dst"
        rm -f "$src"
        echo "[$(date)] Safetensors gelöscht: $src"
    else
        echo "[$(date)] FEHLER: Konvertierung fehlgeschlagen für $name"
    fi
}

# Juggernaut XL v9 (6.62GB erwartet)
convert_when_ready \
    "$MODELS_DIR/juggernaut_xl_v9.safetensors" \
    "$MODELS_DIR/juggernaut_xl_v9_q5_k.gguf" \
    6600000000 \
    "juggernaut" &

# Pony Diffusion v6 (6.46GB erwartet)
convert_when_ready \
    "$MODELS_DIR/pony_diffusion_v6.safetensors" \
    "$MODELS_DIR/pony_diffusion_v6_q5_k.gguf" \
    6400000000 \
    "pony" &

# RealVisXL V5 fp16 (6.46GB erwartet)
convert_when_ready \
    "$MODELS_DIR/realvisxl_v5_fp16.safetensors" \
    "$MODELS_DIR/realvisxl_v5_q5_k.gguf" \
    6400000000 \
    "realvisxl" &

echo "Alle 3 Konvertierungs-Watcher gestartet."
wait
echo "Alle Konvertierungen abgeschlossen."
