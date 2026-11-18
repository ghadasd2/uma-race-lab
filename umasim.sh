#!/usr/bin/env bash
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHONPATH="$HERE${PYTHONPATH:+:$PYTHONPATH}" exec python3 -m umasim.cli "$@"
