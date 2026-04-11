# multibooker — Cross-Platform Betting Slip Converter

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=flat-square)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-6BA81E?style=flat-square)
![JWT](https://img.shields.io/badge/Auth-JWT%20Stateless-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)
![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=flat-square&logo=render&logoColor=white)
![Status](https://img.shields.io/badge/Status-In%20Development-orange?style=flat-square)

> A FastAPI-powered backend service that converts sports betting slip codes across platforms — paste a Stake.com slip code and get a valid code for Bet9ja, Sportybet, 1xBet, and others in seconds.

---

## The Problem

Across Nigeria and West Africa, millions of sports bettors use different platforms — Bet9ja, Sportybet, 1xBet, Stake.com, and others. Every day, tipsters share winning slip codes on Twitter, WhatsApp, and Telegram. The problem: a booking code is platform-specific. A Stake.com code is completely useless to a Bet9ja user.

The only workaround is to manually re-enter every fixture — slow, error-prone, and often impossible before kick-off. No tool existed to solve this.

**multibooker solves it.** It ingests a slip code from one platform, parses the fixtures and selections, maps them to the target platform's event database, and returns a valid booking code — automatically.

---

## Architecture Overview

```
┌─────────────────────────────────┐
│        multibooker-frontend     │  HTML/CSS/JS — user interface
│   (Jinja2 templates / static)   │
└──────────────┬──────────────────┘
               │ HTTP
┌──────────────▼──────────────────┐
│         FastAPI Application     │
│                                 │
│  ┌─────────┐  ┌──────────────┐  │
│  │ routes/ │  │  schemas/    │  │  Pydantic request/response models
│  └────┬────┘  └──────────────┘  │
│       │                         │
│  ┌────▼────────────────────┐    │
│  │       services/         │    │  Core business logic
│  │  ┌──────────────────┐   │    │
│  │  │ event_matcher    │   │    │  Cross-platform fixture matching
│  │  │ slip_converter   │   │    │  Slip ingestion & code generation
│  │  │ platform_client  │   │    │  Per-platform API integrations
│  │  └──────────────────┘   │    │
│  └─────────────────────────┘    │
│                                 │
│  ┌──────────┐  ┌─────────────┐  │
│  │ models/  │  │   utils/    │  │
│  └────┬─────┘  └─────────────┘  │
│       │                         │
│  ┌────▼─────┐  ┌─────────────┐  │
│  │database.py│ │  config.py  │  │
│  └────┬─────┘  └─────────────┘  │
└───────┼─────────────────────────┘
        │ SQLAlchemy ORM
┌───────▼──────────┐
│   PostgreSQL DB  │
└──────────────────┘
        │ Alembic migrations
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **API Framework** | FastAPI | High-performance async REST API |
| **Database** | PostgreSQL | Primary data store |
| **ORM** | SQLAlchemy | Database models and query layer |
| **Migrations** | Alembic | Version-controlled schema migrations |
| **Data Validation** | Pydantic (via FastAPI) | Request/response schema validation |
| **Authentication** | JWT (stateless) | Secure, stateless user auth |
| **Frontend** | HTML / CSS / JavaScript | User interface (served via static files) |
| **Deployment** | Render | Cloud deployment (configured, pending launch) |
| **Environment** | python-dotenv / `.env` | Configuration and secrets management |

---

## Key Features

### Slip Conversion Engine
- Accepts a booking code and source platform identifier
- Fetches full slip data via the source platform's API
- Parses fixture data: teams, kick-off times, market types, and selected outcomes
- Maps fixtures to the target platform's event database using the event matching engine
- Constructs a valid slip object conforming to the target platform's API schema
- Returns a usable booking code for the target platform

### Event Matching Engine (`services/`)
The core technical challenge of this project. Each platform assigns its own internal IDs to the same real-world fixture. The event matching service resolves this using:
- **Team name normalisation** — handles variations ("Man City" vs "Manchester City" vs "Manchester C.")
- **Kick-off time alignment** — confirms fixture identity using match start time within a tolerance window
- **Market type translation** — maps bet market names across platform naming conventions (e.g. "1X2" vs "Match Result" vs "Full Time Result")

### Authentication (`routes/` + JWT)
- Stateless JWT-based authentication
- Token issuance, validation, and refresh handling
- Protected routes requiring valid bearer tokens

### Database Layer (`models/` + `database.py` + Alembic)
- SQLAlchemy ORM models for users, slips, conversions, and platform data
- Alembic migration history tracking schema changes across environments
- PostgreSQL as the production database

### API Design (`routes/` + `schemas/`)
- RESTful endpoints with full Pydantic schema validation on request and response bodies
- Automatic OpenAPI documentation generated by FastAPI (available at `/docs`)
- Stateless design — no server-side session state

---

## Project Structure

```
multibooker/
├── app/
│   ├── models/             # SQLAlchemy ORM models
│   ├── routes/             # FastAPI route handlers (API endpoints)
│   ├── schemas/            # Pydantic request/response schemas
│   ├── scripts/            # Utility and data scripts
│   ├── services/           # Business logic (event matching, conversion)
│   ├── utils/              # Helper functions and shared utilities
│   ├── config.py           # Application configuration (env-based)
│   ├── database.py         # SQLAlchemy engine and session setup
│   └── main.py             # FastAPI app entry point
├── multibooker-frontend/   # Frontend HTML/CSS/JS application
├── static/                 # Static assets
├── alembic/                # Database migration files
├── .env                    # Environment variables (not committed)
├── .gitignore
└── .render-build.sh        # Render deployment build script
```

---

## Supported Platforms

| Platform | As Source | As Target |
|---|---|---|
| Stake.com | ✅ | — |
| Bet9ja | — | ✅ |
| Sportybet | — | 🔄 Planned |
| 1xBet | — | 🔄 Planned |
| Msport | — | 🔄 Planned |
| Betway | — | 🔄 Planned |

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/auth/register` | User registration | Public |
| `POST` | `/auth/login` | Login, returns JWT | Public |
| `POST` | `/convert` | Convert slip code | Required |
| `GET` | `/convert/{id}` | Get conversion result | Required |
| `GET` | `/platforms` | List supported platforms | Public |
| `GET` | `/docs` | Auto-generated OpenAPI docs | Public |

---

## Local Development Setup

```bash
# Clone the repository
git clone https://github.com/devolusegun/multibooker.git
cd multibooker

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your PostgreSQL credentials and JWT secret

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
Interactive API docs at `http://localhost:8000/docs`

---

## Engineering Challenges

**Cross-platform fixture identity**
No two platforms share fixture IDs. Resolving "Manchester City vs Arsenal" across Stake.com and Bet9ja requires normalising team names, validating against kick-off times, and handling edge cases where platform data lags or uses different naming conventions for the same club.

**Undocumented APIs**
Betting platform APIs are largely undocumented, rate-limited, and change without notice. The services layer is designed so each platform integration is isolated — a breaking change on one platform's API doesn't affect others.

**Stateless architecture**
JWT-based stateless authentication ensures the API can be horizontally scaled without shared session state — a deliberate architectural choice for future scalability on Render or similar platforms.

**Schema-first design**
Using Pydantic schemas for every API input and output means validation errors are caught at the boundary before reaching business logic, keeping the services layer clean and testable.

---

## Roadmap

- [x] FastAPI application structure
- [x] PostgreSQL + SQLAlchemy + Alembic setup
- [x] JWT stateless authentication
- [x] Pydantic schemas for all endpoints
- [x] Event matching engine (core logic)
- [x] Stake.com slip ingestion
- [x] Bet9ja conversion service
- [x] Frontend interface (multibooker-frontend)
- [ ] Sportybet conversion
- [ ] 1xBet conversion
- [ ] Rate limiting middleware
- [ ] Redis caching layer for frequent fixture lookups
- [ ] Full test suite (pytest)
- [ ] Render deployment launch

---

## Author

**Abioye Solomon Olusegun**
Full-Stack Developer · FastAPI · PHP · PostgreSQL · AWS
[github.com/devolusegun](https://github.com/devolusegun) · [linkedin.com/in/kidolu](https://linkedin.com/in/kidolu) · [Portfolio](https://devolusegun.github.io/portfolio/)
