# CLAUDE.md — Claude Code instructions

Claude Code is the **primary build and deployment agent** for Green Cast.

The full, agent-agnostic guide lives in **[AGENTS.md](./AGENTS.md)** — read it first.
Everything there (golden rules, commands, definition of done, file map) applies to
Claude Code. This file only adds Claude-specific notes.

## Claude Code's remit

- Multi-file features that span backend + frontend (e.g. adding an AI module: model + router + types + UI panel).
- The Vercel deployment: two projects from one repo, `uv.lock`, the `/be` proxy, env vars, and reading build/runtime logs to diagnose failures.
- Writing and maintaining the 112-test backend suite.
- Keeping README.md, AGENTS.md and CHANGELOG.md in sync with the code.

## Working agreement

1. Plan multi-step work as a task list; verify with `uv run pytest -q` and `npx tsc --noEmit` before declaring done.
2. When touching the AI layer, check **both** paths: no-key graceful degradation and the mocked-gateway success path.
3. After changing backend dependencies, regenerate `uv.lock` — Vercel installs from it, not `requirements.txt`.
4. Prefer the same-origin `/be` proxy over any direct backend URL or CORS change.
5. Never commit secrets. AI keys live only in Vercel project env vars and local `.env`.

## Quick reference

```bash
cd backend && uv run pytest -q            # backend tests
cd frontend && npx tsc --noEmit           # frontend type-check
```

Live app: https://green-cast-mvp-s613.vercel.app · Live API: https://green-cast-mvp.vercel.app
