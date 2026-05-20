# IPL Fantasy Cricket

A web app for running a private fantasy cricket league for IPL 2026. Friends pick an XI from each match's player pool, predict the toss winner and Man of the Match, and compete on a leaderboard.

## Features

- **Authentication** — email-based registration with verification, JWT auth, admin role
- **Match-by-match team building** — pick 11 players from the two playing teams within a 100-credit budget
- **Bonus predictions** — toss winner (+10) and Man of the Match (+25)
- **Lockout** — team selection closes 1 hour before match start
- **Leaderboards** — overall and per-match rankings
- **Admin panel** — manage players, matches, and submit performance points
- **Email reminders** — users get notified 2 hrs and 90 mins before a match if they haven't built their team
- **Account settings** — opt-out of email notifications

## Tech Stack

### Backend (`server/`)

- **FastAPI** — Python async web framework
- **SQLAlchemy 2.x async** — ORM with asyncpg driver
- **PostgreSQL** — database (Neon serverless in production)
- **Alembic** — database migrations
- **Pydantic v2** — request/response schemas and settings
- **python-jose + passlib** — JWT auth and password hashing
- **httpx** — HTTP client for Mailjet (email) and CricAPI (scorecards)
- **pytest + hypothesis** — testing with property-based tests

### Frontend (`client/`)

- **React 18** with TypeScript
- **Vite** — build tool and dev server
- **React Router v6** — client-side routing
- **Tailwind CSS** — styling
- **Axios** — API client

### Hosting & Infrastructure

- **Render** — backend API (Python/FastAPI)
- **Vercel** — frontend (Vite static build)
- **Neon** — managed Postgres
- **Mailjet** — transactional email (verification + reminders)
- **CricAPI** — match scorecards (used for points calculation)
- **cron-job.org** — external scheduler for keep-alive ping and notification triggers

## Project Structure

```
.
├── client/                  React + Vite frontend
│   ├── src/
│   │   ├── api/             Axios client with auth interceptor
│   │   ├── components/      Shared UI (Navbar, Modals, ProtectedRoute)
│   │   ├── context/         AuthContext
│   │   ├── pages/           Route pages (Login, Dashboard, TeamBuilder, etc.)
│   │   │   └── admin/       Admin-only pages
│   │   └── types/           Shared TypeScript types matching backend schemas
│   └── vercel.json          Vercel config (SPA fallback)
│
├── server/                  FastAPI backend
│   ├── app/
│   │   ├── core/            config, database, security, deps
│   │   ├── models/          SQLAlchemy ORM models
│   │   ├── schemas/         Pydantic request/response schemas
│   │   ├── routes/          FastAPI routers (auth, matches, admin, cron, etc.)
│   │   └── services/        Business logic (auth, points, email, etc.)
│   ├── alembic/             DB migrations
│   ├── tests/               pytest tests (unit, integration, property)
│   ├── seed.py              Seed players and matches
│   └── main.py              FastAPI app entrypoint
│
└── README.md
```

## Local Development

### Prerequisites

- Python 3.11+
- Node 18+
- Postgres (local or remote)

### Backend

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create .env file with at minimum:
# APP_DATABASE_URL=postgresql+asyncpg://user@localhost:5432/ipl_fantasy

# Run migrations
alembic upgrade head

# Optional: seed players and matches
python -m server.seed

# Start dev server
uvicorn server.main:app --reload --port 8000
```

### Frontend

```bash
cd client
npm install

# Set API URL in .env or use the default (http://localhost:8000/api)
# VITE_API_URL=http://localhost:8000/api

npm run dev
```

Frontend runs on `http://localhost:5173`, backend on `http://localhost:8000`.

## Environment Variables

### Backend (`server/.env`)

