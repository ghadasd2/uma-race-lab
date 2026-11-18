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
# observation-only patch: duel / spot-struggle start+end and skill activation positions.
# Logs are indexed by gate rank (engine's internal order); umasim maps them back to runners.
PATCH="$HERE/data/globalsim-observation.patch"
(cd vendor/GlobalSim && { git apply --check "$PATCH" 2>/dev/null && git apply "$PATCH" || echo "patch already applied or not applicable"; } && cargo build --release --locked)
python3 -m pip install --quiet pandas numpy
./umasim.sh courses nakayama 2500 >/dev/null && echo "umasim ready: try ./umasim.sh run scenarios/example-arima.json --md"
