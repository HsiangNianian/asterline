#!/usr/bin/env bash

set -euo pipefail

while IFS= read -r config; do
  uv run python -m asterline --config "$config" config-check
done < <(find examples -maxdepth 2 -name 'config.*.toml' | sort)
