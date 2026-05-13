#!/usr/bin/env bash
set -euo pipefail

# Build the React frontend for deployment under the subpath /iceaa/
# and create a deployment tarball that contains the built frontend,
# backend code, and deployment configs. Run this from the repo root.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$REPO_ROOT/release_build"
FRONTEND_DIR="$REPO_ROOT/react-app"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

echo "Building frontend with base /iceaa/ ..."
cd "$FRONTEND_DIR"
# Use the lockfile when available for reproducible builds.
if [[ -f package-lock.json ]]; then
	npm ci
else
	npm install
fi
npm run build -- --base=/iceaa/

echo "Copying built frontend..."
mkdir -p "$BUILD_DIR/frontend"
mkdir -p "$BUILD_DIR/frontend/iceaa"
cp -r dist/. "$BUILD_DIR/frontend/iceaa/"

echo "Copying backend and deployment files..."
mkdir -p "$BUILD_DIR/backend"
cp -r "$REPO_ROOT/backend" "$BUILD_DIR/"
cp -r "$REPO_ROOT/deployment" "$BUILD_DIR/"

echo "Creating release tarball: release/alumniconnect-prod.tar.gz"
mkdir -p "$REPO_ROOT/release"
tar -C "$BUILD_DIR" -czf "$REPO_ROOT/release/alumniconnect-prod.tar.gz" .

echo "Done. Release artifact: release/alumniconnect-prod.tar.gz"
echo "Copy the tarball to the server and extract into /var/www/alumniconnect"
