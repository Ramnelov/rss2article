#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d ".venv" ]]; then
  echo "No .venv found. Running setup_env..."
  ./scripts/setup_env.sh
fi

source .venv/bin/activate
python -m rss2article
