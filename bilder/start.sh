#!/bin/bash
cd "$(dirname "$0")"
echo "Galerie läuft auf http://localhost:8080"
python3 -m http.server 8080
