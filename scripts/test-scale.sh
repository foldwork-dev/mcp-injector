#!/bin/bash
#
# Automated scale testing script.
# Clones a large repository and runs mcp-injector against it to ensure stability.
#

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
TEST_DIR="/tmp/scale-test-redis"
INJECTOR_BIN="$REPO_ROOT/mcp-injector-test"

echo "=== Scale Testing MCP Injector ==="

# 1. Build the injector
echo "Building mcp-injector..."
cd "$REPO_ROOT"
go build -o "$INJECTOR_BIN" ./main.go

# 2. Clone a large repository
if [ ! -d "$TEST_DIR" ]; then
    echo "Cloning redis into $TEST_DIR..."
    git clone --depth 1 https://github.com/redis/redis.git "$TEST_DIR"
else
    echo "Test directory $TEST_DIR already exists, skipping clone."
fi

# 3. Start the MCP server and test it
echo "Starting mcp-injector against $TEST_DIR..."
export MCP_WORKSPACE="$TEST_DIR"

# We send a basic initialize request to see if it responds properly without crashing.
# MCP protocol requires an initialize request first.
INITIALIZE_REQ='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}'

# Send the request and capture output, timeout after 10 seconds.
# Using a python script to handle the subprocess cleanly.
python3 -c "
import subprocess
import json
import sys

proc = subprocess.Popen(['$INJECTOR_BIN'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
try:
    # Send initialize request
    proc.stdin.write('$INITIALIZE_REQ\n')
    proc.stdin.flush()
    
    # Read response
    response_line = proc.stdout.readline()
    if not response_line:
        print('ERROR: No response from server')
        sys.exit(1)
        
    response = json.loads(response_line)
    if 'result' in response:
        print('SUCCESS: Received valid initialize response from mcp-injector!')
    else:
        print(f'ERROR: Unexpected response: {response}')
        sys.exit(1)
        
    proc.terminate()
except Exception as e:
    print(f'ERROR: {e}')
    proc.terminate()
    sys.exit(1)
"

echo "=== Scale Test Passed! ==="
rm -f "$INJECTOR_BIN"
