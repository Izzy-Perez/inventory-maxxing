# Inventory Maxxing - Project Context

## What This Project Is
An internal IT inventory and asset management system for Pinnacle Exhibits. It bridges IT device tracking with accounting's fixed asset register and automates provisioning workflows.

## Key Stakeholders
- **IT** — manages devices, provisions hardware, maintains scripts
- **Accounting** — owns the fixed asset register, tracks depreciation, needs disposal records
- **Managers / Finance** — approve new device requests

## Architecture
See `device-inventory-overview.md` for the full diagram. Summary:
- **AD-joined devices** (legacy 2K) — tracked in Domain Controller
- **Entra-joined devices** — tracked in Intune via Graph API
- **Autopilot devices** — being introduced, tracked in Intune
- **Postgres** — system of record for all assets (replaces ManageEngine)
- **Redis** — request queue and cache layer
- **1 User : 1 Device** assignment model
- Asset tags are the linking key across systems

## Web App Portals (role-based views)
- **Manager Portal** — self-service device requests, order history
- **IT Portal** — verification queue, asset management, sync oversight
- **VP / Accounting Portal** — reports, pricing, depreciation, inventory dashboards

## Request Flow
1. Manager/report-to submits device request via web portal
2. Approval chain (Manager -> Finance)
3. IT receives approved request, provisions device, verifies details
4. IT confirms asset into Postgres (serial, tag, cost, etc.)
5. Asset appears in reporting dashboards for VP/Accounting

## Planned Modules
- `scripts/ad/` — PowerShell scripts querying Active Directory, scheduled sync to Postgres
- `scripts/intune/` — PowerShell/Graph API scripts for Entra/Autopilot devices, scheduled sync to Postgres

## Accounting Fixed Asset Requirements
See `fixed-asset-tracking.md` for the full field list. Key points:
- Accounting needs IT to reconcile physical inventory against their fixed asset list
- Disposals need approximate dates and should be tracked
- Industry standard: IRS MACRS 5-year depreciation for computer hardware
- Must track: asset tag, serial, make/model, purchase date/cost, location, assigned user, status, disposal info

## Open Items
- Autopilot naming convention — not yet defined
- Autopilot asset tagging convention — not yet created
- Accounting reconciliation workflow — in progress (waiting on their list by location)

## Tech Stack
- **Database**: Redrock Postgres (enhanced PostgreSQL) — via asyncpg + SQLAlchemy async
- **Cache/Queue**: Redis
- **Backend**: Python + FastAPI
- **Frontend**: HTMX + Jinja2 templates (no Node.js, no build step)
- **CSS**: Pico CSS (classless/minimal CSS framework)
- **ORM**: SQLAlchemy 2.0 with async sessions
- **Migrations**: Alembic

## Project Structure
```
app/
  main.py           # FastAPI app entry point, lifespan
  config.py         # pydantic-settings, loads .env
  database.py       # async SQLAlchemy engine + session
  cache.py          # Redis connection pool
  models.py         # SQLAlchemy models (Asset, Location)
  templating.py     # Jinja2 templates setup
  routes/
    dashboard.py    # Dashboard with stats
    assets.py       # Full CRUD for assets
  templates/
    base.html       # Layout with nav, HTMX + Pico CSS
    dashboard.html
    assets/
      list.html     # Searchable/filterable asset list
      detail.html   # Asset detail view
      form.html     # Create/edit form
      _table.html   # HTMX partial for live search
      _saved.html   # Post-save confirmation
  static/           # Static files (auto-created)
docker-compose.yml  # Postgres + Redis containers
requirements.txt    # Python dependencies
.env.example        # Environment variable template
```

## Running the App
```bash
docker compose up -d           # Start Postgres + Redis
pip install -r requirements.txt
uvicorn app.main:app --reload  # Start dev server at http://localhost:8000
```

## Conventions
- Scripts will primarily be PowerShell (Windows/AD/Intune environment)
- Use Microsoft Graph API for Intune/Entra queries
- Web app uses async throughout (asyncpg, redis.asyncio)
- HTMX for interactivity — no client-side JS frameworks
- Forms submit via HTMX with server-side validation
