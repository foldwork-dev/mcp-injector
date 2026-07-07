#!/usr/bin/env bash
# ─── mcp-injector Zero-Config Installer ───────────────────────────────────────
#
# Detects OS and architecture, downloads/installs the binaries, and configures
# Claude Desktop, Cursor, VS Code, and Windsurf.
# ─────────────────────────────────────────────────────────────────────────────
set -eu

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

printf "%b\n" "${GREEN}===================================================================${NC}"
printf "%b\n" "  mcp-injector installer"
printf "%b\n" "${GREEN}===================================================================${NC}"
echo ""

# Check dependencies
if ! command -v curl > /dev/null 2>&1; then
  printf "%b\n" "${RED}Error: curl is required to run this installer.${NC}" >&2
  exit 1
fi

if ! command -v python3 > /dev/null 2>&1; then
  printf "%b\n" "${RED}Error: python3 is required to configure IDEs.${NC}" >&2
  exit 1
fi


# 1. Detect OS & Architecture
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

case "$OS" in
  linux*)   OS="linux" ;;
  darwin*)  OS="darwin" ;;
  msys*|cygwin*|mingw*) OS="windows" ;;
  *)        OS="linux" ;;
esac

case "$ARCH" in
  x86_64|amd64) ARCH="amd64" ;;
  arm64|aarch64) ARCH="arm64" ;;
  *)            ARCH="amd64" ;;
esac

# 2. Setup paths
EXE_EXT=""
if [ "$OS" = "windows" ]; then
  EXE_EXT=".exe"
fi

INSTALL_DIR="/usr/local/bin"
BIN_DEST="$INSTALL_DIR/mcp-injector${EXE_EXT}"
BENCHMARK_DEST="$INSTALL_DIR/mcp-benchmark${EXE_EXT}"

# Check permissions
USE_SUDO=""
if [ "$OS" != "windows" ]; then
  if [ ! -w "$INSTALL_DIR" ]; then
    if [ "$(id -u)" -ne 0 ]; then
      if sudo -n true 2>/dev/null; then
        USE_SUDO="sudo"
      else
        INSTALL_DIR="$HOME/.local/bin"
        mkdir -p "$INSTALL_DIR"
        BIN_DEST="$INSTALL_DIR/mcp-injector${EXE_EXT}"
        BENCHMARK_DEST="$INSTALL_DIR/mcp-benchmark${EXE_EXT}"
      fi
    fi
  fi
fi

TMP_BIN=$(mktemp)
TMP_BENCHMARK=$(mktemp)
trap 'rm -f "$TMP_BIN" "$TMP_BENCHMARK"' EXIT

# 3. Download / Install
echo "Detecting release binaries for $OS-$ARCH..."

DOWNLOAD_URL="https://github.com/foldwork-dev/mcp-injector/releases/latest/download/mcp-injector-$OS-$ARCH${EXE_EXT}"
BENCHMARK_URL="https://github.com/foldwork-dev/mcp-benchmark/releases/latest/download/mcp-benchmark-$OS-$ARCH${EXE_EXT}"

if curl -sLf "$DOWNLOAD_URL" -o "$TMP_BIN"; then
  printf "%b\n" "${GREEN}✓${NC} Downloaded mcp-injector from GitHub Releases."
else
  printf "%b\n" "${YELLOW}⚠${NC} Release download failed. Compiling/copying local binary..."
  if [ -f "./mcp-injector${EXE_EXT}" ]; then
    cp "./mcp-injector${EXE_EXT}" "$TMP_BIN"
  elif command -v go > /dev/null 2>&1; then
    go build -o "$TMP_BIN" .
  else
    printf "%b\n" "${RED}Error: Download failed and 'go' compiler is not installed.${NC}" >&2
    exit 1
  fi
fi

if curl -sLf "$BENCHMARK_URL" -o "$TMP_BENCHMARK"; then
  printf "%b\n" "${GREEN}✓${NC} Downloaded mcp-benchmark from GitHub Releases."