| Variable | Description |
|---|---|
| `APP_DATABASE_URL` | Postgres URL (asyncpg) |
| `APP_JWT_SECRET` | JWT signing secret |
| `APP_JWT_ALGORITHM` | Default `HS256` |
| `APP_JWT_EXPIRATION_MINUTES` | Default 60 |
| `APP_CORS_ORIGINS` | Comma-separated CORS origins |
| `APP_MAILJET_API_KEY` | Mailjet API key |
| `APP_MAILJET_SECRET_KEY` | Mailjet secret key |
| `APP_MAILJET_SENDER_EMAIL` | Default sender email |
| `APP_FEEDBACK_RECIPIENT_EMAIL` | Where feedback emails go |
| `APP_FRONTEND_URL` | Used in email links |
| `APP_CRON_SECRET` | Shared secret for cron-job.org → API |

### Frontend (`client/.env`)

| Variable | Description |
|---|---|
| `VITE_API_URL` | Backend base URL (e.g., `https://api.example.com/api`) |

## Deployment

### Frontend (Vercel)

1. Connect the repo to Vercel
2. Set root directory to `client/`
3. Vercel auto-detects Vite — no extra config needed
4. Add `VITE_API_URL` in Vercel env vars pointing to your Render backend
5. `client/vercel.json` already handles SPA fallback routing

### Backend (Render)

1. Create a new Web Service on Render
2. Root directory: `server/`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn server.main:app --host 0.0.0.0 --port $PORT`
5. Add all `APP_*` env vars (see table above)
6. Connect Neon Postgres and set `APP_DATABASE_URL`

### Database (Neon)

- Sign up at [neon.tech](https://neon.tech) and create a project
- Copy the connection string and prefix the driver: `postgresql+asyncpg://`
- Run migrations from your local machine with that URL set:
  ```bash
  cd server
  APP_DATABASE_URL="postgresql+asyncpg://..." alembic upgrade head
  ```

### Cron Jobs (cron-job.org)

Two cron jobs needed:

**1. Keep Render warm (free tier sleeps after 15 min idle)**
- URL: `https://your-render-backend.onrender.com/health`
- Method: GET
- Schedule: Every 10-14 minutes

**2. Send match reminders**
- URL: `https://your-render-backend.onrender.com/api/cron/send-match-reminders`
- Method: POST
- Schedule: Every 15 minutes
- Custom header: `X-Cron-Secret: <APP_CRON_SECRET value>`

The reminder cron checks every 15 min for matches starting in ~120 min or ~90 min and emails users without a team.

## Admin Operations

### Promoting a user to admin

```sql
UPDATE users SET role = 'ADMIN' WHERE email = 'admin@example.com';
```

### Adding a new player mid-season

```sql
INSERT INTO players (id, name, role, franchise, cost, created_at, updated_at)
VALUES (gen_random_uuid(), 'Player Name', 'BOWLER', 'Mumbai Indians', 7.0, now(), now());
```

Player roles: `BATSMAN`, `BOWLER`, `ALL_ROUNDER`, `WICKET_KEEPER`.

### Setting a player image

```sql
UPDATE players SET image_url = 'https://...' WHERE name = 'Player Name';
```

### Submitting points for a match

Use the admin Points Entry page at `/admin/points/<match_id>`. Paste a JSON of player stats (runs, balls, fours, sixes, wickets, overs, runsConceded, maidens, catches, stumpings, runOuts, didBat) and the page calculates points based on the scoring rules.

## Scoring Rules

**Batting**
- 1 pt per run
- +1 per four, +2 per six (bonus on top of runs)
- +10 for 50+, +20 for 100+ (mutually exclusive)
- -3 duck (0 runs, faced a ball, didBat=true, role ≠ BOWLER)

**Bowling**
- +25 per wicket
- +10 for 3-4 wickets, +20 for 5+ wickets (mutually exclusive)
- +8 per maiden
- Economy <6 over 2+ overs: +10
- Economy >12 over 2+ overs: -10

**Fielding**
- +10 per catch / stumping / run out

**Bonus predictions (added to team score)**
- Correct toss winner: +10
- Correct MOTM: +25

## Spec

The full feature spec, design docs, and task breakdown live under `.kiro/specs/` and were used by Kiro during initial development.

## License

Private project. No license granted.
