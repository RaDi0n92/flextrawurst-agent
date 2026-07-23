#!/usr/bin/env bash
set -euo pipefail

OUT="$GITHUB_WORKSPACE/out/FLEXTRAWURST_OPEN_ASSETS_V1"
SRC="$GITHUB_WORKSPACE/work"
mkdir -p "$OUT/assets" "$OUT/licenses" "$OUT/manifests" "$SRC"

repos=(
  "KenneyNL/Starter-Kit-City-Builder"
  "KenneyNL/Starter-Kit-3D-Platformer"
  "KenneyNL/Starter-Kit-FPS"
  "KenneyNL/Starter-Kit-Racing"
  "KenneyNL/Starter-Kit-Basic-Scene"
)

printf 'repository\tcommit\tlicense_files\tasset_files\n' > "$OUT/manifests/repositories.tsv"

for repo in "${repos[@]}"; do
  name="${repo#*/}"
  dir="$SRC/$name"
  git clone --depth 1 "https://github.com/$repo.git" "$dir"
  commit="$(git -C "$dir" rev-parse HEAD)"
  mkdir -p "$OUT/assets/$name" "$OUT/licenses/$name"

  while IFS= read -r -d '' f; do
    rel="${f#$dir/}"
    mkdir -p "$OUT/assets/$name/$(dirname "$rel")"
    cp -a "$f" "$OUT/assets/$name/$rel"
  done < <(find "$dir" -type f \( \
      -iname '*.glb' -o -iname '*.gltf' -o -iname '*.obj' -o -iname '*.fbx' -o -iname '*.blend' -o \
      -iname '*.stl' -o -iname '*.dae' -o -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o \
      -iname '*.webp' -o -iname '*.svg' -o -iname '*.wav' -o -iname '*.ogg' -o -iname '*.mp3' \
    \) -print0)

  while IFS= read -r -d '' f; do
    cp -a "$f" "$OUT/licenses/$name/$(basename "$f")"
  done < <(find "$dir" -maxdepth 3 -type f \( -iname 'LICENSE*' -o -iname 'COPYING*' -o -iname 'README*' \) -print0)

  licenses="$(find "$OUT/licenses/$name" -type f | wc -l | tr -d ' ')"
  assets="$(find "$OUT/assets/$name" -type f | wc -l | tr -d ' ')"
  printf '%s\t%s\t%s\t%s\n' "$repo" "$commit" "$licenses" "$assets" >> "$OUT/manifests/repositories.tsv"
done

find "$OUT/assets" -type f -print0 | sort -z | xargs -0 sha256sum > "$OUT/manifests/SHA256SUMS.txt"
python3 - <<'PY'
from pathlib import Path
from collections import Counter
import json, os
out = Path(os.environ['GITHUB_WORKSPACE'])/'out'/'FLEXTRAWURST_OPEN_ASSETS_V1'
files = [p for p in (out/'assets').rglob('*') if p.is_file()]
counts = Counter(p.suffix.lower() or '<none>' for p in files)
size = sum(p.stat().st_size for p in files)
report = {
  'asset_files': len(files),
  'bytes': size,
  'extensions': dict(sorted(counts.items())),
  'repositories': 5,
  'license_rule': 'Each source repository license/README is preserved beside its harvested assets. Recheck per-file exceptions before production use.'
}
(out/'manifests'/'VALIDATION.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
(out/'README.md').write_text(
  '# Flextrawurst Open Assets V1\n\n'
  'Tatsächlich geerntete Binärassets aus fünf offenen Kenney-Starter-Repositories. '
  'Originalpfade, Commit-SHAs, Lizenz-/README-Dateien und SHA-256-Prüfsummen sind erhalten.\n',
  encoding='utf-8')
PY

cd "$GITHUB_WORKSPACE/out"
zip -r -9 FLEXTRAWURST_OPEN_ASSETS_V1.zip FLEXTRAWURST_OPEN_ASSETS_V1 >/dev/null
