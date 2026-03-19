# Trade Flow Visualizer

A full-stack web application for exploring and analyzing international trade flows between countries. Visualize bilateral trade relationships on an interactive map, detect trade shifts, and drill into country-level profiles with time-series charts and Sankey diagrams.

## Features

- **Interactive Map** — GPU-accelerated deck.gl arcs showing trade direction and magnitude on a MapLibre GL base map
- **Trade Shift Detection** — compare two years to find surges, collapses, new routes, and abandoned flows
- **Sankey Diagrams** — visualize top trade relationships with proportional link thickness
- **Country Profiles** — bilateral time-series charts, trade statistics, and regional breakdowns
- **Data Tables** — sortable, filterable views of bilateral trade records
- **Commodity & Year Filters** — slice data by commodity type, year, flow direction, and minimum value

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite 5, Tailwind CSS |
| Visualization | deck.gl, MapLibre GL, Plotly.js |
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 (asyncpg) |
| Infrastructure | Docker, Docker Compose, Nginx |

## Quick Start

### Docker Compose (recommended)

```bash
cp .env.example .env
# Edit .env with your COMTRADE_API_KEY

# Development (hot-reload)
docker compose -f docker-compose.dev.yml up

# Production
docker compose up
```

- Frontend: http://localhost:5173
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Local Development

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Requires PostgreSQL 16 running locally or via Docker.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (asyncpg) |
| `COMTRADE_API_KEY` | UN Comtrade API key for data ingestion |
| `CORS_ORIGINS` | Allowed origins (comma-separated) |

See `.env.example` for defaults.

## API

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/flows` | Trade flows with filters |
| `GET /api/v1/flows/top` | Top flows by value |
| `GET /api/v1/flows/sankey` | Sankey diagram data |
| `GET /api/v1/flows/timeseries` | Bilateral time series |
| `GET /api/v1/shifts` | Trade shift detection |
| `GET /api/v1/commodities` | Available commodities |
| `GET /api/v1/years` | Available years |
| `GET /health` | Health check |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── routes/        # API endpoints
│   │   ├── schemas/       # Pydantic models
│   │   └── services/      # Business logic & data ingestion
│   ├── alembic/           # Database migrations
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── pages/         # Explorer, CountryDetail, Shifts
│   │   ├── components/    # Map, charts, panels, controls
│   │   ├── hooks/         # useFlows, useSankey, useShifts, etc.
│   │   ├── layers/        # deck.gl arc & country layers
│   │   └── api/           # API client
├── data/                  # Scripts & static data assets
├── docker-compose.yml
└── docker-compose.dev.yml
```

## License

MIT