else
  printf "%b\n" "${YELLOW}⚠${NC} Release download failed. Compiling/copying local benchmark binary..."
  if [ -f "./mcp-benchmark${EXE_EXT}" ]; then
    cp "./mcp-benchmark${EXE_EXT}" "$TMP_BENCHMARK"
  elif [ -f "./benchmark${EXE_EXT}" ]; then
    cp "./benchmark${EXE_EXT}" "$TMP_BENCHMARK"
  elif command -v go > /dev/null 2>&1; then
    go build -o "$TMP_BENCHMARK" ./cmd/benchmark
  else
    printf "%b\n" "${RED}Error: Download failed and 'go' compiler is not installed.${NC}" >&2
    exit 1
  fi
fi

chmod +x "$TMP_BIN" "$TMP_BENCHMARK"

echo "Installing binaries to $INSTALL_DIR..."
if [ -n "$USE_SUDO" ]; then
  echo "Elevated permissions required to write to $INSTALL_DIR."
  $USE_SUDO cp "$TMP_BIN" "$BIN_DEST"
  $USE_SUDO cp "$TMP_BENCHMARK" "$BENCHMARK_DEST"
else
  cp "$TMP_BIN" "$BIN_DEST"
  cp "$TMP_BENCHMARK" "$BENCHMARK_DEST"
fi
printf "%b\n" "${GREEN}✓${NC} Binaries installed successfully."

# 4. Resolve IDE config paths
CLAUDE_CONFIG=""
CURSOR_CONFIG=""
VSCODE_CONFIG=""
WINDSURF_CONFIG=""

if [ "$OS" = "darwin" ]; then
  CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
  CURSOR_CONFIG="$HOME/.cursor/mcp.json"
  WINDSURF_CONFIG="$HOME/.windsurf/mcp.json"
elif [ "$OS" = "windows" ]; then
  CLAUDE_CONFIG="${APPDATA:-}/Claude/claude_desktop_config.json"
  CURSOR_CONFIG="${USERPROFILE:-}/.cursor/mcp.json"
  WINDSURF_CONFIG="${USERPROFILE:-}/.windsurf/mcp.json"
else
  # Linux
  CLAUDE_CONFIG="$HOME/.config/Claude/claude_desktop_config.json"
  CURSOR_CONFIG="$HOME/.cursor/mcp.json"
  WINDSURF_CONFIG="$HOME/.windsurf/mcp.json"
fi

if [ -d "$PWD/.git" ]; then
  VSCODE_CONFIG="$PWD/.vscode/mcp.json"
else
  VSCODE_CONFIG=""
fi

# Function to merge config using python
merge_config() {
  local cfg_file="$1"
  local bin_path="$2"
  python3 -c "
import json
import sys
import os

filepath = '$cfg_file'
binpath = '$bin_path'

try:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    data = {}
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read().strip()
            if content:
                data = json.loads(content)
    
    if not isinstance(data, dict):
        data = {}
    
    key = 'servers' if 'mcp.json' in filepath else 'mcpServers'
    if key not in data:
        data[key] = {}
    
    workspace_val = '\${workspaceFolder}'
    if 'claude_desktop_config' in filepath:
        workspace_val = '/absolute/path/to/your/project'

    data[key]['mcp-injector'] = {
        'command': binpath,
        'env': { 'MCP_WORKSPACE': workspace_val }
    }
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
"
}

# 5. Configure IDEs
CLAUDE_STATUS="✗ Claude Desktop not detected"
CURSOR_STATUS="✗ Cursor not detected"
VSCODE_STATUS="✗ VS Code native MCP requires workspace"
WINDSURF_STATUS="✗ Windsurf not detected"

# Check Claude Desktop parent dir or config existence
CLAUDE_DIR=$(dirname "$CLAUDE_CONFIG")
if [ -d "$CLAUDE_DIR" ] || [ -f "$CLAUDE_CONFIG" ]; then
  res=$(merge_config "$CLAUDE_CONFIG" "$BIN_DEST")
  if [ "$res" = "SUCCESS" ]; then
    CLAUDE_STATUS="✓ Claude Desktop configured (IMPORTANT: edit config to set actual MCP_WORKSPACE path)"
  else
    CLAUDE_STATUS="⚠ Claude Desktop: manual config required: $res"
  fi
fi

# Check Cursor parent dir or config existence
CURSOR_DIR=$(dirname "$CURSOR_CONFIG")
if [ -d "$CURSOR_DIR" ] || [ -f "$CURSOR_CONFIG" ]; then
  res=$(merge_config "$CURSOR_CONFIG" "$BIN_DEST")
  if [ "$res" = "SUCCESS" ]; then
    CURSOR_STATUS="✓ Cursor configured"
  else
    CURSOR_STATUS="⚠ Cursor: manual config required: $res"
  fi
