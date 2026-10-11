# Incident Reporting API

A small FastAPI service for reporting and retrieving civic incidents (power
outages, water leaks, theft, etc.). It stores incidents in memory, geocodes the
reported location with Nominatim, and exposes read/create endpoints.

> **Status:** mock/in-memory backend. There is no database yet — data lives in
> module-level Python lists and resets whenever the server restarts.

## Tech stack

- **Python 3.13**
- **FastAPI** (`fastapi[standard]`)
- **Uvicorn** (ASGI server)
- **geopy / Nominatim** for geocoding
- **uv** for dependency management and packaging

## Project structure

```
incident-api/
├── pyproject.toml            # project metadata + dependencies
├── uv.lock                   # locked dependency versions
├── README.md
└── src/
    └── incident_api/
        ├── __init__.py       # `main()` entrypoint (runs uvicorn)
        ├── main.py           # FastAPI app + routes
        ├── data.py           # in-memory mock stores
        └── utils.py          # geocoding + category/tag helpers
```

## Getting started

Prerequisites: [uv](https://docs.astral.sh/uv/) installed.

Install dependencies:

```bash
uv sync
```

Run the development server (with auto-reload):

```bash
uv run incident-api
```

Or via FastAPI's dev runner:

```bash
uv run fastapi dev src/incident_api/main.py
```

The app serves under the root path **`/api/v1`** at `http://127.0.0.1:8000`.
Interactive docs: `http://127.0.0.1:8000/api/v1/docs`.

## Data models

| Model | Key fields |
| --- | --- |
| `incidents` | `id`, `title`, `sanitized_text`, `category_id` (FK), `location_id` (FK), `occurred_at`, `created_at`, `status`, `duplicate_of_id` (nullable FK) |
| `locations` | `id`, `incident_id` (FK), `display_name`, `normalized_name`, `latitude`, `longitude`, `geocode_status` |
| `categories` | `id`, `incident_id` (FK), `categories` — list of `{name, slug}` |
| `incident_tags` | `id`, `incident_id` (FK), `tags` — list of `{name, tag}` |
| `submission_metadata` | `id`, `incident_id` (FK), `source`, `received_at`, `request_id` |

All related rows carry an `incident_id` foreign key back to `incidents.id`.

## API endpoints

Base path: `/api/v1`

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Health/welcome message |
| GET | `/incidents` | List all incidents |
| GET | `/incidents/{incident_id}` | Get one incident with its related records (returns `404` if not found) |
| GET | `/categories` | List categories |
| GET | `/locations` | List locations |
| GET | `/incident-tags` | List incident tags |
| GET | `/submission-data` | List submission metadata |
| POST | `/incidents/create` | Create an incident (plus its location, categories, tags, and submission metadata) |

### `GET /incidents/{incident_id}`

Returns the incident together with the related records joined on `incident_id`:

```json
{
  "incident": { "id": 1, "title": "Power Outage in Sector V", "...": "..." },
  "location": { "id": 12, "incident_id": 1, "display_name": "Sector V, Salt Lake, Kolkata", "...": "..." },
  "categories": { "id": 3, "incident_id": 1, "categories": [{ "name": "Utility / Infrastructure", "slug": "utility-infrastructure" }] },
  "incident_tags": { "id": 34, "incident_id": 1, "tags": [{ "name": "Power Outage", "tag": "power-outage" }] },
  "metadata": { "id": 101, "incident_id": 1, "source": "mobile_app", "...": "..." }
}
```

### `POST /incidents/create`

Request body (JSON object). `tags` and `categories` are comma-separated strings.

```json
{
  "location": "Behala, Kolkata",
  "tags": "Theft,Fraud,Assault",
  "categories": "Crime,Robbery",
  "title": "Theft in Broad Daylight",
  "text": "On October 11, 2026, a bold daytime robbery occurred ...",
  "occurred_at": "October 11, 2026"
}
```

Behavior:

- A random id (`100`–`1000`) is generated for the incident and each related record.
- `location` is geocoded via Nominatim; `latitude`/`longitude` are set from the
  result and `geocode_status` is `"success"` or `"failed"` (on a failed or empty
  lookup the coordinates are `null`).
- `categories` and `tags` are split on `,` and expanded into `{name, slug}` /
  `{name, tag}` rows.
- `status` defaults to `"pending"` and `duplicate_of_id` to `null`.

Response:

```json
{
  "incident": { "...": "..." },
  "location": { "...": "..." },
  "categories": { "...": "..." },
  "incident_tags": { "...": "..." },
  "metadata": { "...": "..." }
}
```

## Notes & limitations

- **In-memory storage.** The mock stores are module-level lists; new records are
  appended and persist only for the lifetime of the process. Restarting the
  server (or `--reload`) resets the data, and multiple workers each keep their
  own copy. There is no SQL/database layer.
- `created_at` / `received_at` use naive `datetime.now()` timestamps.
- Geocoding makes a live network call to Nominatim per create request; failures
  are swallowed and recorded as `geocode_status: "failed"`.
