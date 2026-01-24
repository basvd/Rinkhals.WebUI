#!/usr/bin/env bash
set -euo pipefail

workspace_dir="${1:-}"

if [ -z "${workspace_dir}" ]; then
	echo "post-create.sh requires the workspace path as its first argument" >&2
	exit 1
fi

git config --global --add safe.directory "${workspace_dir}"

cd "${workspace_dir}"
hatch -v env create
