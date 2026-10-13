# AI usage record

## AI tools used

- OpenAI Codex (AI coding assistant) was used to help implement and document this assessment in the local repository.
- No other AI tools are recorded here.

## AI-assisted implementation

Codex assisted with the initial implementation of the FastAPI and SQLAlchemy backend, Pydantic validation, React dashboard and forms, automated tests, sample data, and documentation. The repository owner should update this record if additional tools are used or if the implementation changes materially.

## Human review checklist

Review each item yourself and mark it only after completing the review:

- [ ] Business rules and 30-minute scheduling behavior
- [ ] API request validation and response codes
- [ ] SQLite / SQLAlchemy create, update, and delete operations
- [ ] Conflict handling for edits, cancellations, and completed visits
- [ ] API and frontend error handling
- [ ] Form interactions, accessibility, and responsive layouts
- [ ] Test coverage and whether each test matches the intended behavior
- [ ] Explain the request flow and date/time convention in your own words

## Corrections made during implementation

- The first bare `pytest` invocation could not import the `app` package in this environment. Running tests as `python -m pytest` from `backend/` correctly sets the package import path. The working command is documented below.
- No other independently discovered application defects are claimed in this section. Add actual findings here as you review and change the project.

## Verification observed

- Backend: `cd backend && .venv/bin/python -m pytest -q` — 7 passed (observed during implementation).
- Frontend: `cd frontend && npm run build` — production build succeeded (observed during implementation).
- These are command results, not a claim that every manual checklist item has been completed.

## AI suggestions versus verified behavior

The implementation was AI-assisted and still needs the developer's review. Only the test and build commands listed above were executed and observed. The manual workflows in the README are instructions for future verification, not reported as completed. Do not treat generated code as correct solely because it builds or tests pass.
