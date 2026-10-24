# Systemix — Architecture & Phase Plan

Systemix is a platform for learning system design: structured lessons, interview-style practice,
progress tracking (including LeetCode activity), and 1:1 mentorship from senior and staff engineers.

Lesson content is out of scope for now. Every phase uses placeholder content so the architecture
can be built and tested independently of what we eventually teach.

Design reference: the canvas at https://claude.ai/artifact/3gKNWdH4B4Zh5jsHZpBAUq (private).

---

## 1. Architecture

```
                 ┌──────────────────────────────┐
  Browser ─────▶ │  Next.js (apps/web)          │
                 │  App Router · TS · Tailwind  │
                 │  /api/* rewritten to FastAPI │
                 └──────────────┬───────────────┘
                                │ same origin (cookie session)
                 ┌──────────────▼───────────────┐      ┌───────────────────┐
                 │  FastAPI (apps/api)          │─────▶│  PostgreSQL       │
                 │  REST · Pydantic v2          │      │  source of truth  │
                 │  SQLAlchemy 2 (async)        │      └───────────────────┘
                 └──────┬───────────────┬───────┘
                        │               │ enqueue jobs  ┌───────────────────┐
                        │               └──────────────▶│  Redis            │
                        │                               │  cache · sessions │
                 ┌──────▼───────────────┐   consume     │  job queue        │
                 │  Worker (apps/api)   │◀──────────────┤                   │
                 │  arq: LeetCode sync, │               └───────────────────┘
                 │  emails, reminders   │
                 └──────────────────────┘
```

### Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | Next.js (App Router), TypeScript, Tailwind CSS | Matches the design; server components for public pages, client components for the app |
| Backend | FastAPI, Pydantic v2, SQLAlchemy 2 (async), Alembic | Typed request/response models, auto OpenAPI docs, async I/O for external calls |
| Database | PostgreSQL | Relational data (users, progress, bookings) with strong constraints |
| Cache / queue | Redis + arq | Session cache, rate limiting, background jobs in the same async style as the API |
| Auth | OAuth 2.0 (Google, GitHub) owned by the backend, httpOnly session cookie | No passwords to store; backend is the single place that knows who you are |
| Drawing canvas | Excalidraw (React component) | Practice workspace diagrams, saved as JSON |
| Tooling | `uv` + ruff + mypy + pytest (api); `pnpm` + ESLint + Prettier + Vitest + Playwright (web) | Fast installs, one linter per language |
| Local dev | Docker Compose for Postgres and Redis | One command to bring up dependencies |
| CI | GitHub Actions on every pull request | Lint, type-check, test; required to pass before merge |

### Repository layout

```
systemix/
├── apps/
│   ├── web/                 Next.js app
│   └── api/                 FastAPI app + arq worker
│       ├── app/
│       │   ├── core/        config, db session, security, errors
│       │   ├── modules/     one package per domain (see below)
│       │   └── main.py
│       ├── migrations/      Alembic
│       └── tests/
├── docs/                    this plan, ADRs, API notes
├── infra/                   docker-compose, deployment config
└── .github/workflows/       CI
```

Backend domain modules (each owns its models, schemas, service, and router):
`accounts` · `onboarding` · `learning` · `progress` · `practice` · `integrations` (LeetCode) ·
`mentorship` · `billing`

### Key decisions

1. **Auth lives in FastAPI, not Next.js.** The API runs the OAuth flow, creates the user, and
   issues an opaque session id in an httpOnly, Secure, SameSite=Lax cookie. Sessions are stored in
   Postgres and cached in Redis. Next.js only forwards the cookie.
2. **Same origin via rewrites.** Next.js rewrites `/api/*` to FastAPI, so the browser sees one
   origin: no CORS and no cross-site cookie problems.
3. **Account linking by verified email.** Google and GitHub sign-ins with the same verified email
   map to one user (`users` 1 → N `oauth_accounts`).
4. **Content is data, not code.** Tracks, modules, lessons and problems are rows in the database,
   loaded by a seed script from placeholder files, so real content can be swapped in later.
5. **Progress is event-sourced-lite.** Every meaningful action writes an `activity_events` row;
   streaks and heatmaps are computed from it (and cached), never stored as counters that drift.
6. **External calls never block requests.** LeetCode sync, emails and reminders run in the worker.
7. **Timezones are explicit.** Store UTC, keep each user's IANA timezone, compute "today" and
   streaks in the user's zone. Mentorship slots are stored in UTC.

---

## 2. Working agreement

- `main` is protected: no direct pushes, changes arrive only through a pull request with
  **at least one approval**, merged by Vaibhav.
- Each phase gets a branch from `main`: `phase/<n>-<name>` (e.g. `phase/1-home-screen`).
- Work inside a phase happens on feature branches cut from the phase branch:
  `feat/<n>-<topic>` (e.g. `feat/1-hero-section`). Each feature branch merges back into its phase
  branch through a pull request.
- When a phase meets its definition of done, a pull request `phase/<n>-… → main` is opened,
  reviewed, and merged by Vaibhav.
- A GitHub ruleset enforces this: direct pushes to `main` are rejected.

---

## 3. Phases

Each phase ends with something you can run and click through. Later phases only depend on earlier
ones.

### Phase 0 — Foundation · `phase/0-foundation`
**Goal:** an empty but production-shaped skeleton.
- Monorepo layout above; `apps/web` and `apps/api` both start with one command.
- Docker Compose for Postgres and Redis; `.env.example` files; settings via environment.
- FastAPI: app factory, config, async DB session, Alembic baseline, `/api/health` (checks DB and
  Redis), structured logging, error format.
