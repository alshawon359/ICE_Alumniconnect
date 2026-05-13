#!/usr/bin/env bash
set -euo pipefail

# Run this on the production server after you git pull the latest repo.
# It installs/updates the backend venv, builds the frontend for /iceaa,
# and refreshes the static deploy files in /var/www/alumniconnect.

REPO_DIR="${1:-/var/www/alumniconnect}"
BACKEND_DIR="$REPO_DIR/backend"
FRONTEND_DIR="$REPO_DIR/react-app"

if [[ ! -d "$REPO_DIR/.git" ]]; then
  echo "Expected a git checkout at $REPO_DIR"
  exit 1
fi

cd "$REPO_DIR"

echo "Pulling latest code..."
git pull --ff-only

echo "Preparing Python venv..."
cd "$BACKEND_DIR"
if [[ ! -d venv ]]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

if [[ ! -f "$REPO_DIR/.env.production" && -f "$BACKEND_DIR/.env.production.example" ]]; then
  echo "Creating .env.production from example..."
  cp "$BACKEND_DIR/.env.production.example" "$REPO_DIR/.env.production"
  chmod 600 "$REPO_DIR/.env.production"
  echo "Edit $REPO_DIR/.env.production before starting the service."
fi

echo "Building frontend for /iceaa/..."
cd "$FRONTEND_DIR"
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi
npm run build -- --base=/iceaa/

echo "Syncing frontend build to /var/www/alumniconnect/frontend..."
mkdir -p "$REPO_DIR/frontend/iceaa"
rm -rf "$REPO_DIR/frontend/iceaa"/*
cp -r dist/. "$REPO_DIR/frontend/iceaa/"

echo "Done. Restart the service and reload nginx:"
echo "  sudo systemctl restart alumniconnect"
echo "  sudo nginx -t && sudo systemctl reload nginx"
