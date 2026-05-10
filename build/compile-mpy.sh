#!/bin/sh
# Compile all .py files in rinkhals-webui/src/ to .mpy bytecode in build/dist/mpy/
set -e

SRC=rinkhals-webui/src
OUT=build/dist/mpy

rm -rf "$OUT"

find "$SRC" -name '*.py' | while read -r f; do
    rel="${f#$SRC/}"
    out="$OUT/${rel%.py}.mpy"
    mkdir -p "$(dirname "$out")"
    mpy-cross "$f" -o "$out"
done

echo "Compiled $(find "$OUT" -name '*.mpy' | wc -l) files to $OUT/"
