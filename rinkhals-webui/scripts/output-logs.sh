#!/bin/bash

for file in /useremain/rinkhals/*.log; do
  if [ -f "$file" ]; then
    echo "=== File: $file ==="
    cat "$file"
    echo -e "\n"
  fi
done
