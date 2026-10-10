#!/usr/bin/env bash
# Builds dist/Alakazam.app via py2app.
#
# Uses its own venv, built from Homebrew's Python rather than this project's own (uv-managed)
# one: py2app needs a CPython build where zlib (and friends) are real dynamic .so files, but
# uv's managed CPython distributions link zlib statically into the interpreter, which crashes
# py2app's freezing step. Homebrew's python.org-style framework build has a real zlib.so.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_VENV="$SCRIPT_DIR/.venv"
BUILD_PYTHON="$BUILD_VENV/bin/python"
HOMEBREW_PYTHON="/opt/homebrew/bin/python3.14"

if [ ! -x "$BUILD_PYTHON" ]; then
    echo "Setting up packaging venv at $BUILD_VENV (one-time)..."
    uv venv --python "$HOMEBREW_PYTHON" "$BUILD_VENV"
    uv pip install --python "$BUILD_PYTHON" rumps pyobjc-framework-cocoa py2app setuptools
fi

uv pip install --python "$BUILD_PYTHON" -e "$PROJECT_ROOT/../alakazam" -e "$PROJECT_ROOT"

rm -rf "$SCRIPT_DIR/build" "$PROJECT_ROOT/dist"
(cd "$SCRIPT_DIR" && "$BUILD_PYTHON" setup.py py2app)

echo "Built: $PROJECT_ROOT/dist/Alakazam.app"
