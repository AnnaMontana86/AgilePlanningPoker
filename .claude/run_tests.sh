#!/bin/bash
# Stop hook: run all unit tests after code changes.
# Exit code 2 feeds output back to Claude so it can fix failures.

PROJECT_DIR="/home/anna/codingProjects/AgilePlanningPoker"

# Only run if source files were changed in this session
if ! git -C "$PROJECT_DIR" diff --quiet HEAD 2>/dev/null || \
   ! git -C "$PROJECT_DIR" diff --cached --quiet 2>/dev/null; then
  :
else
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

# Frontend tests
FRONTEND=$(cd "$PROJECT_DIR/frontend" && source "$HOME/.nvm/nvm.sh" && npm test 2>&1)
if [ $? -ne 0 ]; then
  FAILED=1
  OUTPUT+=$'\n=== FRONTEND TEST FAILURES ===\n'"$FRONTEND"
fi

if [ $FAILED -ne 0 ]; then
  echo "Unit tests failed. Please fix the failures before finishing."
  echo "$OUTPUT"
  exit 2
fi

exit 0
