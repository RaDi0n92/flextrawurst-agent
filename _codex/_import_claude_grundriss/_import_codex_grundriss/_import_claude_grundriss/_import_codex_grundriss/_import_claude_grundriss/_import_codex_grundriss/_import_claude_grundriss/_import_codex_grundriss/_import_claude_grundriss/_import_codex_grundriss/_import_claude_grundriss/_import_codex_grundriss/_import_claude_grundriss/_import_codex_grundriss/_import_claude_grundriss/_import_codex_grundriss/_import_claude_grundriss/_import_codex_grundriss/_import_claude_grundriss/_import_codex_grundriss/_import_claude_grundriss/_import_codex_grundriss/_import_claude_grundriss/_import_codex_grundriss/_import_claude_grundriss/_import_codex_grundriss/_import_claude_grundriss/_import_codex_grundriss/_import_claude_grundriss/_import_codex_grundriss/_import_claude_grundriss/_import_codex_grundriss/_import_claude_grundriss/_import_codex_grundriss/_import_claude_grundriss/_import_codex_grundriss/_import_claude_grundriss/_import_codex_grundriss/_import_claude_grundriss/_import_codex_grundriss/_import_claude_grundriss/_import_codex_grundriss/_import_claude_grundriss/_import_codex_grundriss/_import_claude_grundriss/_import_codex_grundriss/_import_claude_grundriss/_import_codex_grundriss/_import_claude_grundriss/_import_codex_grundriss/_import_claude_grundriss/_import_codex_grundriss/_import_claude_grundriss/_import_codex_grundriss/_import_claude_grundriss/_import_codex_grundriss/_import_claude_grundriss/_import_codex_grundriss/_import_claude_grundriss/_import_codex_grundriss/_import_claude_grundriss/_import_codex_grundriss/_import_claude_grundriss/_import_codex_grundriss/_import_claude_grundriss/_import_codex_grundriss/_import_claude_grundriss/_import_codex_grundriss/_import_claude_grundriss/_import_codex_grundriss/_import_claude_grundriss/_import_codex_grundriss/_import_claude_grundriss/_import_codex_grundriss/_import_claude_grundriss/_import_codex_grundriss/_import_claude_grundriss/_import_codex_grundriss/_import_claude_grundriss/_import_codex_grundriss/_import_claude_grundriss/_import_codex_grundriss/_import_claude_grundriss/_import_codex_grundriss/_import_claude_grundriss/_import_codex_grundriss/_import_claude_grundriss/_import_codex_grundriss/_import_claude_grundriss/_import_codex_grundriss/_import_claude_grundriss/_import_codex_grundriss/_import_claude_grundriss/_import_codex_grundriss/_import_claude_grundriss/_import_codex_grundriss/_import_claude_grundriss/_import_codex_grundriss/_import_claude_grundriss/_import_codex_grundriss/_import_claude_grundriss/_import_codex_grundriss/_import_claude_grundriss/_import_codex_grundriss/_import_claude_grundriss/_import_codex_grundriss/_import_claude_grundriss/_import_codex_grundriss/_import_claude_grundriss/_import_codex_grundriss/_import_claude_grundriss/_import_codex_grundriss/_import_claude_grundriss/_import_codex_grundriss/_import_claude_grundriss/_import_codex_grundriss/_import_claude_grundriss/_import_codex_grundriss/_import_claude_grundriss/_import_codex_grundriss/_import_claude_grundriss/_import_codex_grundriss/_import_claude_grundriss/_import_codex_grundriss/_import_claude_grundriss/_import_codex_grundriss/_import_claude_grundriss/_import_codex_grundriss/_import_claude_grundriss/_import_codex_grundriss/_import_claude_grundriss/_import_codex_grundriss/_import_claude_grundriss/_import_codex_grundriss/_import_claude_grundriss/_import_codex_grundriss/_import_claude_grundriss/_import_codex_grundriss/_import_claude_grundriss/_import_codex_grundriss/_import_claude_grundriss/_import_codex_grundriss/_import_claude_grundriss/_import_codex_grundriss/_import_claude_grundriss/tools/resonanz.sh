#!/bin/bash
# Resonanzkörper: Ollama liest eine Spiegel-Datei und wirft eine unbequeme Frage zurück.
# Aufruf: resonanz.sh <spiegel-datei.md>
# Ergebnis wird an die Datei angehängt.

DATEI=$1
MODELL="dolphin-mistral:7b"

if [ -z "$DATEI" ] || [ ! -f "$DATEI" ]; then
    echo "Nutzung: resonanz.sh <spiegel-datei.md>"
    exit 1
fi

INHALT=$(cat "$DATEI")
ZEITSTEMPEL=$(date '+%Y-%m-%d %H:%M')

PROMPT="Du liest eine Reflexion eines KI-Systems über ein Konzept in einem Softwareprojekt.
Du bist nicht dieses KI-System — du bist ein anderes Modell mit anderer Perspektive.

Deine einzige Aufgabe: Stelle eine einzige unbequeme Frage oder benenne einen blinden Fleck.
Keine Zusammenfassung. Keine Erklärung. Kein Lob. Nur die Frage oder der blinde Fleck.
Maximal 3 Sätze.

Reflexion:
$INHALT"

echo ""
echo "Sende an Ollama/$MODELL..."

ANTWORT=$(curl -s http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d "$(python3 -c "
import json, sys
prompt = open('$DATEI').read()
full_prompt = '''Du liest eine Reflexion eines KI-Systems über ein Konzept in einem Softwareprojekt.
Du bist nicht dieses KI-System — du bist ein anderes Modell mit anderer Perspektive.

Deine einzige Aufgabe: Stelle eine einzige unbequeme Frage oder benenne einen blinden Fleck.
Keine Zusammenfassung. Keine Erklärung. Kein Lob. Nur die Frage oder der blinde Fleck.
Maximal 3 Sätze.

Reflexion:
''' + prompt
print(json.dumps({'model': '$MODELL', 'prompt': full_prompt, 'stream': False}))
")" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('response','(keine Antwort)'))")

cat >> "$DATEI" << EOF

---

## Resonanz *(Ollama/$MODELL, $ZEITSTEMPEL)*

$ANTWORT
EOF

echo "Resonanz angehängt an: $DATEI"
