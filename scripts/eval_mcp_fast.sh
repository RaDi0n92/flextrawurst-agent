#!/usr/bin/env bash
set -euo pipefail

cd /root/werkraum

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

python3 -m py_compile /root/werkraum/agent/dak_gord_system/graph/evals/eval_mcp_fast.py
python3 -m agent.dak_gord_system.graph.evals.eval_mcp_fast

latest=$(ls -t /root/werkraum/agent/dak_gord_system/spuren/evals/eval_mcp_fast_*.md | head -n 1)
echo
echo "LATEST_REPORT=$latest"
echo
sed -n "1,220p" "$latest"