- Next.js: base layout, Tailwind with the design tokens (colors, type, radius), font setup.
- CI: lint, type-check and tests for both apps on every pull request.
- Branch protection and this roadmap.

**Done when:** `docker compose up` + both dev servers run, `/api/health` is green through the
Next.js proxy, and CI passes on a pull request.

### Phase 1 — Home screen · `phase/1-home-screen`
**Goal:** the public landing page, plus the shared UI kit every later phase reuses.
- Components: button, card, badge/pill, progress bar, tag, page container, header, footer.
- Landing sections: nav, hero with Google/GitHub buttons (not wired yet), four tracks,
  how-it-works, problems preview, call to action, footer.
- Responsive down to phone width; light theme first, tokens ready for dark mode.

**Done when:** the landing page matches the design on desktop and mobile and scores well on a
Lighthouse accessibility check.

### Phase 2 — Authentication · `phase/2-auth`
**Goal:** sign in with Google or GitHub; one account per person.
- Tables: `users`, `oauth_accounts`, `sessions`.
- Endpoints: `GET /api/auth/{provider}/login`, `GET /api/auth/{provider}/callback`,
  `POST /api/auth/logout`, `GET /api/me`.
- OAuth `state` + PKCE, verified-email linking, session rotation on login, logout everywhere.
- Next.js: sign-in page, middleware that protects app routes, signed-in/out header states.

**Done when:** both providers work locally, linking the second provider reuses the same user, and
protected pages redirect to sign-in.

### Phase 3 — Onboarding & app shell · `phase/3-onboarding-shell`
**Goal:** first-run setup and the authenticated layout.
- Onboarding: level → target companies → weekly pace (no interview date). Skippable; resumable.
- Tables: `user_profiles`, `companies`, `user_target_companies`.
- App shell: sidebar, top bar, search placeholder, account menu.
- Settings: profile, linked accounts (connect/disconnect, keep at least one), level, companies,
  pace, theme, delete account (soft delete + scheduled purge).
- Dashboard with real empty states.

**Done when:** a new user lands in onboarding once, a returning user lands on the dashboard, and
all settings persist.

### Phase 4 — Learning core · `phase/4-learning`
**Goal:** browse and read lessons, using placeholder content.
- Tables: `tracks`, `modules`, `lessons`, `lesson_progress`, `bookmarks`, `notes`.
- Seed script that loads placeholder Markdown lessons.
- Learn catalog (tabs per track, status per lesson), lesson reader (table of contents, prev/next),
  mark complete, bookmark, private notes with autosave.

**Done when:** a user can finish a lesson and see it reflected in the catalog and on the dashboard.

### Phase 5 — Progress & streaks · `phase/5-progress`
**Goal:** honest progress numbers.
- Table: `activity_events` (append-only); streak and heatmap queries in the user's timezone,
  cached in Redis.
- Progress page: stat tiles, 26-week heatmap, per-track progress, bookmarks and notes tabs.
- Dashboard: continue-learning card, weekly goal vs pace, recent activity.

**Done when:** streaks are correct across midnight and timezone changes (covered by tests).

### Phase 6 — Practice · `phase/6-practice`
**Goal:** interview-style practice with saved work.
- Tables: `problems`, `practice_attempts` (per-step answers, canvas JSON, self-check state,
  status, timer).
- Problem list with filters; workspace with the five steps, autosave (debounced), Excalidraw
  canvas, hints, self-check, finish.

**Done when:** a draft survives a refresh and a device switch, and finished attempts count toward
progress.

### Phase 7 — LeetCode activity · `phase/7-leetcode`
**Goal:** show coding practice next to system design practice.
- Table: `leetcode_profiles` (username, last synced, cached stats JSON, sync status).
- Worker job fetches the public profile (unofficial GraphQL), with timeouts, retries and backoff,
  per-user and global rate limits, and a scheduled refresh.
- Progress card: solved by difficulty, submission heatmap, recently solved; clear
  "couldn't load" state.

**Done when:** adding a username shows data within one sync, and a LeetCode outage degrades
gracefully instead of breaking the page.

### Phase 8 — Mentorship · `phase/8-mentorship`
**Goal:** students choose one tutor from verified senior/staff engineers.
- Tables: `mentor_applications`, `mentor_profiles`, `mentor_availability`, `packages`
  (placeholder pricing), `mentorships` (one active per student), `bookings`, `session_notes`,
  `homework_items`, `reviews`.
- Apply-to-mentor flow + admin review; directory with filters; mentor profile.
- Package choice and slot booking with double-booking prevention (row locks or an exclusion
  constraint on time ranges); reschedule and cancel rules.
- Student "My mentor" page and mentor dashboard (requests, today, students).
- Explicit student consent before a mentor can see progress and practice drafts.

**Done when:** two students racing for the same slot cannot both get it (tested), and the full
flow works with payments stubbed.

### Phase 9 — Payments · `phase/9-payments`
**Goal:** charge for packages once the pricing model is decided.
- Provider to be decided (Razorpay or Stripe). Checkout, webhooks with signature checks,
  idempotency keys, refunds, mentor payouts ledger.

### Phase 10 — Launch hardening · `phase/10-launch`
**Goal:** safe to put in front of real users.
- Deployment (web, API, worker, managed Postgres and Redis), backups, migrations in CI/CD.
- Rate limiting, security headers, dependency audit, error tracking, metrics, uptime checks.
- Privacy: data export and account deletion.

---

## 4. Open decisions

| Decision | Needed by |
|---|---|
| Content source and authoring workflow | Phase 4 (placeholders until then) |
| Pricing model and payment provider | Phase 9 |
| Hosting provider | Phase 10 (local only until then) |
| Who approves pull requests into `main` (GitHub does not let an author approve their own PR) | Phase 0 |
