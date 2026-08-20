#!/usr/bin/env bash
# Lint Markdown text against the egai-write-tone structural rules for one mode.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  echo "Usage: $(basename "$0") <prose|terse|compact> FILE [FILE...]" >&2
}

if [[ $# -lt 2 ]]; then
  usage
  exit 3
fi

mode="$1"
shift

case "$mode" in
  prose|terse|compact) ;;
  *)
    echo "Error: unknown mode '$mode' (use prose, terse, or compact)." >&2
    usage
    exit 3
    ;;
esac

if ! command -v vale >/dev/null 2>&1; then
  echo "Error: vale is not installed or not on PATH. Install it from https://vale.sh (e.g. 'brew install vale')." >&2
  exit 3
fi

exec vale --config "$SCRIPT_DIR/vale/$mode.vale.ini" "$@"
