#!/bin/sh

# Create SWU update packages for Rinkhals WebUI
#
# Expects build artifacts to already exist:
#   - build/dist/mpy/
#   - build/dist/frontend/
#
# Run `hatch run build` for the full pipeline, or call individual steps:
#   - `hatch run build-frontend`
#   - `hatch run build-mpy`
#   - `hatch run build-swu`

set -e

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
STAGING_DIR=$(mktemp -d)
DIST_DIR="$SCRIPT_DIR/dist"
MPY_DIR="$DIST_DIR/mpy"

cleanup() {
    rm -rf "$STAGING_DIR"
}
trap cleanup EXIT

# Prerequisites
for cmd in zip tar; do
    if ! command -v "$cmd" > /dev/null 2>&1; then
        echo "Error: $cmd is not installed" >&2
        exit 1
    fi
done

# Verify build artifacts
if [ ! -d "$DIST_DIR/frontend" ]; then
    echo "Error: Frontend not built (build/dist/frontend/ missing)" >&2
    echo "Run 'hatch run build-frontend' first" >&2
    exit 1
fi

if [ ! -d "$MPY_DIR" ]; then
    echo "Error: Compiled bytecode not found (build/dist/mpy/ missing)" >&2
    echo "Run 'hatch run build-mpy' first" >&2
    exit 1
fi

# Stage the package
echo "Staging update package..."

APP_STAGE="$STAGING_DIR/rinkhals-webui"
mkdir -p "$APP_STAGE/lib"

# Add top-level app files
cp "$PROJECT_ROOT/rinkhals-webui/app.json" "$APP_STAGE/"
cp "$PROJECT_ROOT/rinkhals-webui/app.sh" "$APP_STAGE/"
chmod +x "$APP_STAGE/app.sh"

# Add compiled Micropython modules
cp -r "$MPY_DIR/rinkhals_webui" "$APP_STAGE/lib/rinkhals_webui"
cp -r "$MPY_DIR/microdot" "$APP_STAGE/lib/microdot"

# Add frontend
cp -r "$DIST_DIR/frontend" "$APP_STAGE/static"

# Add update.sh at root of staging
cp "$SCRIPT_DIR/update.sh" "$STAGING_DIR/update.sh"

# Create setup.tar.gz
echo "Creating setup.tar.gz..."
mkdir -p "$DIST_DIR"
rm -rf "$DIST_DIR/update_swu"
mkdir -p "$DIST_DIR/update_swu"

cd "$STAGING_DIR"
tar -czf "$DIST_DIR/update_swu/setup.tar.gz" .

# Create encrypted SWU packages
echo "Creating SWU packages..."
cd "$DIST_DIR"
rm -f update-k2p-k3.swu update-ks1.swu update-k3m.swu

zip -P 'U2FsdGVkX19deTfqpXHZnB5GeyQ/dtlbHjkUnwgCi+w=' -r update-k2p-k3.swu update_swu
zip -P 'U2FsdGVkX1+lG6cHmshPLI/LaQr9cZCjA8HZt6Y8qmbB7riY' -r update-ks1.swu update_swu
zip -P '4DKXtEGStWHpPgZm8Xna9qluzAI8VJzpOsEIgd8brTLiXs8fLSu3vRx8o7fMf4h6' -r update-k3m.swu update_swu

#rm -rf "$DIST_DIR/update_swu"

echo "Done! SWU packages:"
ls -1 "$DIST_DIR"/update-*.swu
