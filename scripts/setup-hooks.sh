#!/bin/bash
#
# Sets up the git hooks for this repository.
#

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "Setting up git hooks..."

# Ensure the pre-commit script is executable
chmod +x "$REPO_ROOT/scripts/pre-commit"

# Create symlink
ln -sf "$REPO_ROOT/scripts/pre-commit" "$HOOKS_DIR/pre-commit"

echo "Successfully installed pre-commit hook!"
