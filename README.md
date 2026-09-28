# Campus Customs — MGT 409 Homework 4

Campus Customs is a Yale merchandise storefront built with React, Vite, and TypeScript, backed by
a FastAPI service and a PydanticAI shopping assistant that answers from a real SQLite catalogue.

## What a grader needs before starting

This repository contains **source code only**. Two things are deliberately not committed and must
be supplied locally:

1. **The data pack** — `data/campus_customs.db` and the product photography in `public/products/`.
   Copy the provided data pack into the repository so the tree looks like this:

   ```
   hw4/
     data/campus_customs.db
     public/products/*.jpg
   ```

2. **A `.env` file** — copy the template and add your own key:

   ```sh
   cp .env.example .env
   ```

   Then set `PORTKEY_API_KEY` in `.env`. Without it the storefront still runs, but
   `POST /api/chat` returns HTTP 503 naming the missing variable. `OPENAI_MODEL` defaults to
   `gpt-5.6-luna`.

## Run it

Two terminals, both from the repository root.

**Terminal 1 — FastAPI backend**

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Vite/React frontend**

```sh
npm install
npm run dev
```

| Service | URL |
| --- | --- |
| Storefront | http://localhost:5173 |
| API health check | http://127.0.0.1:8000/api/health |
| Interactive API docs | http://127.0.0.1:8000/docs |

A seeded account is available for testing sign-in and saved chat history:
`test@campuscustoms.yale.edu` / `password`.

## What the app does

- **Storefront** — Home, Products, About, Log in, Create account, and a detail page per product,
  all rendered from the catalogue in `campus_customs.db`.
- **Catalogue filtering** — search plus garment type, size, colour, availability, and sort. Filters
  are stored in the URL, so a filtered view survives a reload and can be shared.
- **Accounts** — registration and login against the `users` table. Passwords are stored as
  PBKDF2-HMAC-SHA256 hashes with a random salt at 600,000 iterations; sessions are random tokens
  kept only as SHA-256 hashes in `auth_sessions` behind an HttpOnly cookie.
- **AI shopping assistant** — a PydanticAI agent with three read-only database tools. It answers
  price, description, colour, and per-size stock questions from the database, returns structured
  product cards that render live in the page, remembers a signed-in shopper's conversation, knows
  which product page is open so "this" resolves correctly, and asks a clarifying question instead
  of guessing when a request is too vague.

## Project layout

```
hw4/
  AI_prompts.md              prompt log for Problems 1-13
  requirements.txt           Python dependencies (includes backend/requirements.txt)
  .env.example               environment template, placeholders only
  .gitignore
  README.md
  index.html                 Vite entry point
  package.json
  src/                       React + TypeScript frontend
  backend/
    main.py                  FastAPI app: catalogue, auth, chat, chat history
    agent.py                 PydanticAI agent setup and model configuration
    tools.py                 database-backed catalogue and inventory tools
    models.py                Pydantic request, response, and tool-result models
    audit.py                 append-only audit trail writer
    prompts/prompt.md        system prompt and agent safety rules
    requirements.txt
  output/
    harness.md               technical documentation: models, tools, safety, system specs
    design.md                design pass notes
    usability.md             usability improvements
    app_check.html           visual app-check report (open directly in a browser)
    app_check_images/        screenshots for the report
    audit_trail.json         append-only record of agent runs
  data/                      not committed — supplied by the data pack
  public/products/           not committed — supplied by the data pack
```

## Configuration

All variables are documented in `.env.example`. `PORTKEY_API_KEY` is the only required one;
the rest cover the model id, database path, CORS origins, the agent timeout and rate limit, the
audit-trail path, and the frontend's API base URL.

## Notes

`output/app_check.html` can be opened directly from disk — it uses relative image paths and does
not need either server running. Checkout is not connected; the assistant is read-only and cannot
place orders or change stock.
