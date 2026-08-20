#!/usr/bin/env bash
# Installs the external CLI dependencies the skills in this repository need.
#
# When a skill under skills/ starts depending on a new external CLI, add its
# Homebrew formula (tap-qualified if it is not in homebrew-core) to
# BREW_FORMULAE below instead of writing a separate installer.
set -euo pipefail

BREW_FORMULAE=(
  "vale"                                  # egai-write-tone: structural prose linting for the prose/terse/compact tone modes
)

if ! command -v brew >/dev/null 2>&1; then
  echo "Error: Homebrew is required. Install it from https://brew.sh and rerun this script." >&2
  exit 1
fi

for formula in "${BREW_FORMULAE[@]}"; do
  echo "Installing $formula..."
  brew install "$formula"
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "Warning: python3 not found. It is required by run-tests.py and several skill scripts." >&2
fi

echo "Done. All skill dependencies are installed."
