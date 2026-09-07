#!/usr/bin/env bash

set -u -o pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  echo "Usage: scripts/validate.sh [--links] <path-to-skill>" >&2
}

if ! command -v skill-validator >/dev/null 2>&1; then
  echo "Error: skill-validator is not installed or not available on PATH." >&2
  exit 3
fi

mode="local"
skill_path=""

case "$#" in
  1)
    skill_path="$1"
    ;;
  2)
    if [[ "$1" != "--links" ]]; then
      usage
      exit 3
    fi
    mode="links"
    skill_path="$2"
    ;;
  *)
    usage
    exit 3
    ;;
esac

if [[ ! -d "$skill_path" ]]; then
  echo "Error: skill path is not a directory: $skill_path" >&2
  exit 3
fi

skill_file="$skill_path/SKILL.md"

if [[ -f "$skill_file" ]] && grep -En '<!--|</?[A-Za-z][^>]*>|<![A-Za-z-][^>]*>' "$skill_file"; then
  echo "Error: HTML tags, HTML comments, and angle-bracket placeholders are not allowed in SKILL.md." >&2
  exit 1
fi

if [[ "$mode" == "links" ]]; then
  exec skill-validator validate links "$skill_path"
fi

skill-validator check "$skill_path" \
  --only structure,content,contamination \
  --allow-flat-layouts \
  -o json | python3 "$script_dir/filter-orphans.py"
exit "${PIPESTATUS[1]}"
