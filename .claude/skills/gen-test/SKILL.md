---
name: gen-test
description: Generate a test stub for a given file following project conventions (pytest-asyncio/httpx for backend, Vitest/@vue/test-utils for frontend)
disable-model-invocation: true
---

Generate a test for: $ARGUMENTS

## Backend conventions (FastAPI / pytest)
- Use `pytest-asyncio` with `asyncio_mode = "auto"`
- Use `httpx.AsyncClient` with the FastAPI app via `httpx.ASGITransport`
- Share fixtures via `backend/tests/conftest.py`
- Place API tests in `backend/tests/api/`, store tests in `backend/tests/store/`, model tests in `backend/tests/models/`
- Import the app from `app.main`

## Frontend conventions (Vue 3 / Vitest)
- Use Vitest + `@vue/test-utils`
- Environment: jsdom (configured in vite.config.js)
- Mock Pinia stores with `createTestingPinia`
- Place component tests in `frontend/tests/unit/components/`
- Place store tests in `frontend/tests/unit/stores/`
- Use `vi.fn()` for mocks, `vi.spyOn()` for spies

## Output
- Generate a complete test file ready to run (no placeholders)
- Include at least: one happy-path test, one edge-case or error test
- Add a comment at the top indicating the file under test
- Follow the naming convention: `test_<module>.py` (backend) or `<Component>.test.js` (frontend)
