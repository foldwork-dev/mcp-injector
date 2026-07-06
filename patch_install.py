import sys
import re

def patch_script(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # 1. Add WINDSURF_CONFIG to Resolve IDE config paths
    content = re.sub(
        r'CLAUDE_CONFIG=""\nCURSOR_CONFIG=""\nVSCODE_CONFIG=""',
        'CLAUDE_CONFIG=""\nCURSOR_CONFIG=""\nVSCODE_CONFIG=""\nWINDSURF_CONFIG=""',
        content
    )
    
    # 2. Update the OS conditionals
    content = re.sub(
        r'CURSOR_CONFIG="\$HOME/\.cursor/mcp\.json"\n\s*VSCODE_CONFIG="\$HOME/\.continue/[^"]+"',
        'CURSOR_CONFIG="$HOME/.cursor/mcp.json"\n  WINDSURF_CONFIG="$HOME/.windsurf/mcp.json"',
        content
    )
    content = re.sub(
        r'CURSOR_CONFIG="\$\{USERPROFILE:-\}/\.cursor/mcp\.json"\n\s*VSCODE_CONFIG="\$\{USERPROFILE:-\}/\.continue/[^"]+"',
        'CURSOR_CONFIG="${USERPROFILE:-}/.cursor/mcp.json"\n  WINDSURF_CONFIG="${USERPROFILE:-}/.windsurf/mcp.json"',
        content
    )
    content = re.sub(
        r'# Linux\n\s*CLAUDE_CONFIG="([^"]+)"\n\s*CURSOR_CONFIG="([^"]+)"\n\s*VSCODE_CONFIG="([^"]+)"',
        '# Linux\n  CLAUDE_CONFIG="\\1"\n  CURSOR_CONFIG="\\2"\n  WINDSURF_CONFIG="$HOME/.windsurf/mcp.json"',
        content
    )
    
    # 3. Add workspace check for VSCODE_CONFIG right after the if block
    vscode_logic = """
if [ -d "$PWD/.git" ]; then
  VSCODE_CONFIG="$PWD/.vscode/mcp.json"
else
  VSCODE_CONFIG=""
fi
"""
    content = re.sub(r'fi\n\n# Function to merge config using python', 'fi\n' + vscode_logic + '\n# Function to merge config using python', content)
    
    # 4. Add Windsurf logic in Configure IDEs
    content = re.sub(
        r'CURSOR_STATUS="✗ Cursor not detected"\nVSCODE_STATUS="✗ VS Code [^"]+"',
        'CURSOR_STATUS="✗ Cursor not detected"\nVSCODE_STATUS="✗ VS Code native MCP requires workspace"\nWINDSURF_STATUS="✗ Windsurf not detected"',
        content
    )
    
    # 5. Replace VS Code check logic
    old_vscode_check = re.search(r'# Check VS Code Continue parent dir or config existence.*?fi\n\n# 6\. Print', content, re.DOTALL).group(0)
    
    new_vscode_check = """# Check VS Code native MCP (workspace local)
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

# 6. Print"""
    
    content = content.replace(old_vscode_check, new_vscode_check)
    
    # 6. Add Windsurf to printing
    print_logic = """if echo "$VSCODE_STATUS" | grep -q "^✓"; then
  printf "%b\\n" "  ${GREEN}$VSCODE_STATUS${NC}"
else
  printf "%b\\n" "  $VSCODE_STATUS"
fi

if echo "$WINDSURF_STATUS" | grep -q "^✓"; then
  printf "%b\\n" "  ${GREEN}$WINDSURF_STATUS${NC}"
else
  printf "%b\\n" "  $WINDSURF_STATUS"
fi
echo ""
"""
    content = re.sub(r'if echo "\\$VSCODE_STATUS".*?echo ""\n', print_logic.replace('$', '\\$'), content, flags=re.DOTALL)
    
    # 7. Update Notify if no IDE configured
    content = content.replace('$CLAUDE_STATUS$CURSOR_STATUS$VSCODE_STATUS', '$CLAUDE_STATUS$CURSOR_STATUS$VSCODE_STATUS$WINDSURF_STATUS')
    
    # 8. Update intro comments
    content = content.replace('Claude Desktop, Cursor, and VS Code.', 'Claude Desktop, Cursor, VS Code, and Windsurf.')
    
    with open(filepath, 'w') as f:
        f.write(content)

patch_script("website/install.sh")
patch_script("scripts/install.sh")
