#!/usr/bin/env bash
# One-time setup: fetch + build the GlobalSim engine, install Python deps.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
if [ ! -e vendor/GlobalSim ]; then
  mkdir -p vendor
  git clone --depth 1 https://github.com/daftuyda/GlobalSim.git vendor/GlobalSim
fi
command -v cargo >/dev/null || { echo "Install Rust first: https://rustup.rs"; exit 1; }
(cd vendor/GlobalSim && cargo build --release --locked)
python3 -m pip install --quiet pandas numpy
./umasim.sh courses nakayama 2500 >/dev/null && echo "umasim ready: try ./umasim.sh run scenarios/example-arima.json --md"
