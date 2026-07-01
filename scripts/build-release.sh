#!/usr/bin/env bash
# scripts/build-release.sh - build cross-platform releases of mcp-injector
set -euo pipefail

# Read version from VERSION file
VERSION=$(tr -d '[:space:]' < VERSION)
RELEASE_DIR="releases/v${VERSION}"

mkdir -p "$RELEASE_DIR"

echo "Building version v${VERSION}..."

GOOS=linux   GOARCH=amd64  go build -ldflags="-s -w -X main.Version=v${VERSION}" -o "${RELEASE_DIR}/mcp-injector-linux-amd64"
GOOS=linux   GOARCH=arm64  go build -ldflags="-s -w -X main.Version=v${VERSION}" -o "${RELEASE_DIR}/mcp-injector-linux-arm64"
GOOS=darwin  GOARCH=amd64  go build -ldflags="-s -w -X main.Version=v${VERSION}" -o "${RELEASE_DIR}/mcp-injector-darwin-amd64"
GOOS=darwin  GOARCH=arm64  go build -ldflags="-s -w -X main.Version=v${VERSION}" -o "${RELEASE_DIR}/mcp-injector-darwin-arm64"
GOOS=windows GOARCH=amd64  go build -ldflags="-s -w -X main.Version=v${VERSION}" -o "${RELEASE_DIR}/mcp-injector-windows-amd64.exe"

# Generate checksums using sha256sum
cd "$RELEASE_DIR"
sha256sum mcp-injector-* > checksums.sha256

echo "Build complete. Output in ${RELEASE_DIR}:"
ls -la