fi

# Check VS Code native MCP (workspace local)
if [ -n "$VSCODE_CONFIG" ]; then
  res=$(merge_config "$VSCODE_CONFIG" "$BIN_DEST")
  if [ "$res" = "SUCCESS" ]; then
    VSCODE_STATUS="✓ VS Code configured for this workspace"
  else
    VSCODE_STATUS="⚠ VS Code: manual config required: $res"
  fi
else
  VSCODE_STATUS="⚠ VS Code: Not in a git repository. Run installer inside your project to auto-configure .vscode/mcp.json."
fi

# Check Windsurf
WINDSURF_DIR=$(dirname "$WINDSURF_CONFIG")
if [ -d "$WINDSURF_DIR" ] || [ -f "$WINDSURF_CONFIG" ]; then
  res=$(merge_config "$WINDSURF_CONFIG" "$BIN_DEST")
  if [ "$res" = "SUCCESS" ]; then
    WINDSURF_STATUS="✓ Windsurf configured"
  else
    WINDSURF_STATUS="⚠ Windsurf: manual config required: $res"
  fi
fi

# 6. Print Installation Summary
echo ""
printf "%b\n" "${GREEN}===================================================================${NC}"
printf "%b\n" "  Installation Summary"
printf "%b\n" "${GREEN}===================================================================${NC}"
printf "%b\n" "  ✓ mcp-injector installed to $BIN_DEST"
printf "%b\n" "  ✓ mcp-benchmark installed to $BENCHMARK_DEST"
if echo "$CLAUDE_STATUS" | grep -q "^✓"; then
  printf "%b\n" "  ${GREEN}$CLAUDE_STATUS${NC}"
else
  printf "%b\n" "  $CLAUDE_STATUS"
fi

if echo "$CURSOR_STATUS" | grep -q "^✓"; then
  printf "%b\n" "  ${GREEN}$CURSOR_STATUS${NC}"
else
  printf "%b\n" "  $CURSOR_STATUS"
fi

if echo "$VSCODE_STATUS" | grep -q "^✓"; then
  printf "%b\n" "  ${GREEN}$VSCODE_STATUS${NC}"
else
  printf "%b\n" "  $VSCODE_STATUS"
fi

if echo "$WINDSURF_STATUS" | grep -q "^✓"; then
  printf "%b\n" "  ${GREEN}$WINDSURF_STATUS${NC}"
else
  printf "%b\n" "  $WINDSURF_STATUS"
fi

# Warn if installed to user home bin and not in PATH
if echo "$BIN_DEST" | grep -q "$HOME/.local/bin"; then
  if ! echo ":$PATH:" | grep -q ":$HOME/.local/bin:"; then
    echo ""
    printf "%b\n" "${YELLOW}⚠ Warning: $HOME/.local/bin is not in your PATH.${NC}"
    printf "%b\n" "  You may need to add it to your shell profile (e.g. ~/.bashrc or ~/.zshrc):"
    printf "%b\n" "  export PATH=\$PATH:\$HOME/.local/bin"
  fi
fi

# Notify if no IDE configured
if ! echo "$CLAUDE_STATUS$CURSOR_STATUS$VSCODE_STATUS$WINDSURF_STATUS" | grep -q "✓"; then
  echo ""
  printf "%b\n" "${YELLOW}⚠ No supported IDE directories were detected for automatic configuration.${NC}"
  printf "%b\n" "  To manually integrate mcp-injector with your AI tools, please refer to"
  printf "%b\n" "  the documentation at https://foldwork.dev or create your tool config file manually."
fi
echo ""


echo ""
printf "%b\n" "${GREEN}===================================================================${NC}"
if ! echo "$CLAUDE_STATUS$CURSOR_STATUS$VSCODE_STATUS$WINDSURF_STATUS" | grep -q "✓"; then
  echo "  Installation complete! Please configure your IDE/client manually."
else
  echo "  You're all set. Restart your IDE and mcp-injector will be active."
fi
echo "  Docs: https://foldwork.dev"
printf "%b\n" "${GREEN}===================================================================${NC}"
