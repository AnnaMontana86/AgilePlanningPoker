#!/bin/bash
# PostToolUse hook: run unit tests only when production code is edited.
# Exit code 2 feeds output back to Claude so it can fix failures.

PROJECT_DIR="/home/anna/codingProjects/AgilePlanningPoker"

# PostToolUse passes tool input as JSON on stdin
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only run tests if a production source file was edited (not tests/specs/config)
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

is_prod_file() {
    echo "$FILE_PATH" | grep -E '(backend/app/|frontend/src/)' | grep -qvE '(test|spec)'
}

if ! is_prod_file; then
    exit 0
fi

FAILED=0
OUTPUT=""

# Backend tests
BACKEND=$(cd "$PROJECT_DIR/backend" && python3.12 -m pytest --tb=short -q 2>&1)
if [ $? -ne 0 ]; then
    FAILED=1
    OUTPUT+=$'\n=== BACKEND TEST FAILURES ===\n'"$BACKEND"
fi

# Frontend unit tests
FRONTEND=$(cd "$PROJECT_DIR/frontend" && source "$HOME/.nvm/nvm.sh" && npm test 2>&1)
if [ $? -ne 0 ]; then
    FAILED=1
    OUTPUT+=$'\n=== FRONTEND TEST FAILURES ===\n'"$FRONTEND"
fi

if [ $FAILED -ne 0 ]; then
    echo "Unit tests failed after editing $FILE_PATH — please fix before continuing."
    echo "$OUTPUT"
    exit 2
fi

exit 0
