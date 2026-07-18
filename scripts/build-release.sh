#!/usr/bin/env bash
# scripts/build-release.sh - build cross-platform releases of mcp-injector
set -euo pipefail

# Read version from VERSION file
VERSION=$(tr -d '[:space:]' < VERSION)
RELEASE_DIR="releases/v${VERSION}"

mkdir -p "$RELEASE_DIR"

echo "Building version v${VERSION}..."

GOOS=linux   GOARCH=amd64  go build -trimpath -ldflags="-s -w -X main.Version=v${VERSION}" -o "${RELEASE_DIR}/mcp-injector-linux-amd64" ./cmd/mcp-injector
GOOS=linux   GOARCH=arm64  go build -trimpath -ldflags="-s -w -X main.Version=v${VERSION}" -o "${RELEASE_DIR}/mcp-injector-linux-arm64" ./cmd/mcp-injector
GOOS=darwin  GOARCH=amd64  go build -trimpath -ldflags="-s -w -X main.Version=v${VERSION}" -o "${RELEASE_DIR}/mcp-injector-darwin-amd64" ./cmd/mcp-injector
GOOS=darwin  GOARCH=arm64  go build -trimpath -ldflags="-s -w -X main.Version=v${VERSION}" -o "${RELEASE_DIR}/mcp-injector-darwin-arm64" ./cmd/mcp-injector
GOOS=windows GOARCH=amd64  go build -trimpath -ldflags="-s -w -X main.Version=v${VERSION}" -o "${RELEASE_DIR}/mcp-injector-windows-amd64.exe" ./cmd/mcp-injector

# Generate checksums using sha256sum
cd "$RELEASE_DIR"
sha256sum mcp-injector-* > checksums.sha256

echo "Build complete. Output in ${RELEASE_DIR}:"
ls -la
