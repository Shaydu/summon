#!/bin/bash
# Activate venv and run pytest
set -e
source "$(dirname "$0")/../venv/bin/activate"
# Clean pyc caches
find . -type d -name "__pycache__" -print0 | xargs -0 rm -rf || true
# Run pytest
pytest -q
