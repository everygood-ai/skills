#!/usr/bin/env bash

set -u

usage() {
  echo "Usage: bash scripts/validate-context-lengths.sh <context-directory> [context-file ...]" >&2
}

line_limit=500

if (( $# < 1 )); then
  usage
  exit 2
fi

context_directory=${1%/}
shift

if [[ ! -d "$context_directory" ]]; then
  echo "ERROR: context directory does not exist: $context_directory" >&2
  exit 2
fi

context_files=()

if (( $# > 0 )); then
  context_files=("$@")
else
  while IFS= read -r -d '' file_path; do
    context_files+=("$(basename "$file_path")")
  done < <(find "$context_directory" -maxdepth 1 -type f -name '*.md' -print0 | sort -z)

  if (( ${#context_files[@]} == 0 )); then
    echo "ERROR: no .md context files found in $context_directory" >&2
    exit 2
  fi
fi

status=0

for context_file in "${context_files[@]}"; do
  file_path="$context_directory/$context_file"

  if [[ ! -f "$file_path" ]]; then
    echo "ERROR: missing context file: $file_path" >&2
    status=1
    continue
  fi

  actual_lines=$(awk 'END { print NR }' "$file_path")

  if (( actual_lines > line_limit )); then
    echo "ERROR: $file_path has $actual_lines lines; exceeds the $line_limit-line ceiling" >&2
    status=1
  else
    echo "PASS: $file_path has $actual_lines/$line_limit lines"
  fi
done

exit "$status"
